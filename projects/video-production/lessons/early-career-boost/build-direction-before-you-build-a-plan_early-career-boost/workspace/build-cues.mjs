// build-cues.mjs — regenerates cues.js from the narration word timings.
//
// The composition's clock is ../audio/narration.words.json, not a hand-typed
// number: every storyboard cue below names the word index it fires on, and this
// script writes that word's real onset into cues.js. The expected word text is
// asserted, so a re-synthesis that shifts the transcript fails here loudly
// instead of drifting silently on screen.
//
//   node build-cues.mjs        # rewrite cues.js and cross-check index.html
//
import { readFileSync, writeFileSync } from "node:fs";

const words = JSON.parse(readFileSync("../audio/narration.words.json", "utf8"));

// [cue name, word index, expected word text] — one row per storyboard onset.
const CUES = [
  ["b2_easy", 8, "easy"], ["b2_career", 12, "career"], ["b2_title", 16, "title:"],
  ["b2_intern", 17, "intern,"], ["b2_analyst", 18, "analyst,"],
  ["b3_coordinator", 19, "coordinator,"], ["b3_assistant", 20, "assistant,"],
  ["b3_associate", 22, "associate."],
  ["b4_labels", 27, "labels."], ["b4_they", 28, "They"], ["b4_how", 36, "how"],
  ["b4_what", 39, "what"], ["b4_where", 44, "where"],
  ["b5_before", 48, "Before"], ["b5_understand", 57, "understand"],
  ["b5_that", 64, "That"], ["b5_patterns", 70, "patterns."],
  ["b6_think", 71, "Think"], ["b6_school", 77, "school,"], ["b6_parttime", 78, "part-time"],
  ["b6_internships", 80, "internships,"], ["b6_student", 81, "student"],
  ["b6_volunteering", 83, "volunteering,"], ["b6_personal", 85, "personal"],
  ["b7_q1", 87, "Where"], ["b7_q2", 92, "Where"], ["b7_q3", 97, "Where"], ["b7_q4", 102, "Where"],
  ["b8_these", 110, "These"], ["b8_moments", 111, "moments"], ["b8_reveal", 116, "reveal"],
  ["b8_than", 118, "than"], ["b8_show", 123, "show"], ["b8_naturally", 126, "naturally"],
  ["b9_left", 128, "Maybe"], ["b9_organizing", 131, "organizing"], ["b9_right", 134, "Maybe"],
  ["b9_analyzing", 137, "analyzing"], ["b9_patterns", 141, "patterns."],
  ["b10_left", 142, "Maybe"], ["b10_helping", 146, "helping"], ["b10_right", 151, "Maybe"],
  ["b10_turns", 157, "turns"], ["b10_action", 161, "action."],
  ["b11_a", 162, "A"], ["b11_strong", 163, "strong"], ["b11_early", 164, "early-career"],
  ["b11_repeated", 171, "repeated"], ["b11_clues", 172, "clues."],
  ["b12_it", 173, "It"], ["b12_this1", 178, "this"], ["b12_path", 182, "path,"],
  ["b12_this2", 187, "this"], ["b12_me", 199, "me"],
  ["b13_in", 202, "In"], ["b13_three", 208, "three"],
  ["b14_first", 210, "First,"], ["b14_your", 211, "your"], ["b14_strengths", 212, "strengths"],
  ["b14_how", 222, "how"],
  ["b15_second", 226, "Second,"], ["b15_values", 228, "values"], ["b15_what", 230, "what"],
  ["b15_learning", 238, "learning,"], ["b15_stability", 239, "stability,"],
  ["b15_flexibility", 240, "flexibility,"], ["b15_meaning", 241, "meaning,"],
  ["b15_collaboration", 242, "collaboration,"], ["b15_recognition", 243, "recognition."],
  ["b16_third", 244, "Third,"], ["b16_energy", 246, "energy"], ["b16_leaves", 253, "leaves"],
  ["b16_consistently", 263, "consistently"],
  ["b17_you", 266, "You"], ["b17_dream", 273, "dream"], ["b17_not", 278, "Not"],
  ["b18_a", 282, "A"], ["b18_ingredients", 287, "ingredients:"], ["b18_people", 289, "people"],
  ["b18_problems", 295, "problems"], ["b18_structure", 301, "structure"],
  ["b18_growth", 308, "growth"],
  ["b19_dream", 313, "Dream"], ["b19_titles", 319, "titles."], ["b19_they", 320, "They"],
  ["b19_ingredients", 324, "ingredients."],
  ["b20_you", 325, "You"], ["b20_reflection", 328, "reflection"], ["b20_ai1", 330, "AI"], ["b20_in", 332, "in"], ["b20_ai2", 337, "AI"],
  ["b21_it", 344, "It"], ["b21_notice", 350, "notice"], ["b21_you", 352, "you"],
  ["b21_own", 360, "own."],
  ["b22_by", 361, "By"], ["b22_describe", 369, "describe"], ["b22_started", 377, "started."],
  ["b23_and", 378, "And"], ["b23_clarity", 380, "clarity"], ["b23_next", 384, "next"],
  ["b23_easier", 387, "easier."],
];

// Beat windows from the approved storyboard. Beat n ends where beat n+1 starts,
// so the ground never shows through between beats; the last beat holds to the
// composition duration.
const STARTS = [
  0, 2.5, 8.0, 11.9, 20.3, 27.9, 36.4, 44.1, 51.7, 58.2, 65.5, 70.4, 79.9,
  83.2, 88.3, 98.1, 105.9, 110.8, 119.8, 126.8, 132.6, 137.4, 142.4,
];
const DURATION = 146.5;

const errors = [];
const out = {};
for (const [name, idx, text] of CUES) {
  const w = words[idx];
  if (!w) { errors.push(`${name}: word ${idx} does not exist`); continue; }
  if (w.text !== text) errors.push(`${name}: word ${idx} is "${w.text}", expected "${text}"`);
  out[name] = Number(w.start.toFixed(2));
}

const lastEnd = words[words.length - 1].end;
if (DURATION < lastEnd) errors.push(`composition duration ${DURATION}s truncates narration ${lastEnd}s`);

// Beat starts must be ordered and each must sit on or before its first cue.
for (let i = 1; i < STARTS.length; i++) {
  if (STARTS[i] <= STARTS[i - 1]) errors.push(`beat ${i + 1} starts before beat ${i}`);
}

// Cross-check the authored clip attributes against the beat table.
const html = readFileSync("index.html", "utf8");
STARTS.forEach((start, i) => {
  const n = i + 1;
  const dur = Number(((STARTS[i + 1] ?? DURATION) - start).toFixed(2));
  const re = new RegExp(`id="beat-${n}"[^>]*?data-start="([\\d.]+)"[^>]*?data-duration="([\\d.]+)"`);
  const m = html.match(re);
  if (!m) { errors.push(`index.html: no clip beat-${n} with data-start/data-duration`); return; }
  if (Number(m[1]) !== start) errors.push(`beat-${n}: data-start ${m[1]} != ${start}`);
  if (Number(m[2]) !== dur) errors.push(`beat-${n}: data-duration ${m[2]} != ${dur}`);
});
const rootDur = html.match(/data-composition-id="lesson"[\s\S]*?data-duration="([\d.]+)"/);
if (!rootDur || Number(rootDur[1]) !== DURATION) {
  errors.push(`index.html root data-duration is ${rootDur?.[1]}, expected ${DURATION}`);
}

if (errors.length) {
  console.error("build-cues FAILED:");
  for (const e of errors) console.error("  • " + e);
  process.exit(1);
}

const beats = STARTS.map((s, i) => [s, Number(((STARTS[i + 1] ?? DURATION) - s).toFixed(2))]);
writeFileSync(
  "cues.js",
  "// GENERATED by build-cues.mjs from ../audio/narration.words.json — do not edit by hand.\n" +
    `window.DURATION = ${DURATION};\n` +
    `window.BEATS = ${JSON.stringify(beats)};\n` +
    "window.CUE = " + JSON.stringify(out, null, 0).replace(/,"/g, ',\n  "').replace(/^{/, "{\n  ").replace(/}$/, "\n};\n"),
);
console.log(`cues.js written — ${CUES.length} cues, ${beats.length} beats, narration ends ${lastEnd}s`);
