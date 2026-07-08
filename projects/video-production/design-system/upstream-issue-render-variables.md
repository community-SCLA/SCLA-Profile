> **Pending upstream filing** — this session's GitHub token is repo-scoped and cannot create issues on `heygen-com/hyperframes`. File with:
> `gh issue create --repo heygen-com/hyperframes --title "render: data-variable-values not injected into sub-compositions — getVariables() empty, defaults rendered silently (0.7.38–0.7.42)" --body-file projects/video-production/design-system/upstream-issue-render-variables.md`
> (strip this blockquote first), then delete this file and note the issue number in design-system/CLAUDE.md.

## Summary

`hyperframes render` leaves `window.__hyperframes.getVariables()` empty inside sub-compositions, so every sub-comp renders its JS-side **defaults** instead of the `data-variable-values` passed at the mount point in the host `index.html`. `preview` and `snapshot` inject the values correctly — so the composition looks right in every authoring/QA surface and then renders wrong content **silently (exit 0)**.

Reproduced on **0.7.38, and still present on 0.7.42** (latest at time of filing).

## Minimal repro (2 files)

`index.html` — mounts one sub-comp with `data-variable-values`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="640" data-height="360" data-duration="2">
      <div
        id="el-sub"
        data-composition-id="sub"
        data-composition-src="compositions/sub.html"
        data-variable-values='{"bg":"injected","label":"INJECTED"}'
        data-start="0" data-duration="2" data-track-index="1"
        data-width="640" data-height="360"
      ></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
```

`compositions/sub.html` — declares the variables, paints red/INJECTED if they arrive, blue/DEFAULT if they don't:

```html
<!doctype html>
<html lang="en"
  data-composition-variables='[
    {"id":"bg","type":"string","label":"Background key","default":"default"},
    {"id":"label","type":"string","label":"Label text","default":"DEFAULT"}
  ]'>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>
        #root { position: absolute; inset: 0; overflow: hidden; }
        #probe-label { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
          font: 900 120px system-ui, sans-serif; color: #fff; }
      </style>
      <div id="root" data-composition-id="sub" data-width="640" data-height="360" data-duration="2">
        <div id="probe-label" class="clip" data-start="0" data-duration="2" data-track-index="1">DEFAULT</div>
      </div>
      <script>
        (function () {
          const defaults = { bg: "default", label: "DEFAULT" };
          const vars = Object.assign({}, defaults,
            window.__hyperframes && window.__hyperframes.getVariables ? window.__hyperframes.getVariables() : {});
          document.getElementById("root").style.background = vars.bg === "injected" ? "#cc0000" : "#0000cc";
          document.getElementById("probe-label").textContent = vars.label;
          window.__timelines = window.__timelines || {};
          window.__timelines["sub"] = gsap.timeline({ paused: true });
        })();
      </script>
    </template>
  </body>
</html>
```

## Steps

```bash
npx hyperframes@0.7.42 snapshot --at 1   # frame is RED with "INJECTED"  ✅ values injected
npx hyperframes@0.7.42 render            # frame at 1s is BLUE with "DEFAULT" ❌ values lost
```

Extract a render frame to compare: `ffmpeg -ss 1 -i renders/*.mp4 -frames:v 1 frame.png`

## Expected

`render` injects the mount point's `data-variable-values` into the sub-composition (matching `preview`/`snapshot` behavior), or at minimum fails loudly when declared variables receive no values.

## Impact

Any template-library workflow (reusable sub-comp scene templates instantiated per video via variables) silently renders placeholder/default content. Because snapshot/preview look correct, the wrong output is only caught by extracting frames from the final MP4. Current workaround: bake real content into each scene file's `defaults` object (one file per mount), which defeats template reuse.

## Environment

- hyperframes 0.7.38 and 0.7.42 (`npx`), Node v24.14.0, linux x64 (GitHub Codespace, Docker), chrome-headless-shell 131.0.6778.85
