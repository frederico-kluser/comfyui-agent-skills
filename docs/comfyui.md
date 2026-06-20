# ComfyUI — Geração local de imagem e vídeo

> **Quick Start (TL;DR)**
>
> ```bash
> # Subir o ComfyUI no browser (modo safe, todos os modelos)
> comfy
>
> # Ciclo de vida
> comfy stop | status | restart | open | logs -f
>
> # Manter atualizado
> comfy update             # core + custom nodes
> comfy snapshot save pre-update-AAAA-MM-DD
>
> # Baixar modelos
> comfy download wan       # Wan 2.2 14B Q4_K_M
> comfy download hunyuan   # HunyuanVideo 720p Q4_K_M
> comfy download sdxl      # SDXL base + refiner
> comfy download all
>
> # Diagnóstico completo
> comfy doctor             # torch+CUDA+sage+disk+GPU
> ```
>
> **Política sage attention:** `comfy` (default) **NÃO** usa `--use-sage-attention` global porque o backend Triton produz output preto em Wan/Qwen. Para Flux/SD use `comfy sage` OU o nó `Patch Sage Attention KJ` (KJNodes) dentro do workflow. Para casos low-VRAM extremos use `comfy extreme`.

---

## 1. Visão geral

ComfyUI é uma engine local de geração de imagem/vídeo via nós (graph-based). Roda inteiramente offline, sem telemetria, e tem o ecossistema mais maduro de quantização/offload do mercado em 2026.

**Por que ComfyUI (vs A1111, SwarmUI, Fooocus):**
- Workflows são JSON versionáveis e portáveis.
- Suporte nativo a quantização GGUF (até Q2_K), DisTorch2 (offload RAM), BlockSwap (Kijai), Dynamic VRAM (mar/2026).
- Custom nodes para tudo: WanVideo/HunyuanVideo wrappers do Kijai, MultiGPU do pollockjj, GGUF do city96.
- ComfyUI-Manager via UI para instalar/atualizar nós sem CLI.
- API JSON para integração com scripts/automation.

**Versão atual** (`comfy doctor` para confirmar):
- ComfyUI 0.22.0 (commit `ea62dc11`)
- PyTorch 2.12.0+cu130
- Triton 3.7.0
- SageAttention 2.2.0 (kernels FP8 sm_89)
- Python 3.12.3 (venv em `~/ComfyUI/venv`)

---

## 2. Hardware deste setup (PHN16-72)

| Componente | Valor |
|---|---|
| CPU | i9-14900HX (8P+16E, 32 threads) |
| GPU | NVIDIA RTX 4070 Laptop **8 GB VRAM** (sm_89 Ada Lovelace) |
| iGPU | Intel Raptor Lake UHD Graphics (não usada pelo ComfyUI) |
| RAM | 31 GB DDR5 (~27 GB utilizáveis para offload) |
| Disco | NVMe 915 GB ext4, ~560 GB livres |
| Driver NVIDIA | 580.126.18 (expõe CUDA 13.0) |
| CUDA toolkit local | `/usr/local/cuda-13.0` (via NVIDIA repo cuda-keyring + `cuda-nvcc-13-0`) |
| Sysctl AI tuning | `/etc/sysctl.d/99-ai-workload.conf` (`vm.vfs_cache_pressure=50`, `vm.min_free_kbytes=262144`) |

**Implicação prática:** com 8 GB VRAM + 27 GB RAM utilizável = **~35 GB de pesos de modelo carregáveis** (com DisTorch2 + BlockSwap + Dynamic VRAM). Vide [§ 8 — Receitas](#8--receitas-práticas-por-tipo-de-modelo).

---

## 3. Layout do diretório

```
~/ComfyUI/                                  # repo principal (git clone)
├── venv/                                   # Python 3.12 + PyTorch + Sage (~10 GB)
├── main.py                                 # entry point
├── start_comfy.sh                          # launcher safe (default — sem sage global)
├── start_comfy_sage.sh                     # launcher Flux/SD only (com --use-sage-attention)
├── start_comfy_extreme.sh                  # launcher --novram para casos OOM
├── custom_nodes/                           # extensões
│   ├── comfyui-manager/                    # gerenciador UI + cm-cli.py
│   ├── ComfyUI-MultiGPU/                   # DisTorch2 (offload RAM/multi-GPU)
│   ├── ComfyUI-GGUF/                       # loaders GGUF (city96)
│   ├── ComfyUI-WanVideoWrapper/            # Wan 2.x + BlockSwap (Kijai)
│   ├── ComfyUI-HunyuanVideoWrapper/        # Hunyuan + BlockSwap (Kijai)
│   ├── ComfyUI-KJNodes/                    # Patch Sage Attention KJ + utilitários
│   └── ComfyUI-VideoHelperSuite/           # codec/preview vídeo
├── models/                                 # ~72 GB total
│   ├── diffusion_models/                   # GGUF UNETs
│   ├── checkpoints/                        # safetensors completos (SDXL)
│   ├── text_encoders/                      # clip_l, t5xxl, umt5, llava
│   ├── vae/                                # decoders
│   ├── loras/                              # (vazio — LightX2V pendente)
│   └── MODELS_TO_DOWNLOAD.txt              # manifest de tiers e instruções
└── user/
    ├── default/workflows/                  # 9 workflows prontos (Flux + APIs vídeo)
    ├── comfy.log                           # log do launcher
    └── comfy.pid                           # PID do processo background

~/.local/bin/comfy                          # executável principal (Bash)
~/.local/share/applications/comfyui.desktop # entrada para launcher COSMIC
```

---

## 4. Executável `comfy`

Script Bash único em `~/.local/bin/comfy` (versionado também em `~/Projects/config/06-ai-agents/`? não — vive lá no `.local/bin`). Wrappa os três launchers e adiciona gerenciamento de ciclo de vida + downloads + diagnóstico.

| Subcomando | Função |
|---|---|
| `comfy` ou `comfy launch` | Sobe em modo safe (todos modelos), abre browser |
| `comfy sage` | Sobe com `--use-sage-attention` global (Flux/SD only) |
| `comfy extreme` | Sobe com `--novram --cache-none` (casos OOM) |
| `comfy stop` | TERM + (KILL após 15s); limpa pidfile |
| `comfy restart [mode]` | stop + launch (modo `safe|sage|extreme`) |
| `comfy status` | Estado, PID, URL, VRAM usada |
| `comfy open` | Abre browser (sobe se não estiver rodando) |
| `comfy logs [-f]` | Mostra/segue `~/ComfyUI/user/comfy.log` |
| `comfy update [target]` | Atualiza `all` (default) / `core` / `nodes` / `pip` |
| `comfy download <set>` | Baixa `flux`, `wan`, `hunyuan`, `sdxl`, `all` (via `hf` CLI) |
| `comfy snapshot save|restore|list` | Wrap do `cm-cli.py` para snapshots de custom nodes |
| `comfy shell` | Subshell com venv ativada e cwd em `~/ComfyUI` |
| `comfy doctor` | Sanity check (torch, CUDA, sage, disco, GPU) |
| `comfy help` | Mensagem de uso |

**Env overrides:** `COMFY_HOME`, `COMFY_HOST` (def `127.0.0.1`), `COMFY_PORT` (def `8188`), `COMFY_BROWSER` (def `xdg-open`), `COMFY_NO_OPEN` (skip browser auto-open).

---

## 5. Modelos instalados (estado atual)

Total: **~72 GB** em `~/ComfyUI/models/`.

### Diffusion models (UNETs / GGUF)
| Arquivo | Tamanho | Loader |
|---|---|---|
| `flux1-dev-Q8_0.gguf` | 12 GB | UnetLoaderGGUFDisTorch2MultiGPU (vv=6.5) |
| `Wan2.2-T2V-A14B-HighNoise-Q4_K_M.gguf` | 9.0 GB | UnetLoaderGGUF + Wan workflow (two-stage) |
| `Wan2.2-T2V-A14B-LowNoise-Q4_K_M.gguf` | 9.0 GB | (segunda passada do Wan) |
| `hunyuan-video-t2v-720p-Q4_K_M.gguf` | 7.4 GB | UnetLoaderGGUF (Hunyuan 1.0, 13B) |

### Checkpoints (SDXL safetensors)
| Arquivo | Tamanho |
|---|---|
| `sd_xl_base_1.0.safetensors` | 6.5 GB |
| `sd_xl_refiner_1.0.safetensors` | 5.7 GB |

### Text encoders
| Arquivo | Tamanho | Para qual modelo |
|---|---|---|
| `clip_l.safetensors` | 235 MB | Flux + Hunyuan + SDXL |
| `t5xxl_fp8_e4m3fn.safetensors` | 4.6 GB | Flux |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6.3 GB | Wan 2.2 |
| `llava_llama3_fp8_scaled.safetensors` | 8.5 GB | Hunyuan |

### VAEs
| Arquivo | Tamanho | Para qual modelo |
|---|---|---|
| `ae.safetensors` | 320 MB | Flux |
| `wan_2.1_vae.safetensors` | 243 MB | Wan 2.x |
| `hunyuan_video_vae_bf16.safetensors` | 471 MB | Hunyuan |
| `sdxl_vae.safetensors` | 320 MB | SDXL (vae-fp16-fix da madebyollin) |

---

## 6. Workflows prontos

Em `~/ComfyUI/user/default/workflows/` (validados server-side):

| Arquivo | Descrição |
|---|---|
| `01_flux_q8_text_to_image.json` | Flux Q8 GGUF + DisTorch2 vv=6.5 + Sage, 1024², 20 steps |
| `02_flux_q8_image_to_image.json` | Flux Q8 I2I, denoise=0.85 |
| `03_api_kling_i2v.json` | API Kling 2.1-master pro 5s (cloud, requer login Comfy API) |
| `04_api_hailuo_i2v.json` | API MiniMax Hailuo 02 6s 768P |
| `05_api_veo3_t2v.json` | API Veo 3.1-generate 1080p 8s + audio |
| `06_api_sora2_video.json` | API sora-2 1280x720 8s |
| `07_api_runway_gen4_i2v.json` | API Gen-4 Turbo 5s 16:9 |
| `08_api_seedance_t2v.json` | API Seedance 1.5 Pro 1080p 5s |
| `09_api_seedance_i2v.json` | API Seedance I2V adaptive ratio |

**Auth API Nodes**: Settings (engrenagem) → User → Sign In em `platform.comfy.org`; depois Settings → Comfy API Key → cole. Free tier 400 cr/mês desde mar/2026. Único proxy unificado, sem BYOK em core (workaround: `holo-q/comfy-api-liberation` se quiser usar chaves próprias).

---

## 7. Desafios que superamos

Cronologia dos problemas encontrados e como foram resolvidos.

### 7.1 — CUDA major mismatch (PyTorch cu130 × nvcc 12.0)
**Problema:** `apt install nvidia-cuda-toolkit` instala `nvcc 12.0`. PyTorch 2.11+cu130 exige `torch.utils.cpp_extension` com nvcc batendo a **major version** (13). Build do SageAttention falhava com `runtime version differs`.

**Solução:** instalar `cuda-keyring` da NVIDIA + `cuda-nvcc-13-0` + `cuda-cudart-dev-13-0`, depois `export CUDA_HOME=/usr/local/cuda-13.0 PATH=$CUDA_HOME/bin:$PATH TORCH_CUDA_ARCH_LIST="8.9"` antes do `python setup.py install` da SageAttention.

### 7.2 — SageAttention global causa output preto em Wan/Qwen
**Problema:** O flag `--use-sage-attention` força backend Triton em todos os modelos do processo. O kernel Triton da SageAttention 2.x tem overflow em quantização e gera tensores zerados → **vídeo/imagem preto** em Wan e Qwen. Confirmado em [SageAttention issue #221](https://github.com/thu-ml/SageAttention/issues/221) e [ComfyUI issue #9773](https://github.com/Comfy-Org/ComfyUI/issues/9773).

**Solução:** removemos `--use-sage-attention` dos launchers default (`start_comfy.sh` e `start_comfy_extreme.sh`). Em workflows Flux/SD usar o nó `Patch Sage Attention KJ` do KJNodes com backend `sageattn_qk_int8_pv_fp16_cuda` (kernel CUDA, não Triton — não tem o bug). Criamos um terceiro launcher `start_comfy_sage.sh` para sessões 100% Flux/SD onde o flag global é seguro (= `comfy sage`).

### 7.3 — Flag inexistente `--cuda-cast-bf16`
**Problema:** Web search sugeriu adicionar `--cuda-cast-bf16` aos launchers. ComfyUI rejeitou: `main.py: error: unrecognized arguments: --cuda-cast-bf16`.

**Solução:** flag não existe. ComfyUI tem `--bf16-unet`, `--bf16-vae`, `--bf16-text-enc` que forçam BF16 por componente, mas em Ada (sm_89) o autodetect já usa BF16 onde apropriado. Nenhum flag adicional necessário.

### 7.4 — Bug clássico `set -euo pipefail` + `((i++))`
**Problema:** No primeiro deploy do `~/.local/bin/comfy`, rodar `comfy` retornava com exit code 1 após 1 segundo, mostrando só `.%` no terminal — mas o daemon subia OK em background. Diagnóstico: dentro do loop `while ! curl ...`, a primeira execução de `((i++))` (post-increment) retorna `0` (valor antigo), interpretado como exit code 1 → `set -e` mata o script silenciosamente.

**Solução:** trocar `((i++))` por `i=$((i+1))`. Outras alternativas válidas: `(( ++i ))` (pre-increment, retorna novo valor não-zero) ou `((i++)) || true`.

### 7.5 — `huggingface-cli` foi descontinuado
**Problema:** `MODELS_TO_DOWNLOAD.txt` original referenciava `huggingface-cli`. Em `huggingface_hub 1.x` o CLI foi renomeado para `hf` e o nome antigo emite warning fatal.

**Solução:** `comfy download` usa `~/ComfyUI/venv/bin/hf` exclusivamente. Funções `_dl_*` no script.

### 7.6 — Estrutura de subdirs do HF preservada em `--local-dir`
**Problema:** `hf download <repo> path/to/file.safetensors --local-dir target/` baixa em `target/path/to/file.safetensors`, não em `target/file.safetensors`. ComfyUI escaneia recursivamente, mas a UX fica ruim.

**Solução:** helper `_dl_file()` no executável `comfy` faz `mv` do arquivo + `rmdir` dos subdirs vazios. Idempotente: pula download se basename já existe no destino.

### 7.7 — Repos errados nos primeiros downloads
**Problema:** Search engine apontou para `city96/Wan2.2-T2V-A14B-gguf` (não existe). Correto é `QuantStack/Wan2.2-T2V-A14B-GGUF` com subdirs `HighNoise/` e `LowNoise/`.

**Solução:** descoberta via `huggingface_hub.HfApi().list_repo_files(repo)` em vez de adivinhar nomes. Caminhos canônicos no `comfy download`:
- `QuantStack/Wan2.2-T2V-A14B-GGUF/{HighNoise,LowNoise}/*.gguf`
- `city96/HunyuanVideo-gguf/hunyuan-video-t2v-720p-Q4_K_M.gguf` (hífens, não underscores)
- `Comfy-Org/Wan_2.1_ComfyUI_repackaged/split_files/{text_encoders,vae}/*` (Wan 2.1 VAE serve para 2.2)
- `Comfy-Org/HunyuanVideo_repackaged/split_files/{text_encoders,vae}/*`

### 7.8 — ComfyUI-HunyuanVideoWrapper stale (9 meses)
**Problema:** Upstream do wrapper do Kijai não tem commit desde 2025-08-20 ("Fix transformers update compatibility"). Com `transformers 5.x` atual pode quebrar.

**Solução:** mantemos instalado mas se quebrar, renomear para `.ComfyUI-HunyuanVideoWrapper.disabled` (ComfyUI ignora). Uso básico de HunyuanVideo via GGUF loader nativo (`UnetLoaderGGUF`) + workflows nativos do core cobre o gap.

### 7.9 — Timeout curto no boot do `comfy launch`
**Problema:** O polling do HTTP `/system_stats` no launcher timeoutava em 90s, mas ComfyUI com Manager + 7 custom nodes leva ~100-110s no cold boot (manager faz fetch da registry completa). Erro confuso aparecia.

**Solução:** subir timeout para 180s + nova semântica: se passar de 180s mas processo continua vivo, imprimir warning ("still booting, check `comfy status`") e retornar 0 ao invés de matar.

### 7.10 — `MODELS_TO_DOWNLOAD.txt` faltava ferramentas
**Problema:** Manifest mandava `aria2c`, mas pacote não estava instalado. Idem `git-lfs` e `huggingface-cli`.

**Solução:** `sudo apt install -y aria2 git-lfs` + `git lfs install --skip-smudge` (evita LFS auto-pull pesado em clones futuros) + `~/ComfyUI/venv/bin/pip install -U "huggingface_hub[cli]"`.

---

## 8. Receitas práticas (por tipo de modelo)

Sua máquina suporta modelos **MUITO** maiores que 8 GB VRAM via offload combinado. Cinco camadas (todas instaladas):

1. **GGUF quantization** — reduz arquivo 2-8× (Q4 vs FP16)
2. **DisTorch2** (MultiGPU) — distribui camadas entre VRAM e RAM
3. **BlockSwap** (Kijai) — swap on-the-fly de blocos transformer
4. **Async Offload + Pinned Memory** — stream RAM↔VRAM 10-50% mais rápido (default desde dez/2025)
5. **Dynamic VRAM** — alocador JIT, pode exceder até RAM (auto desde mar/2026, PR #11845)

### Regra do `virtual_vram_gb` do DisTorch2
```
virtual_vram_gb = max(0, model_GB − 5)
```
Os 5 GB restantes servem para activations + KV cache + safety margin.

### Imagem (Flux / SDXL / HiDream)
```
UnetLoaderGGUFDisTorch2MultiGPU
  virtual_vram_gb = max(0, model_GB − 5)
  donor_device = cpu
+ Patch Sage Attention KJ (KJNodes) backend = sageattn_qk_int8_pv_fp16_cuda
+ comfy launch  (default, sem --use-sage-attention global)
```

### Vídeo (Wan / Hunyuan)
```
WanVideoModelLoader (Q4/Q6/Q8 GGUF)
+ WanVideoBlockSwap blocks_to_swap = 30-40   (max 40 para 14B)
  offload_img_emb = true
  offload_txt_emb = true
+ Tiled VAE Decode tile_size=256             (poupa 4-6 GB)
+ (opcional) LightX2V LoRA 4-steps           (acelera 5-10×)
+ comfy launch                                (NÃO use comfy sage)
```

### Ultra-grande (>25 GB de pesos)
```
+ comfy extreme                              (--novram --cache-none)
+ BlockSwap = 40 (max)
+ DisTorch2 ratio mode: "cuda:0,4gb;cpu,*"
```

### Custo de velocidade (PCIe 4.0 x16 — laptop pode ser x8)
| Quanto excede VRAM | Penalty vs caber tudo |
|---|---|
| 0 GB (cabe) | baseline |
| +5 GB | ~10-20% mais lento |
| +15 GB | ~30-50% mais lento |
| +25 GB | ~50-80% mais lento |
| RAM cheia → swap | 5-20× mais lento |

---

## 9. Roadmap — o que queremos ter

Modelos que valem o download (priorizados por ganho de qualidade no nosso hardware):

| Modelo | Params | Quant recomendado | Tamanho | Repo | Por quê |
|---|---|---|---|---|---|
| **Flux 2 Dev** | 32B | Q4_K_M | 19.3 GB | `city96/FLUX.2-dev-gguf` | **Lançado nov/2025**. 2.7× maior que Flux 1, qualidade muito maior. Q4_K_M preserva ~95% do BF16. **Top recomendação.** |
| **HunyuanVideo 1.5 T2V 720p** | 8.3B | Q5_K_M | 6.1 GB | `jayn7/HunyuanVideo-1.5_T2V_720p-GGUF` | **Lançado dez/2025**. Mais leve E melhor que Hunyuan 1.0 13B atual. Cabe folgado. |
| **Wan 2.2 14B Q8_0** | 14B | Q8_0 | 15.4 GB (×2) | `QuantStack/Wan2.2-T2V-A14B-GGUF/{High,Low}Noise` | Upgrade do Q4_K_M atual (qualidade visivelmente melhor) |
| **LightX2V LoRA 4-steps** | — | LoRA rank64 | ~200 MB ×2 | `lightx2v/Wan2.2-Lightning` | Wan 14B em ~30s ao invés de ~3min |
| **HunyuanVideo 1.5 I2V 720p** | 8.3B | Q5_K_M | 6.1 GB | `jayn7/HunyuanVideo-1.5_I2V_720p-GGUF` | Image-to-video versão 1.5 |
| **HiDream-I1 Q3_K_M** | 17B | Q3_K_M | 8.77 GB | search `HiDream-I1-Full-GGUF` | Estilo HiDream específico (se precisar) |
| **Flux 2 Dev Q6_K** | 32B | Q6_K | 27.4 GB | `city96/FLUX.2-dev-gguf` | Qualidade máxima Flux 2 (lento mas roda) |

**O que NÃO está disponível:** Wan 2.5 (set/2025) e Wan 2.6 (dez/2025) da Alibaba — só API, pesos não liberados. Hunyuan-Image-3.0 80B — comercial.

### Comandos para baixar (manual até estarem no `comfy download`)
```bash
# Flux 2 Dev Q4_K_M (recomendação #1)
~/ComfyUI/venv/bin/hf download city96/FLUX.2-dev-gguf flux2-dev-Q4_K_M.gguf \
  --local-dir ~/ComfyUI/models/diffusion_models/

# HunyuanVideo 1.5 T2V 720p Q5_K_M
~/ComfyUI/venv/bin/hf download jayn7/HunyuanVideo-1.5_T2V_720p-GGUF \
  hunyuanvideo-1.5_t2v_720p-Q5_K_M.gguf \
  --local-dir ~/ComfyUI/models/diffusion_models/

# Wan 2.2 14B Q8_0 (upgrade do Q4)
~/ComfyUI/venv/bin/hf download QuantStack/Wan2.2-T2V-A14B-GGUF \
  HighNoise/Wan2.2-T2V-A14B-HighNoise-Q8_0.gguf \
  --local-dir ~/ComfyUI/models/diffusion_models/
~/ComfyUI/venv/bin/hf download QuantStack/Wan2.2-T2V-A14B-GGUF \
  LowNoise/Wan2.2-T2V-A14B-LowNoise-Q8_0.gguf \
  --local-dir ~/ComfyUI/models/diffusion_models/

# LightX2V LoRA 4-steps (massive speedup para Wan 14B)
~/ComfyUI/venv/bin/hf download lightx2v/Wan2.2-Lightning \
  Wan2.2-T2V-A14B-4steps-lora-rank64-V1/high_noise_model.safetensors \
  --local-dir ~/ComfyUI/models/loras/
~/ComfyUI/venv/bin/hf download lightx2v/Wan2.2-Lightning \
  Wan2.2-T2V-A14B-4steps-lora-rank64-V1/low_noise_model.safetensors \
  --local-dir ~/ComfyUI/models/loras/
```

### TODOs / melhorias do executável `comfy`
- Adicionar `comfy download flux2 | hunyuan15 | lightx2v | wan22-q8`
- Adicionar `comfy bench` (roda 1 workflow padrão e mede tempo)
- Suporte a `COMFY_HF_TOKEN` para evitar rate limits anonymous

---

## 10. Troubleshooting

### `comfy launch` sai imediato sem mensagem
Bug do `set -e + ((i++))` resolvido (§ 7.4). Se voltar a aparecer, checar `bash -n ~/.local/bin/comfy` para erro de sintaxe.

### `nvidia-smi` mostra VRAM lotada após `comfy stop`
ComfyUI cacheia modelos em VRAM. Esperar 30s ou `fuser -k 8188/tcp` se travar.

### Workflow gera tela preta em Wan/Hunyuan
Está usando `comfy sage`? Trocar para `comfy` (default). Se usando `Patch Sage Attention KJ`, confirmar backend = `sageattn_qk_int8_pv_fp16_cuda` (não Triton).

### Boot lento (>2 min)
Manager está fazendo `FETCH ComfyRegistry Data: N/147` na primeira vez. Espera, vira cache.

### OOM no meio de uma geração de vídeo
Aumentar `blocks_to_swap` no `WanVideoBlockSwap` (até 40 para 14B). Reduzir `tile_size` no `Tiled VAE Decode` (256 ou 192). Se ainda OOM, `comfy extreme`.

### `pip install` em custom_node quebra deps do core
Salvar snapshot antes (`comfy snapshot save pre-install-AAAA-MM-DD`). Em último caso `cm-cli.py restore-snapshot`.

### Download via `hf` extremamente lento
Setar `HF_TOKEN` no `~/.secrets` (sourced pelo `~/.zshenv`). Anonymous tem rate limit pesado.

### SageAttention quebra após `pip install -U torch`
ABI break entre versões major de torch/triton. Recompilar:
```bash
cd /tmp/SageAttention
export CUDA_HOME=/usr/local/cuda-13.0 PATH=$CUDA_HOME/bin:$PATH TORCH_CUDA_ARCH_LIST="8.9"
source ~/ComfyUI/venv/bin/activate
python setup.py install
```

---

## 11. Snapshots & rollback

- ComfyUI core: `git -C ~/ComfyUI log` → `git reset --hard <commit>` para voltar.
- Custom nodes: `comfy snapshot list` → `comfy snapshot restore <name>`. Snapshot `pre-refresh-2026-05-24.json` existente.
- Modelos: arquivos são imutáveis, apagar = `rm models/<arquivo>`.
- Venv: se corromper, `rm -rf venv && python3.12 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` + recompilar SageAttention (§ Troubleshooting).

---

## Referências

### Documentação oficial
- [ComfyUI docs](https://docs.comfy.org/)
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Blog](https://blog.comfy.org/)

### Custom nodes essenciais
- [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager) — cm-cli.py docs
- [ComfyUI-MultiGPU (DisTorch2)](https://github.com/pollockjj/ComfyUI-MultiGPU)
- [ComfyUI-GGUF (city96)](https://github.com/city96/ComfyUI-GGUF)
- [ComfyUI-WanVideoWrapper (Kijai)](https://github.com/kijai/ComfyUI-WanVideoWrapper)
- [ComfyUI-HunyuanVideoWrapper (Kijai)](https://github.com/kijai/ComfyUI-HunyuanVideoWrapper)
- [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes)

### Otimizações (blog posts)
- [Dynamic VRAM in ComfyUI (mar/2026)](https://blog.comfy.org/p/dynamic-vram-in-comfyui-saving-local)
- [Async Offload + Pinned Memory + NVFP4 (dez/2025)](https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia)
- [WanVideoBlockSwap deep dive (DeepWiki)](https://deepwiki.com/kijai/ComfyUI-WanVideoWrapper/6.2-block-swapping-and-device-management)

### Issues conhecidas
- [SageAttention #221 — black output em Wan/FP8](https://github.com/thu-ml/SageAttention/issues/221)
- [ComfyUI #9773 — Sage Triton + Qwen](https://github.com/Comfy-Org/ComfyUI/issues/9773)
- [ComfyUI #12541 — memory regression update 13](https://github.com/Comfy-Org/ComfyUI/issues/12541)

### Repos de modelos
- [city96/FLUX.2-dev-gguf](https://huggingface.co/city96/FLUX.2-dev-gguf)
- [QuantStack/Wan2.2-T2V-A14B-GGUF](https://huggingface.co/QuantStack/Wan2.2-T2V-A14B-GGUF)
- [city96/HunyuanVideo-gguf](https://huggingface.co/city96/HunyuanVideo-gguf)
- [jayn7/HunyuanVideo-1.5_T2V_720p-GGUF](https://huggingface.co/jayn7/HunyuanVideo-1.5_T2V_720p-GGUF)
- [Comfy-Org/HunyuanVideo_repackaged](https://huggingface.co/Comfy-Org/HunyuanVideo_repackaged)
- [Comfy-Org/Wan_2.1_ComfyUI_repackaged](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged)
- [comfyanonymous/flux_text_encoders](https://huggingface.co/comfyanonymous/flux_text_encoders)
- [lightx2v/Wan2.2-Lightning](https://huggingface.co/lightx2v/Wan2.2-Lightning)

### Memória do agente (Claude Code)
- `~/.claude/projects/-home-ondokai/memory/comfyui_setup.md`

**Última atualização:** 2026-05-25
