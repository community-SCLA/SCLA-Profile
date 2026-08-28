import copy
import unittest
import xml.etree.ElementTree as ET
import convert

def text(value, kind="notion-text-block", rich=None):
    import html
    return {"type": kind, "text": value, "html": rich if rich is not None else html.escape(value)}

def sample():
    return [
        text("Subject: Example weekly email"),
        text("Preview: An example preview"),
        text("Welcome & hello"),
        text("News", "notion-sub_header-block"),
        text("An approved announcement."),
        {"type":"notion-image-block", "text":"Example landscape", "src":"https://example.org/landscape.png"},
        text("Insight", "notion-sub_header-block"),
        text("One idea to try."),
        text("Visit SCLA", rich='<a href="https://www.thescla.org">Visit SCLA</a>'),
    ]

def notion_text(value, kind="paragraph", href=None, bold=False):
    return {"object":"block", "type":kind, "has_children":False, kind:{"rich_text":[{
        "type":"text", "text":{"content":value, "link":{"url":href} if href else None},
        "plain_text":value, "href":href, "annotations":{"bold":bold}
    }]}}

def api_sample():
    return [
        notion_text("Subject: Example weekly email"),
        notion_text("Preview: An example preview"),
        notion_text("Welcome & hello", bold=True),
        notion_text("News", "heading_2"),
        notion_text("Visit SCLA", href="https://www.thescla.org"),
    ]

class RenderTests(unittest.TestCase):
    def test_complete_email_preserves_copy_brand_and_merge_fields(self):
        result=convert.render(sample())
        self.assertEqual(result["subject"], "Example weekly email")
        root=ET.fromstring(result["mjml"])
        self.assertEqual(root.tag,"mjml")
        self.assertIn("Welcome &amp; hello",result["mjml"])
        self.assertIn("Hi {{user.firstName}}",result["mjml"])
        self.assertIn("{{system.linkToUnsubscribe}}",result["mjml"])
        self.assertEqual(root.find(".//mj-button").attrib["background-color"],"#EAAB2D")
        self.assertNotIn("Subject:",result["mjml"])

    def test_sections_can_be_removed_and_reordered(self):
        blocks=sample()
        result=convert.render(blocks[:3]+blocks[6:]+blocks[3:6])["mjml"]
        self.assertLess(result.index(">Insight<"),result.index(">News<"))
        short=convert.render(blocks[:3]+blocks[6:])["mjml"]
        self.assertNotIn(">News<",short)
        self.assertNotIn("landscape.png",short)

    def test_inline_link_stays_text_and_linked_paragraph_becomes_button(self):
        blocks=sample()
        blocks.insert(3,text("Read this link.",rich='Read <a href="https://example.org">this link</a>.'))
        root=ET.fromstring(convert.render(blocks)["mjml"])
        self.assertEqual(len(root.findall(".//mj-button")),1)
        self.assertTrue(any("Read " in ET.tostring(x,encoding="unicode") for x in root.iter("mj-text")))

    def test_invalid_input_stops_without_silent_content_loss(self):
        cases=[[],sample()[1:]]
        for update in [
            {"type":"notion-table-block"},
            {"type":"notion-image-block","text":""},
            {"type":"notion-image-block","src":"https://example.org/a?X-Amz-Signature=temporary"},
        ]:
            blocks=sample()
            blocks[5].update(update)
            cases.append(blocks)
        cases.append(sample()+[text("Empty section","notion-sub_header-block")])
        for blocks in cases:
            with self.subTest(case=len(blocks)):
                with self.assertRaises(ValueError):
                    convert.render(blocks)

    def test_notion_api_blocks_render_without_a_browser_snapshot(self):
        adapter=getattr(convert,"from_notion",None)
        self.assertTrue(callable(adapter),"Notion API adapter is not implemented yet")
        result=convert.render(adapter(api_sample()))
        self.assertIn("<strong>Welcome &amp; hello</strong>",result["mjml"])
        self.assertEqual(ET.fromstring(result["mjml"]).find(".//mj-button").text,"Visit SCLA")

if __name__=="__main__":
    unittest.main()
