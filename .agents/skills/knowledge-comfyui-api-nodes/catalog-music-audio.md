# API Online — Música, Áudio e 3D

## Áudio/3D
- **`ElevenLabs*`** — TTS/STT/SFX/clone de voz (**não** música).
- **`Meshy*`/`Tencent*`** — 3D.

## Música (text-to-music)

Nós **partner clicáveis** de música:

- 🏆 **`SoniloTextToMusic`** — Sonilo, 0,53/seg — **único servido pelo comfy.org** (confirmado na tabela de preços + smoke; comercial só no tier pago, **sem cláusula de sobrevivência** → licença fraca; treino licenciado Shutterstock = baixo risco).
- ✅ **`ByteDanceSeedAudio`** — Seed Audio 1.0, ~45/min, licença não verificada.
- ⛔ **`StabilityTextToAudio`** — Stable Audio: existe no código e a ToS hospedada §4.a **seria** limpa, MAS **o comfy.org NÃO serve o endpoint** → `API Error: Not Found` **404**; NÃO está na tabela de preços.
- ⛔ `Replicate meta/musicgen` (`comfyui-replicate`) = **CC-BY-NC NÃO-comercial**.

## ACE-Step (recomendado para direito comercial LIMPO)
- **Por script (fal):** `fal-ai/ace-step` → `audio.url` WAV.
- **Por script (Replicate):** `fishaudio/ace-step-1.5`, ~US$0,095/faixa.
- **Local (core, sem custom node):** `EmptyAceStepLatentAudio`→`TextEncodeAceStepAudio`→`KSampler` euler/simple/50/cfg5 + `ModelSamplingSD3` shift 5→`VAEDecodeAudio`→`SaveAudio`; checkpoint `ace_step_v1_3.5b.safetensors`, ~8GB VRAM.
- Instrumental = `lyrics` `[inst]`/`[instrumental]`.

## Licenciamento (é o que decide o provedor)
- **ACE-Step 1.5=MIT / v1=Apache-2.0** → comercial perpétuo/irrevogável.
- No **Replicate** a ToS **dá posse do output e sobrevive ao cancelamento** (§5+§9.5) → melhor para vender "para sempre".
- 🔴 **Suno/Udio** = em litígio (Sony/UMG/Warner).
- ⛔ **Mubert/Beatoven** = direito atrelado à assinatura ativa.
- ⚠️ **créditos comfy.org NÃO dão direito por si**: a ToS do comfy.org define "Output" só como conteúdo **visual** → áudio de partner é regido pela ToS do **provedor**.

## ⚠️ Valide na tabela de preços
O nó existir no `/object_info` ≠ o endpoint estar no ar (Stable Audio dá 404).

## Formato para loop
**WAV/FLAC/OGG, nunca MP3** (padding de encoder quebra o loop).

## Referências
- Template Sonilo: `api_sonilo_t2m.json`
- Bundle: `workflows-api/text-to-music-api/`
- Licenciamento completo → `docs/` (pesquisa de música)
