import importlib
import importlib.util
import unittest
from pathlib import Path
from test_convert import api_sample, notion_text

SOURCE="00000000-0000-4000-8000-000000000001"
QUEUE="00000000-0000-4000-8000-000000000002"
REQUEST="00000000-0000-4000-8000-000000000003"
OUTPUT="00000000-0000-4000-8000-000000000004"
OLD="00000000-0000-4000-8000-000000000005"

def draft():
    return api_sample()+[notion_text("End of email","heading_2"),
        {"id":OUTPUT,"type":"toggle","toggle":{"rich_text":[{"type":"text","text":{"content":"Generated MJML — copy into SCLA"}}]}},
        {"type":"unsupported","unsupported":{"block_type":"button"}}]

class QueueClient:
    def __init__(self):
        self.events=[]
        self.status="Queued"
        self.published=None
        self.reads=0
        self.change=False
        self.fail_publish=False
        self.fail_ack=False
    def requests(self,queue):
        return [{"id":REQUEST}] if self.status in ("Queued","Processing") else []
    def set_request(self,request,status,note):
        self.events.append(status)
        if status=="Ready" and self.fail_ack:
            self.fail_ack=False
            raise RuntimeError("uncertain acknowledgement")
        self.status=status
    def completed_output(self,source,request):
        return self.published
    def children(self,source):
        self.reads+=1
        return draft() if not self.change or self.reads==1 else [notion_text("Subject: changed")]+draft()[1:]
    def save_output(self,source,result,request,build):
        self.events.append("publish")
        if self.fail_publish: raise RuntimeError("private upstream message")
        self.published=OUTPUT
        return OUTPUT

class CloudContractTests(unittest.TestCase):
    def module(self,name):
        self.assertIsNotNone(importlib.util.find_spec(name))
        return importlib.import_module(name)

    def test_workflow_uses_only_the_approved_universal_auth_secrets(self):
        workflow=(Path(__file__).parents[3]/".github/workflows/community-email.yml").read_text()
        self.assertIn("method: universal",workflow)
        self.assertIn("${{ secrets.INFISICAL_CLIENT_ID }}",workflow)
        self.assertIn("${{ secrets.INFISICAL_SECRET }}",workflow)
        self.assertIn("project-slug: scla-projects-n-joy",workflow)
        self.assertIn("env-slug: dev",workflow)
        self.assertNotIn("method: oidc",workflow)
        self.assertNotIn("COMMUNITY_EMAIL_INFISICAL_IDENTITY_ID",workflow)
        self.assertNotIn("id-token: write",workflow)

    def test_page_read_collects_all_pages(self):
        mod=self.module("notion_client")
        requests=[]
        def transport(method,path,data=None):
            requests.append((method,path,data))
            if "start_cursor=" not in path:
                return {"results":api_sample()[:2],"has_more":True,"next_cursor":"next-page"}
            return {"results":api_sample()[2:],"has_more":False}
        client=mod.Notion("synthetic-token",transport=transport)
        self.assertEqual(client.children(SOURCE),api_sample())
        self.assertEqual(len(requests),2)

    def test_source_excludes_button_and_generated_output(self):
        mod=self.module("cloud_job")
        self.assertTrue(callable(getattr(mod,"email_blocks",None)),"Writing boundary not implemented")
        self.assertEqual(mod.email_blocks(draft()),api_sample())
        with self.assertRaises(ValueError): mod.email_blocks(api_sample())
        with self.assertRaises(ValueError): mod.email_blocks(draft()+[notion_text("End of email","heading_2")])

    def test_queue_validates_before_same_page_publication_and_acknowledgement(self):
        mod=self.module("cloud_job")
        self.assertTrue(callable(getattr(mod,"process_queue",None)),"Queue processing not implemented")
        client=QueueClient()
        result=mod.process_queue(client,SOURCE,QUEUE,lambda _:client.events.append("validate"),"build")
        self.assertEqual(client.events,["Processing","validate","publish","Ready"])
        self.assertEqual(result,{"ready":1,"failed":0})
        self.assertEqual(client.reads,2)

    def test_invalid_or_changed_draft_preserves_previous_output(self):
        mod=self.module("cloud_job")
        self.assertTrue(callable(getattr(mod,"process_queue",None)),"Queue processing not implemented")
        for change in (False,True):
            client=QueueClient()
            client.change=change
            def validate(_):
                if not change: raise ValueError("invalid synthetic content")
            result=mod.process_queue(client,SOURCE,QUEUE,validate,"build")
            self.assertEqual(result["failed"],1)
            self.assertNotIn("publish",client.events)
            self.assertEqual(client.status,"Error")

    def test_retry_after_uncertain_acknowledgement_does_not_generate_twice(self):
        mod=self.module("cloud_job")
        self.assertTrue(callable(getattr(mod,"process_queue",None)),"Queue processing not implemented")
        client=QueueClient()
        client.fail_ack=True
        mod.process_queue(client,SOURCE,QUEUE,lambda _:None,"build")
        self.assertEqual(client.status,"Processing")
        mod.process_queue(client,SOURCE,QUEUE,lambda _:self.fail("must reuse confirmed output"),"build")
        self.assertEqual(client.events.count("publish"),1)
        self.assertEqual(client.status,"Ready")

    def test_empty_queue_does_not_read_or_publish_draft(self):
        mod=self.module("cloud_job")
        self.assertTrue(callable(getattr(mod,"process_queue",None)),"Queue processing not implemented")
        client=QueueClient()
        client.status="Ready"
        self.assertEqual(mod.process_queue(client,SOURCE,QUEUE,lambda _:self.fail("no work"),"build"),
                         {"ready":0,"failed":0})
        self.assertEqual(client.reads,0)

    def test_request_query_paginates_and_status_writes_stay_in_notion(self):
        mod=self.module("notion_client")
        calls=[]
        def transport(method,path,data=None):
            calls.append((method,path,data))
            if method=="PATCH": return {"id":REQUEST}
            if "start_cursor" not in data:
                return {"results":[{"id":REQUEST}],"has_more":True,"next_cursor":"next"}
            return {"results":[{"id":OLD}],"has_more":False}
        client=mod.Notion("synthetic-token",transport=transport)
        self.assertTrue(callable(getattr(client,"requests",None)),"Queue API not implemented")
        self.assertEqual([r["id"] for r in client.requests(QUEUE)],[REQUEST,OLD])
        self.assertEqual(calls[0][1],"/data_sources/"+QUEUE+"/query")
        self.assertEqual(calls[1][2]["start_cursor"],"next")
        self.assertEqual(calls[0][2]["filter"],{"or":[
            {"property":"Status","select":{"equals":"Queued"}},
            {"property":"Status","select":{"equals":"Processing"}}]})
        client.set_request(REQUEST,"Ready","Copy code")
        self.assertEqual(calls[-1][2]["properties"]["Status"],{"select":{"name":"Ready"}})

    def test_same_page_output_round_trip_preserves_user_content_and_retires_only_old_generated_code(self):
        mod=self.module("notion_client")
        self.assertTrue(callable(getattr(mod.Notion,"save_output",None)),"Same-page output not implemented")
        code="<mjml>"+"é & text "*900+"</mjml>"
        old={"id":OLD,"type":"code","code":{"caption":[{"text":{"content":"SCLA generated | request "+OLD+" | old"}}],"rich_text":[{"text":{"content":"old code"}}]}}
        note={"id":QUEUE,"type":"paragraph","paragraph":{"rich_text":[{"text":{"content":"A teammate note"}}]}}
        children=[old,note]
        calls=[]
        def transport(method,path,data=None):
            calls.append((method,path,data))
            if method=="GET" and path.startswith("/blocks/"+SOURCE+"/"):
                return {"results":draft(),"has_more":False}
            if method=="GET": return {"results":children[:],"has_more":False}
            if method=="PATCH":
                added=dict(data["children"][0],id=REQUEST)
                children.append(added)
                return {"results":[added]}
            if method=="DELETE":
                children[:]=[b for b in children if b["id"]!=path.rsplit("/",1)[-1]]
                return {"id":OLD,"archived":True}
            self.fail("unexpected operation")
        client=mod.Notion("synthetic-token",transport=transport)
        result=client.save_output(SOURCE,{"subject":"Example","mjml":code},REQUEST,"build")
        self.assertEqual(result,REQUEST)
        self.assertEqual([b["id"] for b in children],[QUEUE,REQUEST])
        code_block=children[-1]["code"]
        self.assertEqual("".join(t["text"]["content"] for t in code_block["rich_text"]),code)
        self.assertTrue(all(len(t["text"]["content"])<=2000 for t in code_block["rich_text"]))
        self.assertEqual(client.completed_output(SOURCE,REQUEST),REQUEST)
        self.assertFalse(any(method=="POST" and path=="/pages" for method,path,_ in calls))

    def test_unconfirmed_output_never_deletes_previous_success(self):
        mod=self.module("notion_client")
        self.assertTrue(callable(getattr(mod.Notion,"save_output",None)),"Same-page output not implemented")
        calls=[]
        def transport(method,path,data=None):
            calls.append((method,path,data))
            if method=="GET" and path.startswith("/blocks/"+SOURCE+"/"):
                return {"results":draft(),"has_more":False}
            if method=="GET": return {"results":[],"has_more":False}
            if method=="PATCH": return {"results":[{"id":REQUEST}]}
            self.fail("unconfirmed output must not delete anything")
        client=mod.Notion("synthetic-token",transport=transport)
        with self.assertRaises(Exception):
            client.save_output(SOURCE,{"subject":"Example","mjml":"<mjml></mjml>"},REQUEST,"build")
        self.assertFalse(any(c[0]=="DELETE" for c in calls))

if __name__=="__main__": unittest.main()
