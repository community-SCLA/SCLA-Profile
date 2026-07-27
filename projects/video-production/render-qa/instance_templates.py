#!/usr/bin/env python3
"""Give every repeated scene slot its own template instance file.

HyperFrames keys a sub-composition's identity to the FILE, not the slot:
the internal `data-composition-id`, the `window.__timelines[...]` key, and
every `id="..."` inside it are shared by every slot pointing at that file.
Use a template once per video and that is invisible. Use it twice — which
Motion v2 pacing forces, since a 14-scene lesson has only 12 templates —
and the instances collide: one timeline object survives, the other slots'
elements are never animated, and v2's exit tween + hard-kill blank them.

Symptom: headings/labels missing, or whole scenes rendering empty, in the
composited render only. Studio preview mounts each scene in its own iframe
and hides it entirely; `hyperframes snapshot` reproduces it.

This script rewrites the 2nd..Nth slot of each repeated template to its own
clone (`scla-points__i2.html`), with the composition id, timeline key, and
every id/class inside it suffixed so nothing is shared. The first slot keeps
the original file.

    python3 instance_templates.py <workspace>          # apply
    python3 instance_templates.py <workspace> --check   # exit 1 if slots share a file

Idempotent: already-cloned slots are left alone.
"""
import re
import sys
from pathlib import Path

CLIP_RE = re.compile(
    r'data-composition-id="(?P<host>[^"]+)"[^>]*?data-composition-src="compositions/(?P<src>[^"]+)"'
    r'|data-composition-src="compositions/(?P<src2>[^"]+)"[^>]*?data-composition-id="(?P<host2>[^"]+)"'
)


def slots(html):
    """[(host_id, src_filename, match_span)] in document order."""
    out = []
    for m in CLIP_RE.finditer(html):
        host = m.group("host") or m.group("host2")
        src = m.group("src") or m.group("src2")
        out.append((host, src, m.span()))
    return out


def rename_tokens(text, tokens, suffix):
    """Suffix each whole-token id/class name wherever it appears."""
    for tok in sorted(tokens, key=len, reverse=True):
        text = re.sub(r"(?<![\w-])" + re.escape(tok) + r"(?![\w-])", tok + suffix, text)
    return text


def clone(template_path, suffix):
    """Namespace one template file so nothing inside it is shared.

    Every scla-* template names its elements with one short prefix
    (`kp-heading`, `st-label`, …) and uses that prefix in ids, class names,
    CSS selectors, AND runtime string concatenation
    (`getElementById("kp-item-" + i)`). Renaming whole tokens would miss the
    concatenated form and leave null lookups, so the prefix itself is what
    gets namespaced: `kp-` -> `kp__i2-`, everywhere in the file.
    """
    text = template_path.read_text()
    m = re.search(r'id="root"[^>]*?data-composition-id="([^"]+)"', text)
    if not m:
        raise SystemExit(f"{template_path.name}: no root data-composition-id found")
    comp_id = m.group(1)

    # (?<![\w-]) so data-hf-id="hf-…" / data-composition-id="…" are not read as ids
    ids = [i for i in re.findall(r'(?<![\w-])id="([A-Za-z][\w-]*)"', text) if i != "root"]
    prefixes = {}
    for i in ids:
        if "-" in i:
            p = i.split("-", 1)[0] + "-"
            prefixes[p] = prefixes.get(p, 0) + 1
    if not prefixes:
        raise SystemExit(f"{template_path.name}: no hyphenated element ids to namespace")
    prefix = max(prefixes, key=prefixes.get)
    if prefixes[prefix] < len(ids) - 1:
        raise SystemExit(
            f"{template_path.name}: ids do not share one prefix "
            f"({prefixes[prefix]}/{len(ids)} use {prefix!r}) — namespace by hand"
        )

    new_prefix = prefix[:-1] + suffix + "-"
    text = text.replace(prefix, new_prefix)
    text = re.sub(r"(?<![\w-])" + re.escape(comp_id) + r"(?![\w-])", comp_id + suffix, text)
    return text, comp_id


def main():
    argv = sys.argv[1:]
    check_only = "--check" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)

    ws = Path(args[0]).resolve()
    index = ws / "index.html"
    html = index.read_text()
    seen, dupes, actions = {}, [], []

    for host, src, _ in slots(html):
        if src in seen:
            dupes.append((host, src))
        else:
            seen[src] = host

    if check_only:
        if dupes:
            print(f"[instance_templates:check] FAIL — {len(dupes)} slot(s) share a template file")
            for host, src in dupes:
                print(f"  ! {host} reuses compositions/{src} — clone it (instance_templates.py <ws>)")
            sys.exit(1)
        print("[instance_templates:check] ok — every slot has its own template file")
        return

    counters = {}
    for host, src in dupes:
        counters[src] = counters.get(src, 1) + 1
        suffix = f"__i{counters[src]}"
        stem = src[:-5] if src.endswith(".html") else src
        out_name = f"{stem}{suffix}.html"
        text, comp_id = clone(ws / "compositions" / src, suffix)
        (ws / "compositions" / out_name).write_text(text)
        # repoint just this slot
        html = re.sub(
            r'(data-composition-id="' + re.escape(host) + r'"[^>]*?data-composition-src=")compositions/'
            + re.escape(src),
            r"\1compositions/" + out_name,
            html,
        )
        html = re.sub(
            r'(data-composition-src=")compositions/' + re.escape(src)
            + r'("[^>]*?data-composition-id="' + re.escape(host) + r'")',
            r"\1compositions/" + out_name + r"\2",
            html,
        )
        actions.append(f"  {host}: {src} -> {out_name}  (composition id {comp_id}{suffix})")

    index.write_text(html)
    if actions:
        print(f"[instance_templates] cloned {len(actions)} repeated slot(s):")
        print("\n".join(actions))
    else:
        print("[instance_templates] nothing to do — every slot already has its own file")


if __name__ == "__main__":
    main()
