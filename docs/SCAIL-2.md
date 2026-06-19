# SCAIL-2 no ComfyUI e RunPod.io: Guia Completo (junho de 2026)

## TL;DR
- **SCAIL-2** (da zai-org, sobre o backbone Wan 2.1 14B, lançado em junho de 2026) é hoje o modelo open-source de animação de personagem end-to-end mais avançado: anima uma foto de referência a partir de um vídeo-condutor sem usar mapas de esqueleto, e suporta substituição de personagem, cenas multi-personagem e até motion de animais — mas exige uma máscara colorida obrigatória e prompts longos e detalhados.
- Para rodar no RunPod, use o template oficial ComfyUI (ou "ComfyUI Blackwell Edition" para RTX 5090/B200) com um **Network Volume** persistente; a melhor relação custo-benefício para gerar vídeo Wan 2.1 14B é o **RTX 5090 (32GB)** para clipes 480p e o **A100 80GB / H100 / H200** quando você precisa de 720p ou clipes longos.
- Para comerciais, encadeie: geração de imagem (Flux) → animação (SCAIL-2 para personagem ou Wan I2V para produto) → upscale + interpolação RIFE → edição/áudio; produza em 480p e faça upscale, gere vertical 9:16 e 16:9 desde o início do workflow.

## Key Findings

**O que é e o que faz.** SCAIL-2 ("SCAIL-2: Unifying Controlled Character Animation with End-to-end In-Context Conditioning", arXiv 2606.10804) transfere o movimento de um vídeo-condutor diretamente para uma imagem de personagem de referência, concatenando os latentes do vídeo-condutor à sequência de geração. Diferente do SCAIL-1/SCAIL-Preview (que usava uma representação de pose 3D-consistente com esqueletos coloridos, CVPR 2026 Findings), o SCAIL-2 elimina toda representação intermediária de pose. Foi treinado em 64 GPUs NVIDIA H100 por cerca de uma semana (FSDP-2), usando o dataset sintético MotionPair-60K gerado com SCAIL-Preview, Wan-Animate e MoCha.

**Capacidades emergentes.** Substituição cross-identity, animação dirigida por animais (zero-shot, sem dados de animais no treino), e suporte zero-shot a renderização de malha do SAM3D-Body. Suporta animação single/multi-personagem e substituição de personagem num único modelo unificado.

**Modos e a máscara colorida.** Há "Animation Mode" e "Replacement Mode". A máscara colorida é input crítico mesmo em single-character Animation Mode: preto = fundo não deve ser visível, branco = fundo deve ser visível, cor = correspondência entre regiões do personagem e o movimento condutor.

**Comparação com concorrentes (do paper):** SCAIL-2 vence em "win rate" de consistência de movimento contra SCAIL, Wan-Animate e Kling 3.0. Wan2.2-Animate continua excelente para transferência de expressão facial e tem workflows mais maduros; SCAIL-2 ganha em motion não-padrão, multi-personagem e substituição.

**Versões e VRAM.** Disponível em fp16, fp8_scaled (~17,7 GB de arquivo), mxfp8, e GGUF (RealRebelAI): Q2_K 6,02 GB, Q3_K_M 8,11 GB, Q4_K_M 10,9 GB, Q5_K_M 12,3 GB, Q6_K 13,8 GB, Q8_0 17,7 GB. Recomendação da comunidade: Q8_0 é o "mais próximo do fp16"; Q4_K_M é o "daily driver". Recomenda-se RTX 5090 (32GB) ou superior para setups locais.

## Details

### 1. Arquitetura e capacidades
O backbone é o Wan2.1-14B-I2V. Inovações técnicas: In-Context Mask Conditioning (1 canal "environment switch" + K=6 canais de "binding slots", totalizando 28 canais extras), Mode-specific RoPE como guia suave, e Bias-Aware DPO (Direct Preference Optimization regional, com máscara de mão) para corrigir detalhes como dedos. Usa "reverse driving": um vídeo real é re-sintetizado via transferência de pose/substituição para gerar o condutor sintético, enquanto o vídeo real original serve de alvo — assim o modelo aprende capacidades além dos modelos professores.

Componentes necessários: umt5-xxl text encoder, Wan2.1_VAE, clip_vision_h (OpenCLIP ViT-H/14), sam3.1_multiplex_fp16, e loras de aceleração (Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64) e o DPO lora (wan2.1_SCAIL_2_DPO_lora_bf16, opcional, para corrigir mãos e rostos).

Limitações conhecidas (do README oficial): em certos inputs o Animation Mode pode colapsar em comportamento de Replacement-Mode; a qualidade da animação degrada em movimento complexo; e o efeito de ancoragem do frame de referência degrada em vídeos longos.

### 2. Instalação e setup no ComfyUI

Atualize o ComfyUI para a última versão (nightly pode ser necessário para o nó SCAIL2ColoredMask). Há dois caminhos: nativo ComfyUI (Comfy-Org) e o wrapper ComfyUI-WanVideoWrapper do Kijai.

**Estrutura de pastas (caminho nativo, GGUF):**
```
ComfyUI/models/
├── unet/                SCAIL-2-Q4_K_M.gguf  (ou diffusion_models/ para fp8/fp16)
├── text_encoders/       umt5_xxl_fp8_e4m3fn_scaled.safetensors
├── loras/               Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors
│                        wan2.1_SCAIL_2_DPO_lora_bf16.safetensors (opcional)
├── sam/                 sam3.1_multiplex_fp16.safetensors  (algumas guias usam checkpoints/)
├── clip_vision/         clip_vision_h.safetensors
└── vae/                 wan_2.1_vae.safetensors
```

**Custom nodes necessários:** ComfyUI-GGUF (city96) para carregar GGUF via "Unet Loader (GGUF)"; ComfyUI-WanVideoWrapper (Kijai) para o caminho wrapper; e nós SAM3 (SAM3_VideoTrack) + SCAIL2ColoredMask para gerar as máscaras.

**Onde baixar os modelos:** zai-org/SCAIL-2 (pesos oficiais, precisam de conversão para safetensors via convert.py para o branch wan), Comfy-Org/SCAIL-2 (fp8_scaled/fp16/mxfp8 já empacotados + DPO lora), realrebelai/SCAIL-2_GGUF (quantizações).

**Workflows disponíveis:**
- Kijai test workflow no ComfyUI-WanVideoWrapper (pasta example_workflows).
- "Infinite length workflow" no RunningHub.
- RunComfy "SCAIL-2 Motion Transfer in ComfyUI – Reference Image to Video".
- Next Diffusion tutorial com JSON (nextdiffusion.ai).
- nomadoor "Comfy with ComfyUI" workflow (comfyui.nomadoor.net).

**Avisos comuns:**
- "WEIGHT NOT MERGED warning on patch_embedding is harmless" — o ComfyUI constrói um patch embedding de 36 canais e concatena os canais de máscara em runtime; o peso armazenado de 20 canais é esperado. A geração prossegue normalmente.
- A máscara colorida é obrigatória mesmo em single-character Animation Mode — não a remova do workflow.
- Defina width e height explicitamente, ambos divisíveis por 16 (832×480 é um bom ponto de partida 480p; para 32, 704×1280 vertical).

**Qual quantização escolher:** ≤12GB VRAM → Q4_K_M/Q5_K_M GGUF; 16GB → Q8_0 GGUF ou fp8; 24GB (RTX 4090) → fp8_scaled; 32GB+ (RTX 5090) ou cloud → fp16 para máxima qualidade.

### 3. Melhor configuração qualidade vs velocidade

**Configuração oficial (generate.py) com LightX2V:** `--sample_steps 8 --sample_shift 1 --sample_guide_scale 1.0` com lora_alpha 1.0.

**Configuração ComfyUI (comunidade):** sampler **euler**, scheduler **simple**, **6 steps**, shift **1**, CFG **1.0** (a guidance vem da LoRA destilada, via nó SamplerCustom). Há divergência: CLI oficial usa 8 steps; workflows nativos usam 6. Os ranks da LoRA variam: rank128 (oficial), rank64 (maioria ComfyUI), rank256 (Next Diffusion). Teste os dois valores de steps.

**Frames/fps/resolução:** máximo/padrão **81 frames** (~5s); saída **30 fps** por padrão (VHS VideoCombine); resolução recomendada de 480p (864×480) até ~720p (1280×704), múltiplo de 32. Para vídeos mais longos, use WAN Context Windows com context_length 81 e overlap.

**Prompts:** SCAIL-2 foi treinado com prompts longos e detalhados. Prompts curtos/vazios funcionam mas dão resultado pior. A equipe sugere usar o Gemini para ler a imagem de referência e o movimento e gerar um prompt detalhado. O prompt deve descrever o vídeo gerado em si.

**Qualidade GGUF vs fp8 vs fp16:** Q8_0 é o mais próximo do fp16; fp8 corta a precisão pela metade vs fp16 mas preserva qualidade surpreendentemente bem; Q4/Q3 podem prejudicar qualidade (mais artefatos). Use o DPO lora para corrigir mãos e rostos.

**Trade-off velocidade:** LightX2V (6–8 steps) é dramaticamente mais rápido que os 40 steps padrão do Wan 2.1. GGUF economiza VRAM mas o loader faz memory-map (custa disco e tempo de streaming, não RAM residente).

### 4. RunPod.io — tutorial atualizado (interface 2026)

**Passos:**
1. Crie conta em runpod.io e adicione fundos (mínimo recomendado $10).
2. **Crie um Network Volume** (Storage → New Network Volume) — armazenamento persistente que retém ComfyUI, modelos e workflows mesmo após o pod ser terminado. Escolha a região com as GPUs que você quer. 50GB é um bom começo; vídeo precisa de mais (100–200GB). Custo ~$0,07/GB/mês.
3. **Deploy do pod** com o volume anexado. Use o template oficial **ComfyUI** (RunPod-owned, com CUDA 12.8, ComfyUI-Manager, KJNodes pré-instalados) para GPUs padrão (RTX 4090, L40, A100), ou **ComfyUI Blackwell Edition** para RTX 5090/B200. Templates da comunidade como "One Click ComfyUI - Wan 2.1/2.2 (CUDA 12.8)" da HearmemanAI também servem.
4. Escolha GPU + região e faça Deploy On-Demand (mais flexível) ou Spot/Community Cloud (mais barato, ~20-30% menos, mas pode ser interrompido).
5. Aguarde o status "Running" e a porta 8188 ficar verde/Ready (pode levar de 2-3 min a 30 min na primeira inicialização). Clique em Connect → "Connect to HTTP Service [Port 8188]".
6. Baixe os modelos: use o terminal web/JupyterLab e `wget`/`curl` direto do HuggingFace (velocidade de data center) em vez de upload do PC. Use o ComfyUI Manager para instalar custom nodes faltantes.
7. **Pare o pod** quando terminar — o RunPod cobra por segundo/minuto enquanto o pod roda. Pods parados pagam taxa modesta de storage; o Network Volume mantém os arquivos.

**GPU Cloud (Pods) vs Serverless:** Pods = sessão interativa, ideal para ComfyUI e iteração. Serverless = API que escala a zero, ideal para produção/automação (worker-comfyui no GitHub do RunPod). Para criar comerciais interativamente, use Pods.

**Mudanças 2026:** o RunPod separa Community Cloud vs Secure Cloud (este último com certificação SOC 2 Type II — auditoria iniciada em 1º de março com período de observação de seis meses; os data centers do RunPod já estão certificados Type II), templates dedicados Blackwell, e cobrança por segundo. O ComfyUI nativo agora tem template oficial RunPod com Civicomfy e ComfyUI-RunpodDirect.

### 5. Comparação de tiers de GPU no RunPod (junho de 2026)

Preços on-demand do RunPod (ComputePrices.com / preços oficiais RunPod, atualizado 19/jun/2026; Community Cloud é mais barato):

| GPU | VRAM | Preço/h (on-demand) | Adequação para SCAIL-2 / Wan 2.1 14B |
|---|---|---|---|
| RTX 4090 | 24GB | ~$0,69 (Secure) / ~$0,39 (Community) | 480p OK; não roda 720p no 14B; bom para GGUF/fp8 |
| RTX 5090 | 32GB | ~$0,69–0,90 | Melhor custo-benefício 480p; ~45% mais rápido que 4090 |
| A40 / A6000 | 48GB | ~$0,40–0,80 | Boa folga de VRAM; mais lenta |
| L40S | 48GB | ~$0,79 | Inferência eficiente; throughput médio |
| A100 PCIe | 40GB | $1,19 | Bom equilíbrio; roda 720p |
| A100 SXM | 80GB | $1,39 | 720p + clipes longos confortável |
| H100 PCIe | 80GB | $1,99 | Mínimo prático p/ 720p; rápido |
| H100 SXM | 80GB | $2,69 | Mais rápido (HBM3, 3,35 TB/s vs 2 TB/s do PCIe); ~3x A100 |
| H100 NVL | 94GB | $2,59 | — |
| H200 | 141GB | $3,59 | Para >80GB VRAM e batch |
| B200 | 192GB | ~$5,98 | Topo; geração mais rápida, mas caro |
| HGX B300 | 288GB | ~$6,94 | Frontier; overkill para um clipe |

**Velocidade relativa (Wan 2.1 14B, NÃO SCAIL-2 — labels):** Benchmark InstaSD T2V 14B 480p: RTX 4090 = 281s, A100 = 170s, L40 = 290s, A40 = 350s, H100 = 85s. Em 720p: A100 = 523s, H100 = 284s (4090 não roda 720p). Com LightX2V 6–8 steps esses tempos caem ~5–8x. Wan 2.1 base (40 steps): ~4 min para clipe 480p de 5s no RTX 4090. Nota: SCAIL-2 adiciona overhead de SAM3.1 + CLIP Vision, então os tempos reais são um pouco maiores.

**Veredito custo-benefício:** Para 480p (a maioria dos comerciais virais verticais), **RTX 5090** é o melhor custo-benefício — dobra o throughput do 4090 por preço similar. Para 720p ou clipes longos/multi-personagem, **A100 80GB** é o ponto ideal de equilíbrio; **H100** quando velocidade é prioridade. Use Spot/Community Cloud para economizar em jobs tolerantes a interrupção. Um clipe de 5s no H100 custa aproximadamente $0,25–0,60.

### 6. Workflows para criar um comercial

**a) Foto → vídeo (personagem/pessoa):** Gere a imagem de referência com Flux. Para animar um personagem com performance, use SCAIL-2 com um driving video (dança, gesto, fala). Para movimento mais simples de produto, use Wan 2.1/2.2 I2V direto. A imagem já define o "o quê"; o prompt descreve "como" se move.

**b) Vídeo → vídeo (filmagem real como condutor):** Filme um ator/movimento real e use como driving video no SCAIL-2 para substituir o personagem por seu avatar de marca (Replacement Mode com --replace_flag e máscara da região de substituição) ou estilizar. Ideal para influenciadores virtuais e AI actors consistentes.

**c) Pipeline intercalado:** Combine segmentos foto→vídeo (closes de produto, hero shots) com segmentos vídeo→vídeo (personagem em ação). Mantenha identidade consistente usando a mesma imagem de referência e as mesmas cores de máscara entre clipes. Encadeie clipes curtos (~5s/81 frames cada) via Context Windows ou edição externa, mantendo seed, prompt e versão do modelo registrados.

**d) Formatos:** Vertical 9:16 (Reels/TikTok/Shorts): use por ex. 720×1280 ou 704×1280 (múltiplo de 32). Padrão 16:9 (YouTube/web): 832×480 ou 1280×704. Escolha o aspect ratio no estágio do workflow, não no final.

**Ferramentas complementares (encadeamento):**
- **Imagem inicial (hero frames):** Flux.1. Atenção à licença e atualidade: **FLUX.1 [schnell]** está sob Apache 2.0 e pode ser usado para fins pessoais, científicos e **comerciais** — porém, segundo a Black Forest Labs (jan/2026), foi sucedido por **FLUX.2 [klein]** (variante 4B, também Apache 2.0, ~13 GB VRAM, livre para uso comercial). **FLUX.1 [dev]** usa a "FLUX.1 [dev] Non-Commercial License" (uso comercial exige licença paga em bfl.ai), e foi sucedido por FLUX.2 [dev]. Para comercial sem custo de licença, prefira o ramo schnell/klein (Apache 2.0).
- **Upscale de vídeo:** workflows com modelos como 4x-AnimeSharp (anime) ou NMKD SCAX (fotorrealismo), via CR Upscale Image.
- **Interpolação:** RIFE VFI (ComfyUI-Frame-Interpolation da Fannovel16); um vídeo de 15fps com multiplier 2 → 30fps suave. Use rife47/rife49.
- **Face restore:** CodeFormer (cuidado com flickering facial em anime).
- **Áudio/música:** bibliotecas como Epidemic Sound; o SCAIL-2 passa o áudio dos vídeos de referência.
- **Edição/montagem:** Canva, CapCut ou DaVinci para juntar clipes, legendas e CTA.

**Boas práticas de prompt para comerciais (estrutura Wan):** Sujeito (descrição) + Cena + Movimento + Linguagem de câmera + Atmosfera + Estilo, 80–120 palavras. Inclua ângulo de câmera, iluminação, tipo de movimento e mood. Use negative prompts contra "morphing, warping, distortion, blurry, low quality, face deformation, flickering". Exemplo produto: "A rotating wristwatch on a marble pedestal, studio lighting, ultra-sharp focus". Descreva como as coisas se movem, não o que aparece (a imagem já define isso). Comece com movimento sutil e aumente intensidade ao longo do clipe.

**Resolução/duração por plataforma:** clipes de 3–5s por cena, 24 ou 30 fps. Gere em 480p para iterar rápido e barato (480p é ~7-8x mais barato que 720p) e faça upscale ao final. Vertical 1080×1920 final para Reels/TikTok; 1920×1080 para YouTube.

## Recommendations

1. **Comece barato e local-cloud:** Suba um pod RTX 5090 (32GB) no RunPod com o template ComfyUI Blackwell Edition + Network Volume de 100GB. Rode SCAIL-2 fp8_scaled ou GGUF Q8_0. Configure euler/simple/6 steps/CFG 1.0/shift 1 com a LightX2V LoRA. Gere em 480p, 81 frames.
2. **Suba de tier conforme a necessidade:** se precisar de 720p, multi-personagem ou clipes longos sem degradação, migre para A100 80GB; para velocidade máxima de produção, H100. Use Community Cloud/Spot para lotes toleráveis a interrupção.
3. **Pipeline de comercial:** Flux/FLUX.2 klein (hero frames) → SCAIL-2 (personagem) / Wan I2V (produto) → RIFE 2x → upscale 2x → edição com áudio. Mantenha um workflow-template salvo em três presets (preview, balanced, final).
4. **Sempre inclua a máscara colorida** e prompts longos e detalhados; use o DPO lora para mãos/rostos.
5. **Controle de custo:** pare o pod ao terminar; baixe modelos via wget direto no pod; arquive os JSON de workflow e os frames PNG.

**Benchmarks que mudam a decisão:** Se um clipe 480p levar >2 min com LightX2V no seu tier, suba de GPU. Se a qualidade GGUF Q4 mostrar artefatos em mãos/rosto, troque para Q8/fp8 e ative o DPO lora. Se você gera >200 clipes/mês de forma sustentada, considere o trade-off de comprar um RTX 5090 local (paga-se em ~3-4 meses vs cloud).

## Caveats
- **SCAIL-2 é muito recente (jun/2026):** o suporte nativo no ComfyUI/WanVideoWrapper ainda estava em discussão/evolução (issue #2031 aberta em 10/jun/2026); nós como SCAIL2ColoredMask podem exigir builds nightly.
- **Não há benchmark de tempo/VRAM específico do SCAIL-2** publicado; os tempos de geração citados são de Wan 2.1/2.2 14B equivalentes e estão rotulados como tais. SCAIL-2 tende a ser um pouco mais lento por causa do SAM3.1 + CLIP Vision.
- **Preços de GPU flutuam** por disponibilidade e região; valores são de jun/2026 (on-demand, principalmente Secure Cloud). Community Cloud é mais barato. Verifique runpod.io/pricing antes de provisionar.
- **VRAM por variante:** os números de "32GB para fp8 / 16GB para fp16" de uma fonte (stablediffusiontutorials) parecem invertidos/errados — o arquivo fp8 tem só 17,7 GB; trate com cautela.
- **Licenças:** verifique a licença do SCAIL-2 (MIT no repo GGUF) e de cada modelo/LoRA antes de uso comercial. FLUX.1 [schnell] e FLUX.2 [klein] são Apache 2.0 (uso comercial livre); FLUX.1/2 [dev] são non-commercial sem licença paga.
- **Steps divergentes:** 8 (CLI oficial) vs 6 (ComfyUI nativo) — ambos com CFG 1.0/shift 1/euler/simple. Teste os dois.