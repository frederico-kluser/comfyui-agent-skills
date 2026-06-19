# Guia Completo e Detalhado do RunPod.io para ComfyUI e Geração de Vídeo/Imagem com IA (Atualizado: Junho de 2026)

## TL;DR
- **Para o seu fluxo de comerciais (SCAIL-2, Wan 2.1/2.2 14B, Flux):** o melhor custo-benefício é uma **RTX 5090 (32GB) a US$0,99/h** ou **RTX 4090 (24GB) a US$0,69/h** com modelos quantizados (fp8/GGUF) para 480p; para 720p estável com os modelos 14B em precisão total use **A100 80GB (US$1,39–1,49/h)** ou **H100 (US$2,89/h)**. Sempre conecte um **Network Volume** (US$0,07/GB/mês) para não rebaixar dezenas de GB de modelos a cada pod.
- **O atalho definitivo de setup** é um **provisioning script** (variável de ambiente `PROVISIONING_SCRIPT` no template AI-Dock/ComfyUI) que aponta para um arquivo `.sh` em um GitHub Gist; ele instala custom nodes (WanVideoWrapper, VideoHelperSuite, GGUF, KJNodes, rgthree, Frame-Interpolation) e baixa os modelos automaticamente no boot. Como alternativa pronta, o template **HearmemanAI "One Click ComfyUI - Wan 2.1/2.2 (CUDA 12.8)"** baixa os modelos via variáveis de ambiente.
- **Regra de ouro de custo:** pague GPU só enquanto gera. Pré-baixe modelos no Network Volume, **pare/termine pods** quando não usar, use **Community Cloud/Spot** para testes e **Serverless** (escala a zero) quando for automatizar geração de comerciais via API.

## Key Findings

1. **A RunPod cobra por segundo** e divide a oferta em **Pods** (GPU dedicada que você controla), **Serverless** (endpoints API que escalam a zero) e **Clusters** (multi-nó). Preços de Pods on-demand (Secure Cloud, junho/2026): RTX 4090 US$0,69/h, RTX 5090 US$0,99/h, A100 80GB US$1,39–1,49/h, H100 PCIe US$2,89/h, H200 US$4,39/h, B200 US$5,89/h.
2. **VRAM define tudo.** Os modelos 14B (Wan 2.1/2.2, SCAIL-2) precisam de ~54–80GB em precisão total a 720p, mas caem para ~16–24GB com fp8 e para 6–17GB com GGUF — o que viabiliza RTX 4090/5090. Flux dev cabe em 24GB (fp8) ou menos com GGUF.
3. **Network Volume é essencial** e só existe na Secure Cloud. Ele preserva modelos e saídas entre pods, derrubando o tempo de inicialização de minutos para segundos.
4. **CUDA 12.8** é obrigatório para Blackwell (RTX 5090, B200, RTX PRO 6000). Use o template "ComfyUI Blackwell Edition" da RunPod ou templates da comunidade marcados como CUDA 12.8.
5. **Provisioning scripts** são a forma reproduzível de configurar tudo automaticamente; HuggingFace token (`HF_TOKEN`) e CivitAI token (`CIVITAI_TOKEN`) permitem baixar modelos gated/privados.
6. A RunPod alcançou **SOC 2 Type II em outubro de 2025** para a Secure Cloud, além de **SOC 3, HIPAA e GDPR** (verificáveis em trust.runpod.io), relevante se você lida com dados de clientes em comerciais.

## Details

### 1. Visão geral do RunPod.io e a interface 2026

**O que é.** A RunPod é uma cloud de GPUs sob demanda focada em IA, fundada por **Zhen Lu e Pardeep Singh**, que lançaram o beta via post no Reddit no início de 2022 (TechCrunch, 16/01/2026). Recebeu um seed de US$20M co-liderado por Intel Capital e Dell Technologies Capital, com anjos como Nat Friedman e Julien Chaumond. Cobra **por segundo** (Serverless) ou **por minuto/segundo** (Pods), sem taxa de egress (transferência de saída). Em 20/01/2026 a empresa reportou ter ultrapassado **US$120M de ARR e mais de 500.000 desenvolvedores em 31 regiões**, com signups +155% YoY e clientes como OpenAI, Replit, Cursor e Zillow. O console fica em `console.runpod.io` e a documentação em `docs.runpod.io`.

**Estrutura do console (2026).** A navegação à esquerda traz:
- **Pods** — criar e gerenciar GPUs dedicadas (`console.runpod.io/deploy`).
- **Serverless** — endpoints API que escalam a zero (`console.runpod.io/serverless`).
- **Storage** — Network Volumes (`console.runpod.io/user/storage`).
- **Templates** — imagens Docker pré-configuradas.
- **Hub** — repositórios prontos para deploy (ComfyUI, etc.) e Public Endpoints.
- **Billing** — créditos e histórico.
- **Clusters** — multi-nó (até 64 GPUs).

**Pods vs Serverless.**
- **Pods (GPU Cloud):** container com GPU que fica ligado (e cobrando) até você parar/terminar. Ideal para trabalho interativo no ComfyUI — gerar lotes de vídeo, iterar em workflows, instalar nodes. Acesso via HTTP (porta 8188), JupyterLab, web terminal ou SSH.
- **Serverless:** roda inferência atrás de uma API e escala workers de zero a muitos conforme a demanda; cobra por segundo de compute ativo. Ideal para produção/automação. Com **FlashBoot**, per RunPod, "95% of our cold-starts are less than 2.3 seconds, and 90% are less than 2s" — com cold-starts observados tão baixos quanto 500ms.

**Secure Cloud vs Community Cloud.**
- **Secure Cloud:** data centers Tier 3/4 geridos por parceiros da RunPod; alta confiabilidade, persistência e suporte a Network Volumes. Mais caro.
- **Community Cloud:** GPUs de hosts terceiros vetados; 10–30% mais barato, mas disponibilidade/confiabilidade variam e **não suporta Network Volumes**. Importante: a RunPod **não está mais aceitando novos hosts para Community Cloud**, embora os recursos existentes permaneçam disponíveis.
- Regra prática: prototipe na Community Cloud, produza na Secure Cloud. Para o seu caso (modelos grandes + Network Volume), você ficará majoritariamente na **Secure Cloud**.

**On-Demand vs Spot/Interruptible.**
- **On-Demand:** não é interrompido; disponibilidade garantida.
- **Spot/Interruptible:** 50–70% mais barato, mas pode ser recuperado quando a demanda sobe, com aviso curto (SIGTERM ~5 segundos). Bom para jobs toleráveis a interrupção que salvam checkpoints — não para uma sessão interativa de ComfyUI que você quer manter.
- **Savings Plans:** comprometimento de 3 ou 6 meses para desconto (ex.: H100 SXM de US$3,49 → US$2,79/h, ~20%).

**Billing.** Conta gratuita; você adiciona crédito por cartão ou cripto e paga por uso. Há um limite default de gasto de US$80/hora para novas contas (anti-fraude; pode ser elevado via suporte). Novas contas recebem um bônus aleatório de **US$5–US$500 após o primeiro depósito de US$10**, mas, per runpodreferral.com, "About 96% of users get $10 or less, with most receiving $5" — então não conte com um bônus alto. O **RunPod Startup Program** (Starter Tier) dá US$1.000 em créditos e oferece "up to 1,000 free H100 compute hours, 1,000,000 serverless requests, and 750 multi-node H100 hours"; o Growth Tier dá +US$25K ao depositar US$50K (total US$75K, contrato de 12 meses), e venture backing não é obrigatório.

### 2. Catálogo de GPUs (junho/2026) e compatibilidade por modelo

**Tabela de preços On-Demand (Secure Cloud), com VRAM** — fonte: página oficial de pricing da RunPod:

| GPU | VRAM | RAM | vCPU | On-Demand (Secure) |
|---|---|---|---|---|
| RTX A5000 | 24 GB | 25 GB | 9 | US$0,27/h |
| L4 | 24 GB | 50 GB | 12 | US$0,39/h |
| A40 | 48 GB | 50 GB | 9 | US$0,44/h |
| RTX 3090 | 24 GB | 125 GB | 16 | US$0,46/h |
| RTX A6000 | 48 GB | 50 GB | 9 | US$0,49/h |
| RTX 4090 | 24 GB | 41 GB | 6 | US$0,69/h |
| RTX 6000 Ada | 48 GB | 167 GB | 10 | US$0,77/h |
| L40S | 48 GB | 94 GB | 16 | US$0,86/h |
| L40 | 48 GB | 94 GB | 8 | US$0,99/h |
| RTX 5090 | 32 GB | 35 GB | 9 | US$0,99/h |
| A100 PCIe | 80 GB | 117 GB | 8 | US$1,39/h |
| A100 SXM | 80 GB | 125 GB | 16 | US$1,49/h |
| RTX PRO 6000 | 96 GB | 188 GB | 16 | US$2,09/h |
| H100 PCIe | 80 GB | 188 GB | 16 | US$2,89/h |
| H100 NVL | 94 GB | 94 GB | 16 | US$3,19/h |
| H100 SXM | 80 GB | 125 GB | 20 | US$3,29/h |
| H200 (SXM) | 141 GB | 276 GB | 24 | US$4,39/h |
| B200 | 180 GB | 283 GB | 28 | US$5,89/h |

Community Cloud costuma ser 10–30% mais barato quando disponível (ex.: RTX 4090 já visto perto de US$0,34/h; A100 80GB ~US$0,89–1,19/h), porém varia por região/oferta. A RunPod anuncia "36 tipos de GPU" e 30+ regiões; nem toda GPU está disponível em toda região a todo momento. Não há HGX B300 listada publicamente no pricing de junho/2026 (o topo de linha disponível é B200; H200 e RTX PRO 6000 cobrem o tier de altíssima VRAM).

**VRAM necessária e GPU recomendada por modelo:**

| Modelo | Precisão total | fp8 | GGUF | GPU recomendada (custo-benefício) |
|---|---|---|---|---|
| **SDXL (imagem)** | ~10–12 GB | — | — | RTX 4090 / L40 (sobra) |
| **Flux.1 dev** | ~24 GB (fp16) | ~12–16 GB | Q4 ~6–8 GB, Q8 ~12–13 GB | RTX 4090 24GB (fp8/Q8) |
| **Wan 2.2 TI2V-5B** | — | ~8–12 GB | — | RTX 4090 / 5090; cabe em 24GB a 720p |
| **Wan 2.1/2.2 14B (480p)** | ~54–65 GB | ~16–24 GB | 6–17 GB | RTX 4090/5090 (fp8/GGUF) |
| **Wan 2.1/2.2 14B (720p)** | ~65–80 GB | ~40–50 GB | — | A100 80GB / H100 80GB / H200 |
| **SCAIL-2 (Wan 2.1 14B)** | fp16 (ver caveat) | fp8_scaled / mxfp8 | Q2 ~6 GB → Q8 ~17,7 GB | RTX 4090/5090 (fp8/GGUF); A100/H100 p/ folga |

**SCAIL-2 — variantes e VRAM** (fonte: stablediffusiontutorials.com, 16/06/2026; HF realrebelai/SCAIL-2_GGUF):
- `wan2.1_14B_SCAIL_2_fp8_scaled.safetensors` — "minimum 32GB VRAM"
- `wan2.1_14B_SCAIL_2_fp16.safetensors` — "for minimum 16 GB VRAM"
- `wan2.1_14B_SCAIL_2_mxfp8.safetensors` — "for minimum 16 GB VRAMs"
- GGUF Q2_K (6,02 GB) → Q8_0 (17,7 GB, mais próximo do fp16). Q4_K_M (~10,9 GB) é o "daily driver" recomendado.
- ⚠️ **Atenção:** os rótulos de VRAM da fonte parecem trocados (é implausível fp16 pedir só 16GB e fp8 pedir 32GB). Trate fp8/mxfp8 como as opções de **menor** VRAM e o fp16 como a de **maior**. Para Blackwell (RTX 5090) prefira fp8_scaled/mxfp8; para 6–17GB use GGUF.
- Arquivos companheiros do SCAIL-2 (todos vão para pastas específicas): `umt5_xxl_fp8_e4m3fn_scaled` (text_encoders), `clip_vision_h` (clip_vision), `sam3.1_multiplex_fp16` (checkpoints), `Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64` + `wan2.1_SCAIL_2_DPO_lora_bf16` (loras), `wan_2.1_vae`/`Wan2_1_VAE_bf16` (vae). O SCAIL-2 gera até **81 frames** por passada; use o node "SCAIL Auto Extend" (Brobert-in-aus/scail-auto-extend) para vídeos mais longos. O node `SCAIL2ColoredMask` exige a versão **nightly/master** do ComfyUI.

**Tempos aproximados de geração (clipe ~5s):**
- **Wan 2.1 14B (full-step), benchmark InstaSD:** 480p — A5000 462s, A40 350s, RTX 4090 281s, L40 290s, A100 170s, H100 85s. 720p — A40 1083s, L40 859s, A100 523s, H100 284s; **RTX 4090 e A5000 não geram 720p no 14B em precisão**.
- **Wan 2.2 TI2V-5B:** ~4 min para 5s a 480p na RTX 4090; os 14B levam ~9 min para 5s a 720p (sem otimização).
- **RTX 5090** rende ~2x a RTX 4090 a 480p (~25 clipes de 5s/hora vs ~12).
- **SCAIL-2:** não há benchmark oficial publicado até junho/2026. Como o workflow usa a LoRA destilada **LightX2V a ~6–8 steps**, espere geração **bem mais rápida** que o Wan 2.1 full-step: na ordem de **1–3 min para ~5s a 480p numa RTX 4090/5090**, ainda mais rápido em A100/H100. (Estimativa; valide no seu pod.)

### 3. Como escolher a GPU correta (árvore de decisão)

- **Só imagem (SDXL/Flux), barato e rápido:** RTX 4090 (24GB, US$0,69/h). Flux dev em fp8/Q8 cabe folgado; gera imagem em ~10–18s.
- **Vídeo 480p rápido e barato (Wan/SCAIL-2 em fp8/GGUF):** RTX 5090 (32GB, US$0,99/h) é o melhor custo-benefício — mais VRAM que a 4090, ~2x a velocidade, e nativamente Blackwell/CUDA 12.8. RTX 4090 se quiser economizar mais.
- **Vídeo 720p estável com 14B em precisão (fp8/bf16):** A100 80GB (US$1,39–1,49/h) é o ponto doce; H100 (US$2,89/h+) se quiser ~2x mais velocidade (maior banda de memória).
- **Clipes longos (10s+), multi-personagem, 720p sem risco de OOM:** H200 141GB (US$4,39/h) — a única com folga ampla; sair de 5s→10s a 720p ultrapassa 80GB.
- **Produção/API que escala a zero:** Serverless (ver seção 8).

**Quando quantizar vs precisão total.** Use **fp8** quando quiser quase a mesma qualidade com ~20–40% menos VRAM (perda visível só em texturas finas). Use **GGUF (Q4–Q8)** para caber em GPUs menores (custa 10–30% mais tempo por dequantização). Use **bf16/fp16** só quando a GPU tem VRAM sobrando e você quer qualidade máxima de finalização.

**Estimar custo de um projeto.** Custo ≈ (tempo por clipe em horas) × (preço/h da GPU) × (nº de clipes, incluindo iterações) + storage. Exemplo: 50 clipes finais de 720p no Wan 14B, ~9 min cada na A100 (US$1,49/h) ≈ 50 × 0,15h × US$1,49 ≈ **US$11**; some as iterações a 480p (muito mais baratas). **Dica de maior alavancagem:** itere composição a 480p e só finalize a 720p — um clipe 480p custa ~2–3x menos que o mesmo a 720p.

### 4. Passo a passo de como lançar um Pod (interface 2026)

1. **Conta e crédito:** cadastre-se em runpod.io (email/Google/GitHub) e adicione crédito em Billing.
2. **Crie um Network Volume (faça isto primeiro):** Storage → New Network Volume. Escolha a **região** (de preferência onde há as GPUs que você usará — volumes são travados por região) e o tamanho (sugestão: 100–200GB para modelos de vídeo, que somam dezenas de GB). Custo ~US$0,07/GB/mês (US$0,05 acima de 1TB; tier high-performance US$0,14/GB/mês). Só funciona na **Secure Cloud**.
3. **Deploy do Pod:** Pods → Deploy. Selecione a GPU e a região (com o volume já selecionado na barra). Para Blackwell (RTX 5090/B200), filtre por **CUDA 12.8**.
4. **Escolha o template** (ver seção 5): ComfyUI oficial, ComfyUI Blackwell Edition, ou um da comunidade (HearmemanAI). Clique em "Change Template" para trocar.
5. **Configure o Pod:** Container Disk (efêmero, 20–50GB), Volume Disk/mount (o Network Volume monta em `/workspace`), portas expostas (HTTP 8188 do ComfyUI, 8888 JupyterLab, 8080 FileBrowser), e variáveis de ambiente (tokens, flags de download).
6. **Deploy On-Demand** (ou Spot). A inicialização pode levar de segundos a ~30 min na primeira vez (baixa imagem + copia ComfyUI para o volume).
7. **Conecte:** botão Connect → "Connect to HTTP Service [Port 8188]" abre o ComfyUI. Aguarde o log "All startup tasks have been completed" / a porta 8188 ficar "Ready" (verde). JupyterLab e web terminal também ficam no Connect.
8. **Pare/termine:**
   - **Stop (pausar):** desliga a GPU e para a cobrança de compute, mas o **Volume Disk continua cobrando (em dobro, ~US$0,20/GB/mês, quando o pod está parado)**. Pode falhar ao reiniciar se a GPU estiver esgotada na região.
   - **Terminate (terminar):** apaga o pod e o **container/volume disk efêmero** — você perde tudo que não estiver no Network Volume.
   - **Network Volume:** persiste independentemente; só é cobrado o storage.

**Container Disk vs Volume Disk vs Network Volume.** Container disk = efêmero, sumiu ao terminar. Volume disk = persiste enquanto o pod existe (cobra em dobro parado). Network Volume = persiste sempre, portável entre pods, e é onde você deve guardar **modelos e saídas**.

### 5. Pod Templates — configurações detalhadas

Um template é uma **imagem Docker** + configuração (container disk, mount path, portas expostas, variáveis de ambiente e start/docker command).

**Oficiais da RunPod:**
- **ComfyUI** (`runpod/comfyui`) — última build + CUDA 12.8; vem com ComfyUI-Manager, KJNodes, Civicomfy e ComfyUI-RunpodDirect. Para GPUs padrão (RTX 4090, L40, A100). O FileBrowser na porta 8080 usa login `admin / adminadmin12`.
- **ComfyUI Blackwell Edition** — para RTX 5090 e B200 (arquitetura Blackwell exige imagem dedicada).
- **PyTorch** (ex.: `runpod/pytorch:2.x-cuda12.8`) — base limpa para montar do zero.

**Comunidade (vídeo/IA):**
- **HearmemanAI "One Click ComfyUI - Wan 2.1 / Wan 2.2 (CUDA 12.8)"** — o mais completo para Wan: T2V, I2V, V2V, VACE e Wan Fun. Baixa modelos no primeiro boot conforme variáveis de ambiente. Suporta token CivitAI para LoRAs. **Exige CUDA 12.8.**
- **ComfyUI with Flux** (ValyrianTech) — Flux.1-dev pré-instalado + ComfyUI Manager; tem variante "without Flux" para deploy rápido reusando o Network Volume. Já inclui workflows Wan2.1/2.2, Qwen-image-edit e VibeVoice nas versões recentes (CUDA 12.8 para RTX 5090/PRO 6000).
- **AI-Dock ComfyUI** (`ghcr.io/ai-dock/comfyui`) — base cloud-first com autenticação, suporte a `PROVISIONING_SCRIPT`, serviços em supervisor, porta 8188; testado em RunPod e Vast.ai.
- **WAN 2.2 AI Influencer** (aiorbust) — focado em animação de personagem/retrato.

**Como criar seu template:** Templates → New Template. Defina Container Image (sua imagem do Docker Hub/registry), Container Disk, Volume Mount Path (`/workspace`), portas HTTP/TCP expostas, Docker/Start Command e variáveis de ambiente. Salve e selecione no deploy. **Nunca salve template público com tokens/segredos nos campos.**

**Versão de CUDA:** RTX 50xx/B200 (Blackwell) exigem **CUDA 12.8**. Filtre a GPU por CUDA 12.8 no deploy ao usar templates Blackwell.

### 6. Como criar um arquivo/script de instalação para agilizar o setup (parte crítica)

Há três caminhos, do mais automático ao mais manual.

**(a) Provisioning script via `PROVISIONING_SCRIPT` (recomendado).** Os templates AI-Dock/ComfyUI leem a variável de ambiente `PROVISIONING_SCRIPT`, que aponta para a **URL raw** de um `.sh` (GitHub Gist ou Pastebin raw). O script roda no boot e instala custom nodes + baixa modelos. Estrutura oficial do AI-Dock (arrays a editar):

```bash
#!/bin/bash
# Baseado em github.com/ai-dock/comfyui/config/provisioning/default.sh

NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager"
  "https://github.com/kijai/ComfyUI-WanVideoWrapper"
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
  "https://github.com/city96/ComfyUI-GGUF"
  "https://github.com/kijai/ComfyUI-KJNodes"
  "https://github.com/rgthree/rgthree-comfy"
  "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation"
)

DIFFUSION_MODELS=(
  "https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors"
)
TEXT_ENCODERS=(
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
)
VAE_MODELS=(
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"
)
CLIP_VISION=(
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"
)
LORA_MODELS=(
  "https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors"
)
```
O framework do AI-Dock já traz funções (`provisioning_get_nodes`, `provisioning_get_models`, `provisioning_download` via `wget -qnc --content-disposition`) que iteram esses arrays, fazem `git clone --recursive` de cada node e instalam dependências pip (via micromamba). Você só edita os arrays e hospeda o `.sh` num Gist; cole a URL raw em `PROVISIONING_SCRIPT`. Localmente, você pode montar o script em `/opt/ai-dock/bin/provisioning.sh`. **Só use scripts confiáveis** (eles rodam como root).

**(b) Script bash manual (.sh) no web terminal/JupyterLab.** Quando não quer depender do template AI-Dock:

```bash
#!/bin/bash
cd /workspace/ComfyUI/custom_nodes
for repo in \
  https://github.com/kijai/ComfyUI-WanVideoWrapper \
  https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite \
  https://github.com/city96/ComfyUI-GGUF \
  https://github.com/kijai/ComfyUI-KJNodes \
  https://github.com/rgthree/rgthree-comfy \
  https://github.com/Fannovel16/ComfyUI-Frame-Interpolation; do
  git clone "$repo"
  [ -f "$(basename $repo)/requirements.txt" ] && pip install -r "$(basename $repo)/requirements.txt"
done

# Modelos gated do HuggingFace via token
export HF_TOKEN=hf_xxxxxxxx
cd /workspace/ComfyUI/models/diffusion_models
wget --header="Authorization: Bearer $HF_TOKEN" \
  https://huggingface.co/Comfy-Org/SCAIL-2/resolve/main/diffusion_models/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors
```
Salve como `setup.sh` e rode `bash setup.sh` no web terminal. Para downloads rápidos, use `HF_HUB_ENABLE_HF_TRANSFER=1` com `hf download` (atinge 100–200+ MB/s vs ~15 MB/s no pip).

**(c) Geradores de one-liner.** Sites como `deploy.promptingpixels.com` montam um comando único (`bash <(wget -qO- https://.../script) --hf-token=... --civitai-token=...`) com checkboxes de modelos/nodes; cole no web terminal.

**Estrutura de pastas no Network Volume** (sempre em `/workspace/ComfyUI/models/`):
```
models/
├── diffusion_models/   (wan2.1_14B_SCAIL_2_fp8_scaled, wan2.2_*_14B_fp8_scaled)
├── unet/               (versões GGUF)
├── text_encoders/      (umt5_xxl_fp8_e4m3fn_scaled)
├── clip_vision/        (clip_vision_h)
├── vae/                (wan_2.1_vae)
├── loras/              (lightx2v, DPO lora)
└── checkpoints/        (sam3.1_multiplex_fp16, modelos SDXL)
```

**Tokens gated.** Gere o HF token em huggingface.co/settings/tokens (read) e o CivitAI token nas settings da conta; passe como `HF_TOKEN`/`CIVITAI_TOKEN` (variáveis de ambiente). Um token errado causa downloads parciais silenciosos.

**HearmemanAI por variáveis de ambiente (alternativa sem escrever script).** O template baixa modelos no primeiro boot conforme toggles `True/False`. Confirmados em fontes oficiais/comunidade: `download_480p_native_models` (1.3B T2V + 14B T2V/I2V 480p), `download_720p_native_models` (720p), `download_wan22`, `civitai_token` (sua API key CivitAI), `LORAS_IDS_TO_DOWNLOAD` (lista de AIR codes separados por vírgula). Os toggles de VACE, Wan Fun e o de desativar SageAttention/Triton existem mas têm nomes a confirmar no README in-console (ícone "?"). Defina `HF_TOKEN` para modelos gated. Disco ≥20GB (recomenda-se bem mais — 200GB+ se baixar vários conjuntos).

**Reprodutibilidade e reuso.** (1) Salve o `.sh` no GitHub para versionar; (2) salve seus workflows como JSON (export no ComfyUI) no volume; (3) reuse o mesmo Network Volume entre pods — os modelos já estarão lá. **runpodctl** (CLI, pré-instalado em todo pod) ajuda: `runpodctl send <arquivo>`/`runpodctl receive <código>` para transferências rápidas sem API key (relay via croc), além de `runpodctl pod list/create/stop`. Para volumes, a S3-compatible API (datacenters US-KS-2, EU-CZ-1, US-CA-2) permite subir modelos antes mesmo de ligar uma GPU. Para mover dados entre volumes/regiões, use dois pods "bridge" e `rsync -avzP --inplace -e "ssh -p <porta>"`.

### 7. Otimização de custo-benefício (estratégias)

- **Network Volume para não rebaixar modelos:** o maior ganho. Pré-baixe tudo uma vez; pods seguintes sobem em segundos. Custo ~US$7/mês para 100GB.
- **Pare pods quando não usar.** Cobrança é por tempo ligado. Atenção: Volume Disk parado cobra em dobro; se vai pausar por semanas, migre dados para Network Volume (US$0,07/GB) ou apague volumes não usados.
- **Community Cloud/Spot** para jobs toleráveis a interrupção (50–70% mais barato).
- **Regiões mais baratas / disponibilidade:** verifique disponibilidade de GPU antes de fixar prazo de projeto.
- **Dimensione o disco** corretamente (não pague por 500GB se usa 150GB).
- **Resolução em estágios:** itere a 480p, finalize a 720p (a maior economia por iteração).
- **Serverless** para produção que escala a zero (ver seção 8).
- **Sem egress fees:** a RunPod não cobra transferência de saída, ao contrário de AWS/GCP — bom para baixar/subir modelos e renders pesados.

**Local vs Cloud.** Comprar uma RTX 4090 (~US$1.600) equivale a ~2.300 horas de 4090 na RunPod a US$0,69/h; uma 5090 a US$0,99/h, ~1.600 horas. Se você gera vídeo poucas horas por semana e quer várias GPUs diferentes (A100/H100 para 720p), a cloud vence em flexibilidade e custo inicial. O ponto de virada para vídeo costuma ficar em torno de **100–200 vídeos/mês**; acima disso e com uso constante, hardware local começa a compensar — mas perde o acesso sob demanda a H100/H200.

### 8. Serverless para produção

O **worker-comfyui** (`runpod/worker-comfyui`, oficial) roda ComfyUI atrás de uma API. Características:
- **Escala a zero**: cobra só quando processa; cold start sub-2s com FlashBoot.
- **Workers Flex** (sobem sob demanda, ideais para tráfego em rajada) e **Active** (sempre ligados, ~40% mais baratos para carga constante; valem a pena acima de ~25% de utilização mensal, ~180h).
- **Deploy:** Serverless → New Endpoint. Opções: (a) Hub → ComfyUI (vem com FLUX.1-dev-fp8); (b) Import from Docker Registry com `runpod/worker-comfyui:<versão>-<modelo>` (base, flux1-dev, flux1-schnell, sdxl, sd3); (c) "Start from GitHub Repo" (build automático a cada push). Para modelos próprios (Wan/SCAIL-2), use um **Network Volume** com os modelos (mount em `/runpod-volume`) e a imagem `-base`, ou construa um Dockerfile customizado (sempre `--platform linux/amd64`). Marque "Refresh Worker" para o worker parar após cada job.
- **Uso:** envie o workflow em formato **API** (Export (API) no ComfyUI) no campo `input.workflow` para `/run` (assíncrono, retorna `IN_QUEUE` → consulte `/status`) ou `/runsync` (síncrono, ≤90s). Saída em base64 ou S3 (configurando `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`, `AWS_BUCKET_NAME`). Limite de payload: 10MB (`/run`) / 20MB (`/runsync`). Autenticação por `Bearer <API Key>`.
- **Preços Serverless (flex, equivalente/h):** 16GB US$0,58; 4090 US$1,10; 5090 US$1,58; L40/L40S/6000 Ada US$1,90; A100 US$2,72; RTX 6000 Pro US$4,00; H100 US$4,18; H200 US$5,58; B200 US$8,64.
- **Quando usar:** automação de geração de comerciais via API, picos de demanda, evitar custo ocioso. Para trabalho interativo/iteração, fique em Pods.
- A CLI **ComfyGen** (Hearmeman24) automatiza submeter workflows e baixar modelos (HuggingFace/CivitAI) para o Network Volume e Serverless via comandos JSON — útil para integrar com agentes/pipelines.

### 9. Troubleshooting e dicas práticas

- **Pod não inicia / "Zero GPUs on restart":** a GPU pode estar esgotada na região ao reiniciar um pod parado. Solução: tente outra região/GPU; mantenha modelos no Network Volume para recriar rápido.
- **Porta 8188 não fica disponível:** aguarde o log "All startup tasks have been completed"; "Bad Gateway" do Cloudflare some em ~60s — atualize o navegador.
- **OOM (out of memory):** reduza primeiro o nº de **frames** (multiplicam VRAM mais rápido que resolução), depois a resolução (720p→480p); ative fp8/GGUF e CPU offload do text encoder (`t5_cpu`). Rode **um job de vídeo por GPU** — vídeo não faz batch como imagem; vários jobs na mesma GPU causam OOM.
- **Modelos não baixam:** token HF/CivitAI errado causa download parcial silencioso; verifique. Rate limit (429) do HuggingFace: use `HF_HUB_ENABLE_HF_TRANSFER=1` e baixe primeiro para o volume.
- **Perda de dados:** sem Network Volume, terminar o pod apaga tudo. Sempre salve saídas/workflows no volume.
- **Volume em região errada:** volume e pod precisam estar na mesma região; cross-region falha ou tem latência alta (200ms+).
- **Segurança:** não exponha portas sensíveis; nunca coloque tokens em template público; use senha forte/2FA na conta; para dados de clientes sensíveis, use Secure Cloud (single-tenant) e filtre data centers por compliance ("Security & compliance" em Additional filters no deploy). Dados são criptografados (AES-256 em repouso, TLS em trânsito).
- **Monitorar GPU/VRAM:** página Pods do console mostra utilização de GPU/disco; no terminal use `nvidia-smi`. Se a GPU fica em ~0% e a geração demora 10min+, o modelo caiu para CPU (VRAM insuficiente) — reduza quantização ou use `--lowvram`.
- **Comunidade:** Discord da RunPod, r/comfyui e r/StableDiffusion, e templates do HearmemanAI/AI-Dock são as melhores fontes de scripts e workflows atualizados.

## Recommendations

1. **Setup imediato (semana 1):** crie um Network Volume de 150–200GB na região com boa disponibilidade de RTX 5090/A100. Lance um pod barato (RTX 4090) com o template ComfyUI oficial **ou** AI-Dock + `PROVISIONING_SCRIPT` apontando para um Gist com seus nodes (WanVideoWrapper, VideoHelperSuite, GGUF, KJNodes, rgthree, Frame-Interpolation) e modelos (SCAIL-2 fp8, Wan 2.2 14B fp8, Flux dev fp8). Baixe tudo uma vez para o volume. Para a primeira cópia, uma GPU barata economiza, já que o trabalho é só baixar/instalar.
2. **Fluxo de produção de comerciais:** itere composição em **480p na RTX 5090** (US$0,99/h); finalize em **720p na A100 80GB** (US$1,49/h) ou H100 se precisar de velocidade. Para clipes 10s+/multi-personagem (SCAIL-2 multi-ref), suba para **H200**.
3. **Automação:** quando o workflow estabilizar, replique-o em **Serverless worker-comfyui** com o Network Volume, e dispare via API (`/run`) — escala a zero entre comerciais.
4. **Reprodutibilidade:** versione o `.sh` no GitHub, exporte os workflows como JSON no volume e padronize um template próprio salvo (privado, sem tokens).
5. **Benchmarks que mudam a decisão:** se um clipe 720p no 14B passa de ~80GB (OOM na A100/H100), vá para **H200**. Se o custo mensal de Pods ligados passar de ~25% de utilização contínua (~180h/mês), migre produção para **Serverless Active workers** (ou Savings Plan de 3–6 meses para H100, ~20% off).

## Caveats
- **Preços mudam com frequência.** Os valores são da página oficial de pricing da RunPod (junho/2026, Secure Cloud on-demand) e de análises de terceiros (maio–junho/2026). Community Cloud/Spot variam por oferta e região — sempre confirme no console antes de fechar orçamento.
- **VRAM do SCAIL-2:** os rótulos da fonte (fp8=32GB, fp16=16GB) parecem invertidos; trate fp8/mxfp8 como menor VRAM. Não há benchmark oficial de tempo de geração do SCAIL-2 até junho/2026 — os tempos citados para SCAIL-2 são estimativas baseadas no pipeline destilado de ~6–8 steps; valide no seu pod.
- **Nomes de variáveis do template HearmemanAI:** confirmados via fontes — `download_480p_native_models`, `download_720p_native_models`, `download_wan22`, `civitai_token`, `LORAS_IDS_TO_DOWNLOAD`. Os toggles de VACE, Wan Fun, o de desativar SageAttention/Triton e o uso exato de `HF_TOKEN` devem ser confirmados no README in-console (ícone "?") do template antes de publicar.
- **Community Cloud:** a RunPod não aceita mais novos hosts; a disponibilidade tende a diminuir ao longo do tempo. Network Volumes só existem na Secure Cloud.
- **Licenças:** Wan/SCAIL-2 são Apache 2.0 (uso comercial permitido na maioria dos casos), mas **Flux.2 Klein 9B** usa licença de pesquisa não-comercial — verifique a licença do model card antes de usar em comerciais. Não foi encontrada referência pública à "HGX B300" no catálogo da RunPod em junho/2026; o topo de VRAM disponível é B200/H200/RTX PRO 6000.
- O `worker-comfyui` em modo serverless **pula o provisioning** e não atualiza nodes no boot — garanta que tudo necessário esteja no Network Volume (configurado antes em um pod GPU) ou embutido na imagem Docker.