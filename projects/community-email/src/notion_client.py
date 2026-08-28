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

    def create_page(self,parent,title,children):
        return self.transport("POST","/pages",{
            "parent":{"type":"page_id","page_id":identifier(parent)},
            "properties":{"title":{"type":"title","title":rich(title)}},
            "children":children,
        })

    def create_export(self,parent,result,build):
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        code=block("code",result["mjml"])
        code["code"]["language"]="plain text"
        code["code"]["caption"]=rich("Complete MJML — use Copy code, then paste into SCLA.")
        return self.create_page(parent,"MJML export — "+stamp,[
            block("paragraph","Subject: "+result["subject"]),
            block("paragraph","Generated "+stamp+". Build: "+build+". Review and send a test in SCLA before sending to members."),
            code,
        ])

    def create_failure(self,parent):
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return self.create_page(parent,"Generation failed — "+stamp,[
            block("paragraph","Generation could not be confirmed. Check for a recent export before retrying. Review Subject and Preview, empty headings, unsupported blocks, image captions and lasting image URLs. Stop editing while generating. If it still fails, ask the connection owner to check access. Earlier exports are unchanged.")
        ])
