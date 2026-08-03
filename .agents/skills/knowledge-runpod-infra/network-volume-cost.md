# RunPod — Network Volume e Disciplina de Custo

## Network Volume (essencial)
Só na **Secure Cloud**. Persiste modelos/saídas entre pods (boot de minutos→segundos).
- ~US$0,07/GB/mês (100GB ≈ US$7/mês).
- Sugestão: **150–200GB** para vídeo.
- Travado por região — crie na região da GPU que vai usar.

## Disciplina de custo
- **Pare o pod** ao terminar (cobra por segundo).
- **Volume Disk parado cobra em dobro** — guarde tudo no Network Volume.
- **Terminate** apaga container/volume efêmero (perde o que não está no Network Volume).
- Sem egress fees (baixar/subir renders é grátis).
- **Um job de vídeo por GPU** (vídeo não faz batch como imagem → OOM).

## Custo de projeto (fórmula)
```
Custo ≈ (tempo/clipe em h) × (US$/h) × (nº de clipes + iterações) + storage
```
Ex.: 50 clipes 720p Wan 14B ~9min na A100 ≈ 50×0,15h×1,49 ≈ **US$11**.

## Caveats
- CUDA **12.8** obrigatório para Blackwell (RTX 5090/B200) → template "ComfyUI Blackwell Edition".
- "Zero GPUs on restart": GPU esgotada na região ao religar pod parado → tente outra região.

## Referências
- `docs/runpod-guide.md`
- Setup → `knowledge-runpod-provisioning`
