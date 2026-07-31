#!/usr/bin/env node
// probe_geometry.mjs — runtime geometry probe (spike).
//
// Drives a HyperFrames project in the same headless Chrome the renderer uses,
// seeks to N sample times, and dumps for every element its real
// getBoundingClientRect(), computed font-size/weight, EFFECTIVE opacity
// (product up the ancestor chain), visibility, and own text.
//
// This is the measurement boxmodel.py approximates. Two things it has that a
// static model cannot: real layout (flow, flex, grid, calc, %) and TIME.
//
//   node probe_geometry.mjs <project-dir> --at t1,t2,... [--out probe.json]
//
// Exit 0 on a clean probe. Non-zero means the probe itself failed — never a
// verdict about the composition.

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HF = "/home/codespace/.npm/_npx/702923228c2ce1e6/node_modules/hyperframes";
const PUPPETEER = "/home/codespace/.npm/_npx/702923228c2ce1e6/node_modules/puppeteer-core/lib/puppeteer/puppeteer-core.js";
const CHROME = "/home/codespace/.cache/hyperframes/chrome/chrome-headless-shell/linux-152.0.7928.2/chrome-headless-shell-linux64/chrome-headless-shell";
const RUNTIME = path.join(HF, "dist/hyperframe.runtime.iife.js");

const MIME = {
  ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript",
  ".css": "text/css", ".json": "application/json", ".woff2": "font/woff2",
  ".woff": "font/woff", ".ttf": "font/ttf", ".png": "image/png",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
  ".wav": "audio/wav", ".mp3": "audio/mpeg", ".mp4": "video/mp4",
};

const argv = process.argv.slice(2);
const positional = argv.filter((a) => !a.startsWith("--"));
const flag = (name) => {
  const i = argv.indexOf(name);
  return i === -1 ? null : argv[i + 1];
};
if (!positional.length) {
  console.error("usage: probe_geometry.mjs <project-dir> --at t1,t2,...");
  process.exit(2);
}
const root = path.resolve(positional[0]);
const times = (flag("--at") || "").split(",").map(Number).filter((n) => !Number.isNaN(n));
if (!times.length) {
  console.error("--at is required (comma-separated seconds)");
  process.exit(2);
}
const outPath = flag("--out");

// ── serve the project, injecting the runtime the preview server injects ─────
const runtimeJs = fs.readFileSync(RUNTIME, "utf8");
const server = http.createServer((req, res) => {
  const url = decodeURIComponent((req.url || "/").split("?")[0]);
  if (url === "/__hf/runtime.js") {
    res.writeHead(200, { "Content-Type": "text/javascript" });
    return res.end(runtimeJs);
  }
  const rel = url === "/" ? "index.html" : url.replace(/^\/+/, "");
  const file = path.join(root, rel);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); return res.end("not found");
  }
  const ext = path.extname(file).toLowerCase();
  if (ext === ".html") {
    let html = fs.readFileSync(file, "utf8");
    // Inject only into the entry document; sub-compositions are fetched by the
    // runtime and must not each bootstrap their own copy.
    if (rel === "index.html") {
      const tag = '<script src="/__hf/runtime.js"></script>';
      html = html.includes("</body>") ? html.replace("</body>", `${tag}\n</body>`) : html + tag;
    }
    res.writeHead(200, { "Content-Type": "text/html" });
    return res.end(html);
  }
  res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});

await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;

const { default: puppeteer } = await import(PUPPETEER);
const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--font-render-hinting=none",
         "--force-device-scale-factor=1", "--hide-scrollbars", "--mute-audio"],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  const consoleErrors = [];
  page.on("pageerror", (e) => consoleErrors.push(String(e).slice(0, 300)));

  await page.goto(`http://127.0.0.1:${port}/index.html`,
                  { waitUntil: "networkidle2", timeout: 60000 });
  await page.waitForFunction(
    "window.__playerReady === true && window.__player && !window.__hfTimelinesBuilding",
    { timeout: 60000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);

  const DUMP = () => {
    const out = [];
    const effOpacity = (el) => {
      let o = 1, cur = el;
      while (cur && cur.nodeType === 1) {
        const cs = getComputedStyle(cur);
        if (cs.display === "none" || cs.visibility === "hidden") return 0;
        o *= parseFloat(cs.opacity || "1");
        cur = cur.parentElement;
      }
      return o;
    };
    // Own text only: a wrapper and its child would otherwise report the same run.
    const ownText = (el) => Array.from(el.childNodes)
      .filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.replace(/\s+/g, " ").trim())
      .join(" ").trim();

    // The INK box: union of Range client rects over the element's own text
    // nodes. This is the browser's own answer to "where are the glyphs", i.e.
    // exactly what boxmodel.py's ink model approximates — a centred one-line
    // caption in a 540px box inks only the glyph run, not the empty sides.
    const inkBox = (el) => {
      let box = null;
      for (const n of el.childNodes) {
        if (n.nodeType !== 3 || !n.textContent.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(n);
        for (const r of range.getClientRects()) {
          if (r.width <= 0 || r.height <= 0) continue;
          box = box
            ? { x: Math.min(box.x, r.x), y: Math.min(box.y, r.y),
                r: Math.max(box.r, r.right), b: Math.max(box.b, r.bottom) }
            : { x: r.x, y: r.y, r: r.right, b: r.bottom };
        }
        range.detach();
      }
      return box && { x: +box.x.toFixed(2), y: +box.y.toFixed(2),
                      w: +(box.r - box.x).toFixed(2), h: +(box.b - box.y).toFixed(2) };
    };

    for (const el of document.querySelectorAll("body *")) {
      const tag = el.tagName.toLowerCase();
      if (tag === "script" || tag === "style" || tag === "audio") continue;
      const r = el.getBoundingClientRect();
      if (r.width <= 0 && r.height <= 0) continue;
      const cs = getComputedStyle(el);
      out.push({
        tag,
        id: el.id || null,
        cls: el.className && typeof el.className === "string"
          ? el.className.trim().split(/\s+/).filter(Boolean) : [],
        x: +r.x.toFixed(2), y: +r.y.toFixed(2),
        w: +r.width.toFixed(2), h: +r.height.toFixed(2),
        ink: inkBox(el),
        fontSize: parseFloat(cs.fontSize),
        fontWeight: cs.fontWeight,
        opacity: +effOpacity(el).toFixed(4),
        text: ownText(el).slice(0, 160),
      });
    }
    return out;
  };

  const samples = [];
  for (const t of times) {
    await page.evaluate(async (tt) => {
      if (window.__player.renderSeek) await window.__player.renderSeek(tt);
      else window.__player.seek(tt);
    }, t);
    await new Promise((r) => setTimeout(r, 60));
    samples.push({ t, elements: await page.evaluate(DUMP) });
  }

  const result = {
    project: root, duration: await page.evaluate(() => window.__player.getDuration()),
    samples, pageErrors: consoleErrors,
  };
  const json = JSON.stringify(result, null, 1);
  if (outPath) { fs.writeFileSync(outPath, json); console.error(`wrote ${outPath}`); }
  else console.log(json);
  const visible = samples.reduce((n, s) => n + s.elements.filter((e) => e.opacity > 0.01).length, 0);
  console.error(`probe ok — ${samples.length} sample(s), ` +
                `${visible} visible element instance(s), ${consoleErrors.length} page error(s)`);
} finally {
  await browser.close();
  server.close();
}
