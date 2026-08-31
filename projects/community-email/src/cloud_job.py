"""GitHub-hosted queue worker. Draft content never leaves memory and Notion."""
import os
from pathlib import Path
import subprocess
import sys
from convert import from_notion, render
from notion_client import Notion, identifier, plain

def validate_mjml(markup):
    env={k:v for k,v in os.environ.items() if k in ("PATH","HOME","LANG","NODE_PATH","SYSTEMROOT")}
    result=subprocess.run(["node",str(Path(__file__).with_name("validate.cjs"))],
                          input=markup,text=True,capture_output=True,env=env,timeout=45)
    if result.returncode:
        raise ValueError("MJML validation failed.")
    return True

def email_blocks(blocks):
    ends=[i for i,b in enumerate(blocks)
          if b.get("type")=="heading_2" and plain(b.get("heading_2",{}).get("rich_text",[]))=="End of email"]
    starts=[i for i,b in enumerate(blocks)
            if b.get("type")=="paragraph" and plain(b.get("paragraph",{}).get("rich_text",[])).startswith("Subject:")]
    if len(ends)!=1 or len(starts)!=1 or starts[0]>=ends[0]:
        raise ValueError("Keep one Subject line and one End of email heading.")
    return blocks[starts[0]:ends[0]]

def run_job(client,source,request,validate,build):
    snapshot=email_blocks(client.children(source))
    result=render(from_notion(snapshot))
    if len(result["mjml"].encode("utf-8"))>100000:
        raise ValueError("Shorten the email before exporting.")
    validate(result["mjml"])
    if snapshot!=email_blocks(client.children(source)):
        raise ValueError("The draft changed while generating.")
    return client.save_output(source,result,request,build)

def process_queue(client,source,queue,validate,build):
    source,queue=identifier(source),identifier(queue)
    if source==queue:
        raise ValueError("The draft and request database must be different.")
    counts={"ready":0,"failed":0}
    for row in client.requests(queue):
        request=identifier(row["id"])
        # Resolve an uncertain Ready write before doing any more conversion.
        try:
            existing=client.completed_output(source,request)
            if not existing:
                client.set_request(request,"Processing","Generating from the current saved draft. Please stop editing.")
                run_job(client,source,request,validate,build)
        except Exception:
            counts["failed"]+=1
            try:
                client.set_request(request,"Error",
                    "Generation could not be confirmed. Check the writing above End of email, image links and captions. "
                    "Previous code may be out of date. Fix the draft and click Generate MJML again. Ask the connection owner if it still fails.")
            except Exception:
                break
            continue
        try:
            client.set_request(request,"Ready","MJML is ready in the Generated MJML section on the draft page. Copy code and preview in SCLA.")
            counts["ready"]+=1
        except Exception:
            # Keep Processing. The next scheduled run will reuse the confirmed code.
            counts["failed"]+=1
            break
    return counts

def main():
    stage="workflow safety check"
    try:
        if (os.environ.get("GITHUB_ACTIONS")!="true"
                or os.environ.get("GITHUB_REF")!="refs/heads/main"
                or os.environ.get("GITHUB_EVENT_NAME") not in ("schedule","workflow_dispatch")
                or os.environ.get("COMMUNITY_EMAIL_ENABLED")!="true"):
            raise RuntimeError("Only the enabled GitHub main workflow may generate.")
        stage="Notion connection"
        token=os.environ.get("SCLA_EMAIL_NOTION_TOKEN") or os.environ["NOTION_API_KEY"]
        client=Notion(token)
        stage="draft page lookup"
        source=os.environ.get("SCLA_EMAIL_SOURCE_PAGE_ID") or client.named("Practice draft — do not send","page")
        stage="request queue lookup"
        queue=os.environ.get("SCLA_EMAIL_QUEUE_DATA_SOURCE_ID") or client.named("Email generation requests","data_source")
        stage="request processing"
        counts=process_queue(client,source,queue,
                             validate_mjml,os.environ.get("GITHUB_SHA","unknown")[:12])
        if counts["failed"]:
            print("One or more requests could not be confirmed. Check the private Notion request list.",file=sys.stderr)
            return 1
    except Exception:
        # Never print exception details, identifiers, API responses, or draft text.
        print("Email worker stopped during "+stage+". Check the Notion connection and shared pages.",file=sys.stderr)
        return 1
    print("Email queue check completed. Results remain in Notion.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
