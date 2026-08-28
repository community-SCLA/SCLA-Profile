"""WSGI entry point for an approved HTTPS host; does not accept draft content."""
import hmac
import json
import os
from pathlib import Path
import re
from urllib.request import Request,build_opener
from notion_client import NoRedirect

def dispatch():
    # Repository authority comes from the existing registry, never webhook input.
    registry=json.loads((Path(__file__).resolve().parents[3]/"config/endpoints.json").read_text())
    repository=next(x["id"] for x in registry["github"] if x["type"]=="repo")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repository):
        raise RuntimeError("Invalid repository configuration.")
    req=Request("https://api.github.com/repos/"+repository+"/actions/workflows/community-email.yml/dispatches",
                data=b'{"ref":"main"}',method="POST",headers={
                    "Authorization":"Bearer "+os.environ["SCLA_EMAIL_DISPATCH_TOKEN"],
                    "Accept":"application/vnd.github+json",
                    "Content-Type":"application/json",
                    "X-GitHub-Api-Version":"2022-11-28",
                    "User-Agent":"SCLA-community-email",
                })
    with build_opener(NoRedirect).open(req,timeout=15) as response:
        if response.status not in (200,204):
            raise RuntimeError("Dispatch failed.")

def make_app(secret,send):
    if len(secret)<32:
        raise ValueError("Configure a strong trigger secret before serving requests.")
    def app(env,start_response):
        def respond(status,message):
            body=json.dumps({"message":message}).encode()
            start_response(status,[("Content-Type","application/json"),("Cache-Control","no-store"),
                                   ("Content-Length",str(len(body)))])
            return [body]
        if env.get("REQUEST_METHOD")!="POST" or env.get("PATH_INFO")!="/generate":
            return respond("404 Not Found","Not found.")
        supplied=env.get("HTTP_X_SCLA_TRIGGER","")
        if not hmac.compare_digest(supplied.encode(),secret.encode()):
            return respond("401 Unauthorized","Unauthorized.")
        if env.get("CONTENT_TYPE","").split(";")[0].strip()!="application/json":
            return respond("415 Unsupported Media Type","JSON required.")
        try:
            size=int(env.get("CONTENT_LENGTH","0"))
            if size<2 or size>65536:
                return respond("413 Content Too Large","Invalid request size.")
            payload=env["wsgi.input"].read(size)
            if len(payload)!=size or not isinstance(json.loads(payload),dict):
                return respond("400 Bad Request","Invalid JSON.")
        except (ValueError,TypeError,KeyError):
            return respond("400 Bad Request","Invalid JSON.")
        try:
            # Payload cannot select a branch, repository, source page, or destination.
            send()
        except Exception:
            return respond("502 Bad Gateway","Could not confirm generation. Check results before retrying.")
        return respond("202 Accepted","Generation requested. Open the Notion results page in a moment.")
    return app

def application(env,start_response):
    try:
        secret=os.environ["SCLA_EMAIL_TRIGGER_SECRET"]
        app=make_app(secret,dispatch)
    except (KeyError,ValueError):
        body=b'{"message":"Trigger is not configured."}'
        start_response("503 Service Unavailable",[("Content-Type","application/json"),("Content-Length",str(len(body)))])
        return [body]
    return app(env,start_response)
