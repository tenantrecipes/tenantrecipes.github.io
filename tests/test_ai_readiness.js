#!/usr/bin/env node
/* Offline logic tests for the Enterprise AI readiness check.
 *   node tests/test_ai_readiness.js */
"use strict";
const assert = require("assert");
const path = require("path");
const AIR = require(path.join(__dirname, "..", "assets", "ai-readiness.js"));

let n = 0;
function t(name, fn) {
  return Promise.resolve().then(fn).then(() => { n++; }, (e) => {
    console.error("FAIL " + name + "\n  " + (e && e.stack || e));
    process.exitCode = 1;
  });
}

const gapsAnswers = {
  vendors: { copilot: true, chatgpt: true },
  consumer: "unchecked",
  sensitivity: "unknown",
  prohibited: "no",
  pattern: "rag",
  oversharing: "no",
  labels: "unknown",
  sso: "none",
  mfa: "password",
  ca: "no",
  dlp: "no",
  browser: "no",
  logs: "unknown",
  retention: "no",
  guidance: "no",
  literacy: "no",
  inventory: "no",
  owners: "no",
  decision: "no",
  contract: "no"
};

const solidAnswers = {
  vendors: { copilot: true },
  consumer: "no",
  sensitivity: "internal",
  prohibited: "yes",
  pattern: "chat",
  oversharing: "na",
  labels: "yes",
  sso: "all",
  mfa: "phish",
  ca: "yes",
  dlp: "yes",
  browser: "yes",
  logs: "yes",
  retention: "yes",
  guidance: "yes",
  literacy: "yes",
  inventory: "yes",
  owners: "yes",
  decision: "yes",
  contract: "yes"
};

const tests = [];

tests.push(t("schema: every section has required questions with unique option ids", () => {
  const seenQ = new Set();
  assert.strictEqual(AIR.SECTIONS.length, 8);
  for (const s of AIR.SECTIONS) {
    assert.ok(s.id && s.title && s.questions.length);
    for (const q of s.questions) {
      assert.ok(!seenQ.has(q.id), "duplicate question id " + q.id);
      seenQ.add(q.id);
      assert.ok(q.type === "single" || q.type === "multi");
      const ids = q.options.map((o) => o.id);
      assert.strictEqual(ids.length, new Set(ids).size, q.id);
      assert.ok(ids.length >= 2, q.id);
    }
  }
}));

tests.push(t("questionError requires a choice", () => {
  const q = AIR.SECTIONS[0].questions[0];
  assert.ok(AIR.questionError(q, { vendors: {} }));
  assert.ok(!AIR.questionError(q, { vendors: { copilot: true } }));
  assert.ok(AIR.questionError(q, { vendors: { other: true, otherText: "  " } }));
  assert.ok(!AIR.questionError(q, { vendors: { other: true, otherText: "Self-hosted Llama" } }));
}));

tests.push(t("exclusive 'none yet' clears other vendor ticks", () => {
  const q = AIR.SECTIONS[0].questions[0];
  const answers = { vendors: { copilot: true, chatgpt: true } };
  AIR.applyExclusive(q, answers, "none", true);
  answers.vendors.none = true;
  assert.strictEqual(answers.vendors.copilot, false);
  assert.strictEqual(answers.vendors.chatgpt, false);
  AIR.applyExclusive(q, answers, "claude", true);
  answers.vendors.claude = true;
  assert.strictEqual(answers.vendors.none, false);
}));

tests.push(t("gaps profile produces Foundation gaps and P1 items for inventory, SSO and oversharing", () => {
  const r = AIR.generate(gapsAnswers);
  assert.strictEqual(r.snapshot.level, "gaps");
  const texts = r.groups.flatMap((g) => g.items.map((i) => i.text)).join("\n");
  assert.ok(/inventory/i.test(texts));
  assert.ok(/SSO|identity provider/i.test(texts));
  assert.ok(/oversharing/i.test(texts));
  assert.ok(/consumer or unmanaged|Discover which AI/i.test(texts));
  assert.ok(r.groups.some((g) => g.id === "first" && g.items.length >= 4));
  assert.ok(r.markdown.includes("## Do first"));
  assert.ok(r.markdown.includes("[ ]"));
  assert.ok(r.related.some((l) => /inventory/i.test(l.label)));
}));

tests.push(t("solid chat-only Copilot profile is 'scale' and still reminds about Copilot-specific controls", () => {
  const r = AIR.generate(solidAnswers);
  assert.strictEqual(r.snapshot.level, "scale");
  const texts = r.groups.flatMap((g) => g.items.map((i) => i.text)).join("\n");
  assert.ok(/Copilot-specific|readiness/i.test(texts));
  assert.ok(r.groups.some((g) => g.id === "verify" && g.items.length >= 3));
  assert.ok(!/Stop work use of consumer/i.test(texts));
}));

tests.push(t("agent + special-category data is never 'scale' and asks for action scoping and legal review", () => {
  const a = Object.assign({}, solidAnswers, { pattern: "agent", oversharing: "yes", sensitivity: "special", contract: "yes" });
  const r = AIR.generate(a);
  assert.notStrictEqual(r.snapshot.level, "scale");
  const texts = r.groups.flatMap((g) => g.items.map((i) => i.text)).join("\n");
  assert.ok(/every action an agent may take/i.test(texts));
  assert.ok(/DPO or counsel|special-category/i.test(texts));
}));

tests.push(t("planning-only path points at the approval runbook and does not invent Copilot-only DLP steps as first action", () => {
  const a = Object.assign({}, gapsAnswers, { vendors: { none: true }, pattern: "chat", oversharing: "na" });
  const r = AIR.generate(a);
  const first = (r.groups.find((g) => g.id === "first") || { items: [] }).items.map((i) => i.text).join("\n");
  assert.ok(!/Copilot location/i.test(first));
  const all = r.groups.flatMap((g) => g.items.map((i) => i.text)).join("\n");
  assert.ok(/approval runbook/i.test(all));
}));

tests.push(t("markdown contains editorial boxes and no invented personal experience", () => {
  const md = AIR.toMarkdown(solidAnswers);
  assert.ok(md.includes("## Why we recommend this"));
  assert.ok(md.includes("## When to choose something else"));
  assert.ok(md.includes("## Not verified"));
  assert.ok(/planning aid, not a certification/i.test(md));
  assert.ok(!/in our tenant|we implemented|when I ran/i.test(md));
}));

tests.push(t("third-party tools get a plan-specific DLP/audit reminder", () => {
  const a = Object.assign({}, solidAnswers, { vendors: { claude: true, grok: true } });
  const r = AIR.generate(a);
  const texts = r.groups.flatMap((g) => g.items.map((i) => i.text)).join("\n");
  assert.ok(/non-Microsoft|exact plan/i.test(texts));
}));

Promise.all(tests).then(() => {
  if (!process.exitCode) console.log("OK " + n + " tests");
});
