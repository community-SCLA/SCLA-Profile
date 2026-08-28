"""Small Notion API client. Never logs credentials, payloads, or response bodies."""
import datetime
import json
import random
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener

class RemoteError(RuntimeError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None

def identifier(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError,TypeError,AttributeError):
        raise ValueError("Configure a valid Notion page or block identifier.") from None

def rich(value):
    if len(value.encode("utf-8")) > 100000:
        raise ValueError("Shorten the email before exporting.")
    return [{"type":"text","text":{"content":value[i:i+2000]}} for i in range(0,len(value),2000)]

def block(kind,value):
    return {"object":"block","type":kind,kind:{"rich_text":rich(value)}}

class Notion:
    def __init__(self,token,transport=None):
        if not token:
            raise ValueError("The Notion connection is not configured.")
        self.token=token
        self.transport=transport or self.request

    def request(self,method,path,data=None):
        payload=json.dumps(data,ensure_ascii=False).encode() if data is not None else None
        if payload and len(payload)>450000:
            raise ValueError("Shorten the email before exporting.")
        req=Request("https://api.notion.com/v1"+path,data=payload,method=method,headers={
            "Authorization":"Bearer "+self.token, "Notion-Version":"2026-03-11",
            "Content-Type":"application/json",
        })
        for attempt in range(4):
            try:
                with build_opener(NoRedirect).open(req,timeout=30) as response:
                    raw=response.read(4000001)
                    if len(raw)>4000000:
                        raise RemoteError("Notion response exceeded the safe size limit.")
                    return json.loads(raw)
            except HTTPError as exc:
                retry=exc.code in (429,529) or (method=="GET" and exc.code in (500,502,503,504))
                if not retry or attempt==3:
                    raise RemoteError("Notion request failed; check connection permissions or retry later.") from None
                try:
                    delay=max(0,float(exc.headers.get("Retry-After",2**attempt)))
                except ValueError:
                    delay=2**attempt
                if delay>60:
                    raise RemoteError("Notion requested a longer pause; retry later.") from None
                time.sleep(delay+random.uniform(0,0.25))
            except (URLError,TimeoutError,json.JSONDecodeError):
                raise RemoteError("Notion response could not be confirmed; inspect results before retrying.") from None

    def children(self,page):
        page=identifier(page)
        result,cursor,seen=[],None,set()
        for _ in range(6):
            query={"page_size":100}
            if cursor:
                query["start_cursor"]=cursor
            response=self.transport("GET","/blocks/"+page+"/children?"+urlencode(query))
            result.extend(response["results"])
            if len(result)>500:
                raise ValueError("Keep the email under 500 blocks.")
            if not response.get("has_more"):
                return result
            cursor=response.get("next_cursor")
            if not cursor or cursor in seen:
                raise RemoteError("Notion pagination did not complete.")
            seen.add(cursor)
        raise RemoteError("Notion pagination exceeded the safe limit.")


    def requests(self,data_source):
        data_source=identifier(data_source)
        result,cursor,seen=[],None,set()
        for _ in range(6):
            body={"page_size":5,"sorts":[{"timestamp":"created_time","direction":"ascending"}],
                  "filter":{"or":[{"property":"Status","select":{"equals":"Queued"}},
                                  {"property":"Status","select":{"equals":"Processing"}}]}}
            if cursor: body["start_cursor"]=cursor
            response=self.transport("POST","/data_sources/"+data_source+"/query",body)
            result.extend(response["results"])
            if len(result)>=5 or not response.get("has_more"):
                return result[:5]
            cursor=response.get("next_cursor")
            if not cursor or cursor in seen:
                raise RemoteError("Request pagination did not complete.")
            seen.add(cursor)
        raise RemoteError("Request pagination exceeded its safe limit.")

    def set_request(self,request,status,note):
        if status not in ("Queued","Processing","Ready","Error"):
            raise ValueError("Unknown request status.")
        return self.transport("PATCH","/pages/"+identifier(request),{"properties":{
            "Status":{"select":{"name":status}},
            "Note":{"rich_text":rich(note)},
        }})

    def output_container(self,page,create=False):
        blocks=self.children(page)
        matches=[b for b in blocks if b.get("type")=="toggle"
                 and plain(b.get("toggle",{}).get("rich_text",[]))==OUTPUT_TITLE]
        if len(matches)>1:
            raise ValueError("Keep only one Generated MJML section.")
        if matches:
            return identifier(matches[0]["id"])
        if not create:
            return None
        container=block("toggle",OUTPUT_TITLE)
        response=self.transport("PATCH","/blocks/"+identifier(page)+"/children",{"children":[container]})
        return identifier(response["results"][0]["id"])

    def completed_output(self,page,request):
        container=self.output_container(page)
        if not container:
            return None
        prefix="SCLA generated | request "+identifier(request)+" |"
        for b in self.children(container):
            if b.get("type")=="code" and plain(b.get("code",{}).get("caption",[])).startswith(prefix):
                value=plain(b["code"].get("rich_text",[]))
                if value.startswith("<mjml>") and value.rstrip().endswith("</mjml>"):
                    return identifier(b["id"])
        return None

    def save_output(self,page,result,request,build):
        container=self.output_container(page,create=True)
        old=self.children(container)
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        code=block("code",result["mjml"])
        code["code"]["language"]="plain text"
        code["code"]["caption"]=rich("SCLA generated | request "+identifier(request)+" | "+stamp+
                                    " | build "+build+" | Copy complete code, then preview in SCLA.")
        response=self.transport("PATCH","/blocks/"+container+"/children",{"children":[code]})
        new_id=identifier(response["results"][0]["id"])
        saved=[b for b in self.children(container) if b.get("id")==new_id]
        if (len(saved)!=1 or saved[0].get("type")!="code"
                or plain(saved[0]["code"].get("rich_text",[]))!=result["mjml"]
                or plain(saved[0]["code"].get("caption",[]))!=plain(code["code"]["caption"])):
            raise RemoteError("Saved output could not be verified; earlier code is unchanged.")
        # Append and verify before retiring only this generator's earlier code.
        # Never delete a teammate's notes or another kind of block.
        for b in old:
            if (b.get("type")=="code"
                    and plain(b.get("code",{}).get("caption",[])).startswith("SCLA generated | request ")):
                self.transport("DELETE","/blocks/"+identifier(b["id"]))
        return new_id

OUTPUT_TITLE="Generated MJML — copy into SCLA"

def plain(items):
    return "".join(t.get("text",{}).get("content",t.get("plain_text","")) for t in items)
