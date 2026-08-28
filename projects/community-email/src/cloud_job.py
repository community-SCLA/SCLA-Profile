"""GitHub-hosted conversion; private content stays in memory and Notion."""
import json
import os
from pathlib import Path
import subprocess
import sys
from convert import from_notion,render
from notion_client import Notion,identifier

def validate_mjml(markup):
    env={k:v for k,v in os.environ.items() if k in ("PATH","HOME","LANG","NODE_PATH","SYSTEMROOT")}
    result=subprocess.run(["node",str(Path(__file__).with_name("validate.cjs"))],
                          input=markup,text=True,capture_output=True,env=env,timeout=45)
    if result.returncode:
        raise ValueError("MJML validation failed.")
    return True

def run_job(client,source,parent,validate,build):
    if identifier(source)==identifier(parent):
        raise ValueError("Keep the writing page and output page separate.")
    snapshot=client.children(source)
    result=render(from_notion(snapshot))
    if len(result["mjml"].encode("utf-8"))>100000:
        raise ValueError("Shorten the email before exporting.")
    validate(result["mjml"])
    if snapshot!=client.children(source):
        raise ValueError("The draft changed while generating. Try again when editing is finished.")
    return client.create_export(parent,result,build)

def main():
    client=None
    parent=None
    try:
        if os.environ.get("GITHUB_ACTIONS")!="true" or os.environ.get("GITHUB_REF")!="refs/heads/main":
            raise RuntimeError("This command only runs in the approved GitHub main workflow.")
        client=Notion(os.environ["SCLA_EMAIL_NOTION_TOKEN"])
        source=identifier(os.environ["SCLA_EMAIL_SOURCE_BLOCK_ID"])
        parent=identifier(os.environ["SCLA_EMAIL_OUTPUT_PAGE_ID"])
        run_job(client,source,parent,validate_mjml,os.environ.get("GITHUB_SHA","unknown")[:12])
    except Exception:
        # Never print exception details: API responses and draft text can be private.
        if client is not None and parent is not None:
            try:
                client.create_failure(parent)
            except Exception:
                pass
        print("Generation failed. Check the private Notion results page and connection settings.",file=sys.stderr)
        return 1
    print("Generated MJML saved to the configured private Notion results page.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
