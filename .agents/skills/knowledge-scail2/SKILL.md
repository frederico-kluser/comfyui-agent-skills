---
name: knowledge-scail2
description: >-
  Conhecimento operacional do SCAIL-2 (animação de personagem end-to-end sobre Wan 2.1 14B):
  arquivos e paths exatos de modelo, variantes e VRAM (fp8/GGUF), a máscara colorida obrigatória,
  modos Animation/Replacement, parâmetros do sampler (euler/simple, 6–8 steps, cfg 1, shift 1,
  81 frames) e gotchas. Use ao gerar/animar com SCAIL-2, escolher quantização ou debugar
  máscara/qualidade — mesmo sem citar a skill. Não cobre infra/preço de GPU (ver knowledge-runpod-infra).
metadata:
  version: 0.1.0
  type: knowledge
---
# SCAIL-2 — Geração e Animação de Personagem

SCAIL-2 (zai-org, jun/2026; backbone Wan 2.1-14B-I2V) anima uma imagem de referência a partir de um
vídeo-condutor **sem mapas de esqueleto** — suporta single/multi-personagem, substituição e motion de
animais. Roda no ComfyUI (caminho nativo Comfy-Org ou wrapper Kijai).

## Quando usar
Pedidos de "animar personagem/pessoa", "transferir movimento", "substituir personagem", "SCAIL-2",
problemas de máscara/dedos/rosto, ou escolha de quantização para caber na VRAM.

## Arquivos de modelo (paths exatos no ComfyUI)
```
ComfyUI/models/
├── diffusion_models/  wan2.1_14B_SCAIL_2_fp8_scaled.safetensors   (17.7 GB; fp16/mxfp8 também)
│   └── unet/          SCAIL-2-Q4_K_M.gguf                          (caminho GGUF; Unet Loader do city96)
├── text_encoders/     umt5_xxl_fp8_e4m3fn_scaled.safetensors
├── vae/               wan_2.1_vae.safetensors
├── clip_vision/       clip_vision_h.safetensors
├── sam/               sam3.1_multiplex_fp16.safetensors            (alguns workflows esperam em checkpoints/)
└── loras/             Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors
                       wan2.1_SCAIL_2_DPO_lora_bf16.safetensors     (opcional: corrige mãos/rostos)
```
Repos: `Comfy-Org/SCAIL-2` (fp8/fp16/mxfp8 + DPO lora), `realrebelai/SCAIL-2_GGUF` (quantizações),
componentes Wan em `Comfy-Org/Wan_2.1_ComfyUI_repackaged`. Manifesto completo de download → `knowledge-runpod-provisioning`.

## Escolha de quantização (VRAM)
- ≤12GB → GGUF Q4_K_M (10.9 GB, "daily driver") ou Q5_K_M.
- 16GB → Q8_0 (17.7 GB, mais próximo do fp16) ou fp8.
- 24GB (RTX 4090) → fp8_scaled. 32GB+ (RTX 5090)/cloud → fp16 para máxima qualidade.
- Q8_0 ≈ fp16; fp8 preserva surpreendentemente bem; Q4/Q3 adicionam artefatos (use o DPO lora p/ mãos/rosto).
- ⚠️ Rótulos de VRAM de algumas fontes parecem invertidos (o arquivo fp8 tem só ~17.7 GB). Trate fp8/mxfp8
  como **menor** VRAM e fp16 como **maior**.

## Máscara colorida (input crítico)
Obrigatória **mesmo em Animation Mode single-character** — não a remova do workflow. Por quê: ela codifica
quem é quem. Convenção de cor: **preto** = fundo não deve aparecer; **branco** = fundo deve aparecer; **cor** =
correspondência entre uma região do personagem e o movimento condutor. Gerada via nós SAM 3.1 (`SAM3_VideoTrack`)
+ `Create SCAIL-2 Colored Mask`. **Replacement Mode**: `--replace_flag` + máscara da região a substituir.

## Parâmetros (ComfyUI, consenso da comunidade)
- sampler **euler**, scheduler **simple**, **6 steps** (CLI oficial usa 8 — teste os dois), **cfg 1.0**
  (a guidance vem da LoRA destilada via `SamplerCustom`), **shift 1**.
- Frames: padrão/máx **81** (~5s); saída 30 fps no VHS — mas o modelo roda a **16 fps**, então gere a 16 e
  **interpole** (RIFE/FILM); não suba o `force_rate`.
- Resolução: largura/altura **divisíveis por 32** (832×480 base 480p; 704×1280 vertical). Vídeo longo →
  Context Windows (context_length 81, overlap 16) ou o nó `SCAIL Auto Extend`.
- Config CLI oficial (`generate.py` + LightX2V): `--sample_steps 8 --sample_shift 1 --sample_guide_scale 1.0`, lora_alpha 1.0.

## Prompts
Treinado com prompts **longos e detalhados** que descrevem o vídeo gerado em si. Prompts curtos/vazios
funcionam, mas pioram o resultado. Dica oficial: use um VLM (ex.: Gemini) para ler a imagem de referência + o
movimento e gerar o prompt.

## Gotchas
- `WEIGHT NOT MERGED warning on patch_embedding` é **inofensivo** — o ComfyUI monta um patch embedding de 36
  canais e concatena os canais de máscara em runtime; o peso armazenado de 20 canais é esperado. A geração segue normal.
- `Create SCAIL-2 Colored Mask` é **core do ComfyUI** (não custom). Vermelho/"missing" = ComfyUI não está
  nightly/master → `git pull` em `$COMFY` + reiniciar.
- Em certos inputs, Animation Mode pode **colapsar** em Replacement-Mode; a qualidade degrada em movimento
  complexo; a ancoragem do frame de referência degrada em vídeos longos.
- SCAIL-2 adiciona overhead de SAM 3.1 + CLIP Vision → é um pouco mais lento que Wan 2.1 puro.

## Referências (nível 3, sob demanda)
- `docs/SCAIL-2.md` — guia completo (arquitetura, comparações, workflows da comunidade).
- Cadeia: montar o grafo → `knowledge-comfyui-workflows`; baixar os modelos → `knowledge-runpod-provisioning`.

## Evolução
Ao descobrir um parâmetro melhor, um path/arquivo novo, um gotcha ou uma correção do usuário: append em
`LEARNINGS.md` (data + fonte: usuário > inferência) e, se virar padrão estável, destile no corpo acima
(incremente `version`). Só persista o que NÃO é óbvio nem volátil. Mudança = diff git para revisão humana.
