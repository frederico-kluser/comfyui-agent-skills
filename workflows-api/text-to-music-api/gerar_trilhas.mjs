#!/usr/bin/env node
// gerar_trilhas.mjs — gera trilhas instrumentais/ambient em LOTE por API de nuvem (ACE-Step), sem GPU local.
// ZERO dependencias npm: usa so o `fetch` nativo do Node 18+ (nada de node_modules — nao polui a sidebar do ComfyUI).
//
// Modelo: ACE-Step (licenca permissiva — v1 3.5B Apache-2.0 / 1.5 MIT). O modelo NAO restringe o audio gerado;
//   o direito comercial vem da ToS do HOST (ver README / API_REFERENCE).
//   --provider replicate -> fishaudio/ace-step-1.5 (MIT). ToS Replicate da POSSE + SOBREVIVE ao cancelamento (§5/§9.5).
//   --provider fal       -> fal-ai/ace-step (v1 Apache-2.0). Schema confirmado, devolve WAV. (padrao)
//
// Chaves (do AMBIENTE — nunca commitadas):  export FAL_KEY=...   |   export REPLICATE_API_TOKEN=r8_...
//
// Uso:
//   node gerar_trilhas.mjs                                   # 1 faixa de cada preset, no fal
//   node gerar_trilhas.mjs --provider replicate --preset all --count 3
//   node gerar_trilhas.mjs --preset perseguicao --count 10 --duration 90 --out ./trilhas

import fs from "node:fs/promises";
import path from "node:path";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function parseArgs(argv) {
  const a = { provider: "fal", preset: "all", count: 1, duration: null, steps: null, out: "./output" };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--provider") a.provider = argv[++i];
    else if (k === "--preset") a.preset = argv[++i];
    else if (k === "--count") a.count = parseInt(argv[++i], 10);
    else if (k === "--duration") a.duration = parseFloat(argv[++i]);
    else if (k === "--steps") a.steps = parseInt(argv[++i], 10);
    else if (k === "--out") a.out = argv[++i];
    else if (k === "-h" || k === "--help") a.help = true;
  }
  return a;
}

function seedAleatorio() {
  return Math.floor((Date.now() % 1_000_000) * Math.random());
}

// ---------- fal: fila REST (submit -> poll -> result) ----------
async function gerarFal(preset, { duration, steps }) {
  const key = process.env.FAL_KEY;
  if (!key) throw new Error("Defina FAL_KEY no ambiente (source ~/ComfyUI/secrets.env).");
  const seed = seedAleatorio();
  const input = { tags: preset.tags, lyrics: "[inst]", duration: duration ?? 60, seed };
  if (steps) input.number_of_steps = steps;
  const H = { Authorization: `Key ${key}`, "Content-Type": "application/json" };

  let r = await fetch("https://queue.fal.run/fal-ai/ace-step", { method: "POST", headers: H, body: JSON.stringify(input) });
  if (!r.ok) throw new Error(`fal submit ${r.status}: ${(await r.text()).slice(0, 200)}`);
  const sub = await r.json();
  if (sub?.audio?.url) return { url: sub.audio.url, seed };            // caso responda sincrono
  const statusUrl = sub.status_url, responseUrl = sub.response_url;
  if (!statusUrl || !responseUrl) throw new Error("fal: resposta sem status/response_url: " + JSON.stringify(sub).slice(0, 200));

  for (let i = 0; i < 150; i++) {
    await sleep(2000);
    const s = await (await fetch(statusUrl, { headers: H })).json();
    if (s.status === "COMPLETED") break;
    if (s.status === "FAILED" || s.status === "ERROR") throw new Error("fal FAILED: " + JSON.stringify(s).slice(0, 200));
  }
  const out = await (await fetch(responseUrl, { headers: H })).json();
  const url = out?.audio?.url ?? out?.audio_url;
  if (!url) throw new Error("fal: sem audio na resposta: " + JSON.stringify(out).slice(0, 200));
  return { url, seed };
}

// ---------- replicate: prediction com Prefer: wait ----------
async function gerarReplicate(preset, { duration, steps }) {
  const key = process.env.REPLICATE_API_TOKEN;
  if (!key) throw new Error("Defina REPLICATE_API_TOKEN no ambiente (r8_...).");
  const seed = seedAleatorio();
  const input = { prompt: preset.tags, lyrics: "[instrumental]", instrumental: true, duration: duration ?? 60, seed };
  if (steps) input.infer_step = steps;
  const H = { Authorization: `Bearer ${key}`, "Content-Type": "application/json", Prefer: "wait" };

  let r = await fetch("https://api.replicate.com/v1/models/fishaudio/ace-step-1.5/predictions", {
    method: "POST", headers: H, body: JSON.stringify({ input }),
  });
  if (!r.ok) throw new Error(`replicate ${r.status}: ${(await r.text()).slice(0, 200)}`);
  let p = await r.json();
  while (!["succeeded", "failed", "canceled"].includes(p.status)) {
    await sleep(2000);
    p = await (await fetch(p.urls.get, { headers: { Authorization: `Bearer ${key}` } })).json();
  }
  if (p.status !== "succeeded") throw new Error("replicate " + p.status + ": " + JSON.stringify(p.error || "").slice(0, 200));
  let url = Array.isArray(p.output) ? p.output[0] : p.output;
  if (url && typeof url === "object") url = url.url ?? String(url);
  url = String(url);
  if (!url.startsWith("http")) throw new Error("replicate: output nao-URL: " + url.slice(0, 200));
  return { url, seed };
}

const PROVEDORES = { fal: gerarFal, replicate: gerarReplicate };

async function baixarWav(url, destino) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`download falhou (${resp.status}) ${url}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  await fs.writeFile(destino, buf);
  return buf.length;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log("uso: node gerar_trilhas.mjs [--provider fal|replicate] [--preset <id>|all] [--count N] [--duration S] [--steps N] [--out DIR]");
    return;
  }
  const gerar = PROVEDORES[args.provider];
  if (!gerar) { console.error(`Provider invalido: ${args.provider} (use fal ou replicate)`); process.exit(1); }

  const { default: cfg } = await import(new URL("./presets.mjs", import.meta.url));
  let presets = cfg.presets;
  if (args.preset !== "all") {
    presets = presets.filter((p) => p.id === args.preset);
    if (!presets.length) { console.error(`Preset '${args.preset}' nao existe. Ha: ${cfg.presets.map((p) => p.id).join(", ")}`); process.exit(1); }
  }

  await fs.mkdir(args.out, { recursive: true });
  const total = presets.length * args.count;
  console.log(`>> ${total} faixa(s) via ${args.provider} | duracao ${args.duration ?? cfg.defaults.duration ?? 60}s | saida ${args.out}\n`);

  let ok = 0, i = 0;
  for (const preset of presets) {
    for (let c = 0; c < args.count; c++) {
      i++;
      const rotulo = `[${i}/${total}] ${preset.id}`;
      try {
        process.stdout.write(`${rotulo}  gerando... `);
        const { url, seed } = await gerar(preset, { duration: args.duration ?? cfg.defaults.duration, steps: args.steps });
        const destino = path.join(args.out, `${preset.id}_${seed}.wav`);
        const bytes = await baixarWav(url, destino);
        console.log(`ok -> ${destino} (${(bytes / 1024).toFixed(0)} KB)`);
        ok++;
      } catch (e) {
        console.log(`FALHOU: ${e.message}`);
      }
    }
  }
  console.log(`\n>> concluido: ${ok}/${total} faixa(s) em ${args.out}`);
  console.log(">> loop perfeito: WAV nao tem padding de compressao. No Electron/Web Audio API use loopStart/loopEnd no AudioBufferSourceNode.");
}

main().catch((e) => { console.error(e); process.exit(1); });
