#!/usr/bin/env node
// gerar_trilhas.mjs — gera trilhas instrumentais/ambient em LOTE por API de nuvem (ACE-Step), sem GPU local.
//
// Modelo: ACE-Step (licenca permissiva — v1 3.5B Apache-2.0 / 1.5 MIT). O modelo NAO restringe o audio gerado;
//   o direito comercial vem da ToS do HOST. Por isso o provedor importa (ver README / API_REFERENCE).
//
//   --provider replicate  -> fishaudio/ace-step-1.5 (MIT). ToS do Replicate da POSSE do output e SOBREVIVE ao
//                            cancelamento (secoes 5 e 9.5). => maxima seguranca juridica para "vender para sempre".
//   --provider fal        -> fal-ai/ace-step (v1 Apache-2.0). Schema confirmado, devolve WAV, usa FAL_KEY (padrao
//                            do repo). ToS do host fal nao foi verificada nesta pesquisa; como o modelo e permissivo,
//                            o risco e baixo, mas para o requisito "vender para sempre" prefira replicate ou o local.
//
// Chaves (do AMBIENTE — nunca commitadas):
//   export REPLICATE_API_TOKEN=r8_...     (provider replicate)
//   export FAL_KEY=...                     (provider fal)  — pode vir de ~/ComfyUI/secrets.env
//
// Uso:
//   node gerar_trilhas.mjs                              # 1 faixa de cada preset, no fal
//   node gerar_trilhas.mjs --provider replicate         # idem, no Replicate (ToS mais limpa)
//   node gerar_trilhas.mjs --preset perseguicao --count 10   # 10 variacoes de um preset
//   node gerar_trilhas.mjs --preset all --count 3 --duration 90 --out ./trilhas
//
// Saida: arquivos .wav em --out (default ./output), 1 por faixa, nome <preset>_<seed>.wav — prontos para loop.

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));

// ---------- args ----------
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
    else if (k === "-h" || k === "--help") { a.help = true; }
  }
  return a;
}

function seedAleatorio() {
  // faixa inedita a cada chamada (sem Math.random travado; usa o relogio + ruido)
  return Math.floor((Date.now() % 1_000_000) * Math.random());
}

// ---------- provedores ----------
async function gerarFal(preset, { duration, steps }) {
  let fal;
  try { ({ fal } = await import("@fal-ai/client")); }
  catch { throw new Error("Falta a lib: rode  npm i @fal-ai/client  (ou  bash setup.sh)"); }
  if (!process.env.FAL_KEY) throw new Error("Defina FAL_KEY no ambiente (ex.: export FAL_KEY=... ou ~/ComfyUI/secrets.env).");
  fal.config({ credentials: process.env.FAL_KEY });

  const seed = seedAleatorio();
  const input = {
    tags: preset.tags,
    lyrics: "[inst]",                 // instrumental puro
    duration: duration ?? 60,
    seed,
  };
  if (steps) input.number_of_steps = steps;
  const r = await fal.subscribe("fal-ai/ace-step", { input, logs: false });
  const data = r?.data ?? r;
  const url = data?.audio?.url ?? data?.audio_url ?? data?.url;
  if (!url) throw new Error("fal nao devolveu URL de audio: " + JSON.stringify(data).slice(0, 300));
  return { url, seed };
}

async function gerarReplicate(preset, { duration, steps }) {
  let Replicate;
  try { Replicate = (await import("replicate")).default; }
  catch { throw new Error("Falta a lib: rode  npm i replicate  (ou  bash setup.sh)"); }
  if (!process.env.REPLICATE_API_TOKEN) throw new Error("Defina REPLICATE_API_TOKEN no ambiente (r8_...).");
  const replicate = new Replicate({ auth: process.env.REPLICATE_API_TOKEN });

  const seed = seedAleatorio();
  const input = {
    prompt: preset.tags,              // no Replicate o estilo vai em 'prompt'
    lyrics: "[instrumental]",
    instrumental: true,               // forca instrumental independentemente de lyrics
    duration: duration ?? 60,
    seed,
  };
  if (steps) input.infer_step = steps;
  const out = await replicate.run("fishaudio/ace-step-1.5", { input });
  // o client novo devolve FileOutput (com .url()); versoes antigas, string ou array
  let url = out;
  if (Array.isArray(out)) url = out[0];
  if (url && typeof url === "object") url = typeof url.url === "function" ? url.url() : (url.url ?? String(url));
  url = String(url);
  if (!url.startsWith("http")) throw new Error("Replicate nao devolveu URL de audio: " + url.slice(0, 300));
  return { url, seed };
}

const PROVEDORES = { fal: gerarFal, replicate: gerarReplicate };

// ---------- download ----------
async function baixarWav(url, destino) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`download falhou (${resp.status}) ${url}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  await fs.writeFile(destino, buf);
  return buf.length;
}

// ---------- main ----------
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
  console.log(">> loop perfeito: WAV nao tem padding de compressao (ver README). No Electron/Web Audio API, use loopStart/loopEnd no AudioBufferSourceNode.");
}

main().catch((e) => { console.error(e); process.exit(1); });
