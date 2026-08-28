"""Deterministic SCLA email renderer. No network calls or sending."""
import copy
import datetime
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


def safe_url(value, image=False):
    if image and value.startswith('/image/'):
        value = unquote(value.split('?', 1)[0][len('/image/'):])
    parts = urlsplit(value)
    if (parts.scheme != 'https' or not parts.hostname or parts.username
            or parts.password or parts.hostname in ('localhost', '127.0.0.1', '::1')):
        raise ValueError('Use a public HTTPS link.')
    if image and (parts.hostname.endswith(('notion.so', 'notion.com', 'notion.site'))
                  or any(key in parts.query.lower() for key in ('signature=', 'expires=', 'token='))):
        raise ValueError('Image needs a lasting public URL, not a temporary Notion upload.')
    return value


class Inline(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.output, self.stack, self.links, self.plain = [], [], [], []
        self.active_link = None
        self.feed(value)
        self.close()
        if self.stack:
            raise ValueError('Unclosed inline formatting.')

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'br':
            self.output.append('<br />')
            return
        mapped = {'b':'strong', 'strong':'strong', 'i':'em', 'em':'em', 'u':'u', 's':'s', 'span':'', 'a':'a'}.get(tag)
        if mapped is None:
            raise ValueError('Unsupported inline content: ' + tag)
        self.stack.append((tag, mapped))
        if mapped == 'a':
            if self.active_link is not None:
                raise ValueError('Nested links are unsupported.')
            url = safe_url(attrs.get('href', ''))
            self.active_link = {'url':url, 'text':''}
            self.output.append('<a href="' + html.escape(url, quote=True) + '" style="color:#3393D6">')
        elif mapped:
            self.output.append('<' + mapped + '>')

    def handle_endtag(self, tag):
        if tag == 'br':
            return
        if not self.stack or self.stack[-1][0] != tag:
            raise ValueError('Mismatched inline formatting.')
        _, mapped = self.stack.pop()
        if mapped:
            self.output.append('</' + mapped + '>')
        if mapped == 'a':
            self.links.append(self.active_link)
            self.active_link = None

    def handle_data(self, text):
        self.output.append(html.escape(text).replace('\n', '<br />'))
        self.plain.append(text)
        if self.active_link is not None:
            self.active_link['text'] += text


def render(blocks):
    if len(blocks) < 3 or not blocks[0]['text'].startswith('Subject: ') or not blocks[1]['text'].startswith('Preview: '):
        raise ValueError('Start the practice page with Subject: and Preview: paragraphs.')
    subject, preview = blocks[0]['text'][9:].strip(), blocks[1]['text'][9:].strip()
    if not subject or not preview:
        raise ValueError('Subject and preview must not be empty.')
    groups = [[]]
    has_content = False
    for block in blocks[2:]:
        kind, text = block['type'], block['text'].strip()
        if kind not in ('notion-text-block', 'notion-sub_header-block', 'notion-image-block'):
            raise ValueError('Unsupported block; convert to a paragraph, Heading 2, or image: ' + str(kind))
        if kind == 'notion-image-block':
            if not text:
                raise ValueError('Add an image caption describing the image.')
            url = safe_url(block['src'], image=True)
            groups[-1].append('<mj-image width="550px" border-radius="5px" src="' + html.escape(url, quote=True) + '" alt="' + html.escape(text, quote=True) + '" />')
            has_content = True
            continue
        if not text:
            if kind == 'notion-sub_header-block':
                raise ValueError('Remove or fill the empty section headline.')
            continue
        rich = Inline(block['html'])
        if ''.join(rich.plain).strip() != text:
            raise ValueError('Text and formatting snapshot differ. Read the page again.')
        if kind == 'notion-sub_header-block':
            groups.append(['<mj-text color="#3393D6" font-size="20px" font-weight="700" padding-top="24px">' + ''.join(rich.output) + '</mj-text>'])
        elif len(rich.links) == 1 and rich.links[0]['text'].strip() == text:
            link = rich.links[0]
            groups[-1].append('<mj-button background-color="#EAAB2D" font-size="16px" border-radius="20px" inner-padding="15px 40px" href="' + html.escape(link['url'], quote=True) + '">' + html.escape(text) + '</mj-button>')
            has_content = True
        else:
            groups[-1].append('<mj-text>' + ''.join(rich.output) + '</mj-text>')
            has_content = True
    if not has_content:
        raise ValueError('Write some email content first.')
    base = ET.fromstring(Path(__file__).parent.parent.joinpath('config/weekly-community.mjml').read_text())
    base.find('mj-head/mj-preview').text = preview
    body = base.find('mj-body')
    header, signoff, footer = copy.deepcopy(body[0]), copy.deepcopy(body[-2]), copy.deepcopy(body[-1])
    body[:] = [header]
    groups[0].insert(0, '<mj-text>Hi {{user.firstName}},</mj-text>')
    for index, group in enumerate(groups):
        if index and len(group) == 1:
            raise ValueError('Section has a headline but no content.')
        markup = '<mj-section padding="0 0 12px"><mj-column>' + ''.join(group) + '</mj-column></mj-section>'
        body.append(ET.fromstring(markup))
    for element in footer.iter('mj-text'):
        if element.text and element.text.startswith('© '):
            element.text = '© ' + str(datetime.date.today().year) + ' The Society for Collegiate Leadership & Achievement, LLC'
    body.extend([signoff, footer])
    return {'subject':subject, 'mjml':ET.tostring(base, encoding='unicode') + '\n'}


