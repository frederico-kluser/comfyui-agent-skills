# foto-realismo-celular — deixar qualquer foto com cara de foto de celular

> **Custo zero.** Roda 100% na CPU local: nenhum crédito, nenhuma chave, nenhuma GPU,
> nenhuma chamada de modelo. Serve para tratar **qualquer** imagem — inclusive as suas
> gerações antigas que ficaram com cara de IA.

|  |  |
|---|---|
| 🎯 Faz | Aplica em pixel a assinatura de captura de um celular |
| 🧠 Técnica | Cadeia de degradação calibrada: color match → limite de resolução → curva HDR → aberração cromática → over-sharpening → grão → ruído de sensor → JPEG real |
| 💳 Custo/billing | **Zero.** Nenhuma chamada de API |
| 🔌 Nós | `ColorMatchV2` (KJNodes) · `Image *` (WAS Suite) · `ImageScaleToMaxDimension`/`ImageSharpen`/`ImageAddNoise` (core) |
| 📥 Entrada | A imagem a tratar (+ opcional: uma foto sua de celular como referência de cor) |
| 📤 Saída | `output/celular/foto_*.jpg` |
| 🟢 Status | **Executado e validado nesta máquina.** Os presets foram medidos, não chutados |

---

## Por que isso é necessário

Modelo de imagem entrega uma imagem **matematicamente limpa**: gradiente perfeito,
pele sem poro, tudo igualmente nítido, zero ruído de sensor. Esse conjunto é o que
o olho lê como "IA" — mesmo quando a composição está impecável.

**Pedir grão no prompt não resolve.** O modelo *desenha* uma imitação de grão; ele não
produz a assinatura real do sensor. Ela só entra **depois**, em pixel.

> A pesquisa que embasou este bundle encontrou o mesmo: nenhum fornecedor documenta um
> conjunto de tokens de "celular moderno", e não há dado público de eficácia para o
> look amador via prompt. O passo de pós-processamento é **o único que não depende de
> promessa de fornecedor** — é medível, e foi medido aqui.

---

## Como usar

1. Suba a imagem no `FOTO` (esquerda).
2. *(Opcional)* Suba uma **foto de referência de cor** no `REF DE COR` — de preferência
   uma foto sua real, tirada no celular. O `ColorMatchV2` puxa a paleta dela.
   **Sem referência, ligue a mesma foto nos dois slots.**
3. Run. Sai em `output/celular/`.

## Os 4 presets

Vem no **`padrão`**. Para trocar, ajuste os 8 nós conforme a tabela (também está na nota verde dentro do workflow):

| Nó | `limpo` | **`padrão`** | `marcado` | `luzbaixa` |
|---|---|---|---|---|
| 2 · `largest_size` | 1024 | **896** | 768 | 720 |
| 3 · `contrast` | 0.97 | **0.95** | 0.93 | 0.90 |
| 3 · `saturation` | 1.06 | **1.08** | 1.10 | 0.98 |
| 4 · `intensity` (aberração) | 0.0 | **0.06** | 0.10 | 0.08 |
| 5 · `alpha` (sharpen) | 0.35 | **0.50** | 0.65 | 0.40 |
| 6 · `intensity` (grão) | 0.03 | **0.05** | 0.08 | 0.14 |
| 7 · `strength` (ruído) | 0.006 | **0.010** | 0.016 | 0.030 |
| 8 · `quality` (JPG) | 92 | **90** | 85 | 80 |

| Preset | Quando usar |
|---|---|
| `limpo` | só tirar o aspecto plástico, luz boa |
| **`padrão`** | **serve para quase tudo** |
| `marcado` | quando o resultado ainda parece renderizado |
| `luzbaixa` | simular foto noturna / ambiente escuro |

## Como esses números foram achados

Não foram chutados. Rodei a cadeia nesta máquina sobre uma saída real do bundle
Nano Banana e comparei recortes de rosto a 1:1.

**A primeira tentativa foi ruim** — aberração cromática em `0.35` e grão em `0.14`
produziram franja colorida em toda borda e um chuvisco que parecia JPEG de 2005,
não celular. Os valores acima são a segunda calibração, e a lição virou regra:

> ⚠️ Foto de celular moderno **em boa luz é limpa**. O que denuncia o celular não é
> ruído pesado — é o **tone-mapping HDR**, o **over-sharpening** e o **JPEG**.
> Aberração acima de ~0.15 e grão acima de ~0.2 estragam em vez de ajudar.

## ⚠️ Limite de tamanho (importante)

O nó 6 (`Image Film Grain`) **supersampleia 4× internamente**. O nó 2
(`ImageScaleToMaxDimension`) segura o lado maior justamente para isso não estourar a RAM.

**Não passe `largest_size` de ~2048.** Durante a calibração, uma imagem de
**5248×12800 derrubou o ComfyUI** nesta máquina. Se precisar de mais resolução,
suba o `resolution` do modelo que gerou a imagem e mantenha este nó baixo.

## Pré-requisitos

Custom nodes (já instalados nesta máquina): `was-node-suite-comfyui` · `ComfyUI-KJNodes`.
Nenhuma chave, nenhum login, nenhuma GPU.

## Setup

```bash
bash setup.sh
```

## Onde mais essa cadeia aparece

Ela já vem **embutida** (mesmos valores) nos bundles de edição:
`../image-edit-nano-banana-2/` e `../image-edit-seedream/`, e numa versão
mais leve em `../video-person-replace/`. Este bundle avulso existe para tratar
imagens que **já existem**.
