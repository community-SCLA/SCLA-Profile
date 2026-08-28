import importlib
import importlib.util
import io
import json
import unittest
from test_convert import api_sample

SOURCE="00000000-0000-4000-8000-000000000001"
OUTPUT="00000000-0000-4000-8000-000000000002"

class CloudContractTests(unittest.TestCase):
    def module(self,name):
        self.assertIsNotNone(importlib.util.find_spec(name),name+" cloud component not implemented yet")
        return importlib.import_module(name)

    def test_page_read_collects_all_pages(self):
        mod=self.module("notion_client")
        requests=[]
        def transport(method,path,data=None):
            requests.append((method,path,data))
            if "start_cursor=" not in path:
                return {"results":api_sample()[:2],"has_more":True,"next_cursor":"next-page"}
            return {"results":api_sample()[2:],"has_more":False,"next_cursor":None}
        client=mod.Notion("synthetic-token",transport=transport)
        self.assertEqual(client.children(SOURCE),api_sample())
        self.assertEqual(len(requests),2)
        self.assertIn("start_cursor=next-page",requests[1][1])

    def test_published_code_survives_notion_text_limits(self):
        mod=self.module("notion_client")
        requests=[]
        def transport(method,path,data=None):
            requests.append((method,path,data))
            return {"id":OUTPUT}
        client=mod.Notion("synthetic-token",transport=transport)
        code="<mjml>"+"é & text "*900+"</mjml>"
        client.create_export(OUTPUT,{"subject":"Example","mjml":code},"test-build")
        self.assertEqual(len(requests),1)
        method,path,data=requests[0]
        self.assertEqual((method,path),("POST","/pages"))
        code_block=next(b["code"] for b in data["children"] if b["type"]=="code")
        self.assertEqual("".join(t["text"]["content"] for t in code_block["rich_text"]),code)
        self.assertTrue(all(len(t["text"]["content"])<=2000 for t in code_block["rich_text"]))

    def test_generation_validates_before_publishing(self):
        mod=self.module("cloud_job")
        events=[]
        class Client:
            def children(self,page):
                events.append("read")
                return api_sample()
            def create_export(self,parent,result,build):
                events.append("publish")
                return {"id":OUTPUT}
        result=mod.run_job(Client(),SOURCE,OUTPUT,lambda text:events.append("validate"),"build")
        self.assertEqual(events,["read","validate","read","publish"])
        self.assertEqual(result["id"],OUTPUT)

    def test_validation_failure_does_not_publish(self):
        mod=self.module("cloud_job")
        class Client:
            published=False
            def children(self,page): return api_sample()
            def create_export(self,*args): self.published=True
        def reject(_): raise ValueError("Invalid test email")
        client=Client()
        with self.assertRaises(ValueError):
            mod.run_job(client,SOURCE,OUTPUT,reject,"build")
        self.assertFalse(client.published)

    def test_edit_during_generation_does_not_publish_stale_copy(self):
        mod=self.module("cloud_job")
        class Client:
            reads=0
            published=False
            def children(self,page):
                self.reads+=1
                return api_sample() if self.reads==1 else api_sample()[:-1]
            def create_export(self,*args): self.published=True
        client=Client()
        with self.assertRaises(ValueError):
            mod.run_job(client,SOURCE,OUTPUT,lambda _:None,"build")
        self.assertFalse(client.published)

    def test_relay_rejects_unauthorized_requests_and_ignores_payload_routes(self):
        mod=self.module("relay")
        sent=[]
        app=mod.make_app("a"*40,lambda:sent.append("fixed-workflow"))
        def request(secret,payload):
            body=json.dumps(payload).encode()
            env={"REQUEST_METHOD":"POST","PATH_INFO":"/generate","CONTENT_TYPE":"application/json",
                 "CONTENT_LENGTH":str(len(body)),"HTTP_X_SCLA_TRIGGER":secret,"wsgi.input":io.BytesIO(body)}
            statuses=[]
            data=b"".join(app(env,lambda status,headers:statuses.append(status)))
            return statuses[0],data
        self.assertTrue(request("bad",{})[0].startswith("401"))
        self.assertEqual(sent,[])
        self.assertTrue(request("a"*40,{"ref":"evil","page_id":"not-allowed"})[0].startswith("202"))
        self.assertEqual(sent,["fixed-workflow"])

    def test_relay_failure_does_not_leak_dispatch_error(self):
        mod=self.module("relay")
        def fail(): raise RuntimeError("sensitive upstream error")
        app=mod.make_app("a"*40,fail)
        statuses=[]
        env={"REQUEST_METHOD":"POST","PATH_INFO":"/generate","CONTENT_TYPE":"application/json",
             "CONTENT_LENGTH":"2","HTTP_X_SCLA_TRIGGER":"a"*40,"wsgi.input":io.BytesIO(b"{}")}
        body=b"".join(app(env,lambda status,headers:statuses.append(status)))
        self.assertTrue(statuses[0].startswith("502"))
        self.assertNotIn(b"sensitive",body)

if __name__=="__main__":
    unittest.main()
