#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os workflows reformulados de workflows-api/.

Arquitetura nova (o que muda em relacao ao que existia):
  1. Resolucao no MINIMO do modelo (Nano Banana 1K / Seedream Custom 1024).
  2. Multi-referencia de rosto (2 fotos suas) -> trava identidade.
  3. ColorMatchV2 contra a BASE -> mata o efeito colagem.
  4. Cadeia de realismo de celular CALIBRADA (medida localmente) -> mata o look "IA limpa".
  5. Saida dupla: PNG limpo (para encadear) + JPG tratado (entregavel).
"""
import json, os, uuid

ROOT = "/home/ondokai/Projects/comfyui/workflows-api"

# ---------------------------------------------------------------- infra do grafo


class G:
    """Builder minimo de workflow em formato UI do ComfyUI."""

    def __init__(self):
        self.nodes, self.links = [], []
        self._nid, self._lid = 0, 0
        self.groups = []

    def add(self, type_, pos, size, title=None, widgets=None, color=None,
            bgcolor=None, inputs=None, outputs=None, order=None):
        self._nid += 1
        n = {
            "id": self._nid, "type": type_, "pos": list(pos), "size": list(size),
            "flags": {}, "order": order if order is not None else self._nid - 1,
            "mode": 0, "inputs": inputs or [], "outputs": outputs or [],
            "properties": {"Node name for S&R": type_},
            "widgets_values": widgets if widgets is not None else [],
        }
        if title:
            n["title"] = title
        if color:
            n["color"] = color
        if bgcolor:
            n["bgcolor"] = bgcolor
        self.nodes.append(n)
        return n

    def link(self, src, src_slot, dst, dst_slot, type_):
        self._lid += 1
        lid = self._lid
        so = src["outputs"][src_slot]
        so.setdefault("links", [])
        if so["links"] is None:
            so["links"] = []
        so["links"].append(lid)
        dst["inputs"][dst_slot]["link"] = lid
        self.links.append([lid, src["id"], src_slot, dst["id"], dst_slot, type_])
        return lid

    def group(self, title, bounding, color="#3f789e"):
        self.groups.append({
            "id": len(self.groups) + 1, "title": title, "bounding": list(bounding),
            "color": color, "font_size": 24, "flags": {}})

    def dump(self, path):
        d = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, path)),
            "revision": 0, "last_node_id": self._nid, "last_link_id": self._lid,
            "nodes": self.nodes, "links": self.links, "groups": self.groups,
            "config": {}, "extra": {"ds": {"scale": 0.5, "offset": [80, 60]}},
            "version": 0.4,
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print("  wrote", os.path.relpath(path, ROOT))


def IN(name, type_, shape=None, label=None):
    d = {"name": name, "type": type_, "link": None}
    if shape:
        d["shape"] = shape
    if label:
        d["label"] = label
    return d


def OUT(name, type_):
    return {"name": name, "type": type_, "links": []}


def note(g, pos, size, text, title, bg="#653"):
    return g.add("MarkdownNote", pos, size, title=title, widgets=[text],
                 color="#432", bgcolor=bg)


def load_image(g, pos, title):
    return g.add("LoadImage", pos, [260, 340], title=title,
                 widgets=["example.png", "image"],
                 outputs=[OUT("IMAGE", "IMAGE"), OUT("MASK", "MASK")])


# ---------------------------------------------------------------- textos

# Clausula acrescentada a TODOS os prompts: resolve o erro de exposicao que
# denuncia colagem (sujeito bem exposto na frente de janela estourada).
EXPOSURE = (
    "Match the base photograph's EXPOSURE behaviour, not just its colour: if the background is "
    "brighter than the subject, let the subject fall darker and slightly flat exactly as a phone "
    "camera would meter it; if a window or lamp is behind the subject, allow it to clip to white "
    "and spill a little halation onto the subject's edges. Never light the inserted person more "
    "flatteringly than the rest of the frame."
)

PHONE = (
    "Overall look: an ordinary snapshot taken on a modern smartphone by a friend — casual framing, "
    "slightly off-centre, imperfect horizon, natural unposed body language, ordinary ambient light. "
    "Not a studio portrait, not a magazine photo, no cinematic colour grade, no bokeh-heavy "
    "background, no beauty retouching."
)

REALISM = (
    "Re-light every edited element to match the base photograph: light direction, colour "
    "temperature, intensity, contrast and shadow softness. Add correct cast shadows, contact "
    "shadows and bounce light from nearby surfaces. Match the base photo's lens characteristics, "
    "depth of field, motion blur, chromatic aberration, highlight roll-off and film grain. "
    "Preserve skin pores and fabric weave. Photorealistic, no visible seam, no cutout edge, "
    "no plastic or over-smoothed skin."
)

SYSPROMPT = (
    "You are an expert photo-retouching and compositing engine. You must ALWAYS produce an image.\n"
    "Treat every instruction as a literal visual directive. Preserve photographic realism at all "
    "times: keep skin texture, pores, fabric weave, sensor noise and lens characteristics of the "
    "base photograph. Never switch to an illustrated, plastic or over-smoothed look. When "
    "compositing a subject into a scene, always solve light direction, colour temperature, "
    "contrast, cast shadows, contact shadows and bounce light before anything else. The result "
    "must be indistinguishable from an ordinary photograph taken on a consumer smartphone."
)

ID_LOCK = (
    "Image 2 and Image 3 are two photographs of the SAME person (me), from different angles. Use "
    "BOTH to reconstruct my identity in three dimensions — do not copy either one flat. Reproduce "
    "with maximum fidelity: facial geometry and proportions, eye shape and colour, nose, mouth, "
    "jawline, ears, skin tone and texture, moles and blemishes, hairline, hair colour and style, "
    "facial hair, apparent age and body build."
)


# ------------------------------------------------- cadeia de realismo (CALIBRADA)
# Valores medidos localmente (sweep em ~/ComfyUI/output/_c*.jpg). O preset "padrao"
# corresponde ao c2: e o ponto em que volta textura de pele/cabelo sem virar ruido.
PRESETS = {
    "limpo":    dict(ca=0.0,  sharp=0.35, grain_i=0.03, grain_d=0.5, noise=0.006,
                     contrast=0.97, sat=1.06, jpg=92, maxdim=1024),
    "padrao":   dict(ca=0.06, sharp=0.50, grain_i=0.05, grain_d=0.7, noise=0.010,
                     contrast=0.95, sat=1.08, jpg=90, maxdim=896),
    "marcado":  dict(ca=0.10, sharp=0.65, grain_i=0.08, grain_d=1.0, noise=0.016,
                     contrast=0.93, sat=1.10, jpg=85, maxdim=768),
    "luzbaixa": dict(ca=0.08, sharp=0.40, grain_i=0.14, grain_d=1.0, noise=0.030,
                     contrast=0.90, sat=0.98, jpg=80, maxdim=720),
}


def realism_chain(g, src_node, src_slot, base_node, prefix, y=760, x0=1090,
                  preset="padrao"):
    """Anexa a cadeia 'foto de celular'. Devolve o no final (Image Save)."""
    p = PRESETS[preset]
    x = x0

    cm = g.add("ColorMatchV2", [x, y], [300, 130],
               title="1 · Casar a cor com a foto ORIGINAL",
               widgets=["mkl", 0.45, True],
               inputs=[IN("image_target", "IMAGE"), IN("image_ref", "IMAGE")],
               outputs=[OUT("IMAGE", "IMAGE")], color="#232", bgcolor="#353")
    g.link(src_node, src_slot, cm, 0, "IMAGE")
    g.link(base_node, 0, cm, 1, "IMAGE")
    x += 330

    # Limite RIGIDO do lado maior: (a) garante a resolucao baixa que foi pedida,
    # (b) mata o micro-detalhe de IA, (c) impede que uma foto enorme estoure a
    # memoria no no de grao (que supersampleia 4x). Aprendido na marra: uma
    # imagem de 5248x12800 derrubou o ComfyUI aqui.
    sc = g.add("ImageScaleToMaxDimension", [x, y], [290, 82],
               title="2 · Limitar o lado maior (resolucao baixa + trava de memoria)",
               widgets=["area", p["maxdim"]],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(cm, 0, sc, 0, "IMAGE")
    x += 320

    fa = g.add("Image Filter Adjustments", [x, y], [300, 250],
               title="3 · Curva HDR de celular",
               widgets=[0.0, p["contrast"], p["sat"], 1.0, 0, 0.0, 0.0, "false"],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(sc, 0, fa, 0, "IMAGE")
    x += 330

    ca = g.add("Image Chromatic Aberration", [x, y], [300, 180],
               title="4 · Aberracao cromatica da lente",
               widgets=[1, 0, -1, p["ca"], 30],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(fa, 0, ca, 0, "IMAGE")
    x += 330

    sh = g.add("ImageSharpen", [x, y], [280, 130],
               title="5 · Over-sharpening (halo de celular)",
               widgets=[1, 0.45, p["sharp"]],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(ca, 0, sh, 0, "IMAGE")
    x += 310

    fg = g.add("Image Film Grain", [x, y], [280, 150],
               title="6 · Grao / ISO",
               widgets=[p["grain_d"], p["grain_i"], 1.0, 4],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(sh, 0, fg, 0, "IMAGE")
    x += 310

    an = g.add("ImageAddNoise", [x, y], [280, 110],
               title="7 · Ruido de sensor",
               widgets=[7, "fixed", p["noise"]],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(fg, 0, an, 0, "IMAGE")
    x += 310

    sv = g.add("Image Save", [x, y], [340, 500],
               title="8 · Salvar JPG (compressao real de celular)",
               widgets=["", prefix, "_", 4, "false", "jpg", 72, p["jpg"],
                        "true", "false", "false", "false", "false", "false", "true"],
               inputs=[IN("images", "IMAGE")], color="#232", bgcolor="#353")
    g.link(an, 0, sv, 0, "IMAGE")

    g.group("REALISMO DE CELULAR  (local, CPU, custo zero)",
            [x0 - 20, y - 90, (x + 360) - x0 + 20, 620], "#3f5159")
    return sv


# ---------------------------------------------------------------- os 6 processos
def P(body):
    """Fecha todo prompt com as tres clausulas que seguram o realismo."""
    return f"{body}\n\n{EXPOSURE}\n\n{REALISM}\n\n{PHONE}"


PROCESSES = [
    dict(
        slug="trocar-roupa", num=1, nome="TROCAR A ROUPA", refs=1,
        base="a foto da pessoa", ref1="a peca de roupa (ou deixe vazio e descreva no prompt)",
        prompt=P(
            "Change ONLY the clothing worn by the person in Image 1. Dress them in the garment "
            "shown in Image 2 (if a second image is provided); otherwise dress them in: "
            "<DESCREVA AQUI A ROUPA>.\n"
            "Keep pixel-faithful and untouched: the person's face and identity, hair, skin, body "
            "pose, hands, the background, the framing and the camera angle.\n"
            "Make the garment obey the body: correct drape and folds where the fabric falls, "
            "tension where it stretches, occlusion by the arms, and a natural neckline and hem.")),
    dict(
        slug="trocar-objetos-em-cena", num=2, nome="TROCAR OBJETOS EM CENA", refs=1,
        base="a foto da cena", ref1="o objeto novo (ou deixe vazio e descreva no prompt)",
        prompt=P(
            "In Image 1, replace <DESCREVA AQUI O OBJETO A SER TROCADO> with the object shown in "
            "Image 2 (if provided); otherwise with: <DESCREVA AQUI O OBJETO NOVO>.\n"
            "Everything else in the frame must stay pixel-identical: people, background, framing, "
            "camera angle and every other object.\n"
            "Seat the new object physically in the scene: correct scale relative to its "
            "surroundings, correct perspective and vanishing lines, contact shadow where it rests, "
            "and reflections on nearby surfaces.")),
    dict(
        slug="trocar-a-pessoa-da-foto", num=3, nome="TROCAR A PESSOA DA FOTO", refs=2,
        base="a foto/cena original", ref1="a pessoa nova (rosto bem visivel)",
        ref2="a pessoa nova — SEGUNDO angulo (perfil ou 3/4)",
        prompt=P(
            "Replace the person in Image 1 with the person shown in Image 2 and Image 3. Only the "
            "identity changes.\n" + ID_LOCK.replace("(me)", "(the new person)") + "\n"
            "Keep from Image 1, pixel-faithful: the outfit and every garment detail, the exact body "
            "pose, shoulder line, head tilt, gaze direction, hand and finger positions, framing, "
            "camera angle, background and all other people.\n"
            "Adapt the new face and neck to the head angle and perspective of Image 1 — do not "
            "paste a frontal face onto a turned head.")),
    dict(
        slug="me-colocar-na-foto-roupa-da-cena", num=4,
        nome="ME COLOCAR NA FOTO — com a ROUPA e a POSE DA CENA", refs=2,
        base="a foto onde quero entrar", ref1="a MINHA foto (rosto nitido, luz neutra)",
        ref2="a MINHA foto — SEGUNDO angulo (perfil ou 3/4)",
        prompt=P(
            "Replace the person in Image 1 with me, the person shown in Image 2 and Image 3. Only "
            "the identity changes.\n" + ID_LOCK + "\n"
            "Keep from Image 1, pixel-faithful: the outfit and every garment detail, the exact body "
            "pose, shoulder line, head tilt, gaze direction, hand and finger positions, framing, "
            "camera angle, background and all other people.\n"
            "Adapt my face and neck to the head angle and perspective of Image 1 — do not paste a "
            "frontal face onto a turned head. Keep the original head silhouette and hair volume "
            "where the outfit or scene requires it.")),
    dict(
        slug="me-colocar-na-foto-minha-roupa", num=5,
        nome="ME COLOCAR NA FOTO — com a MINHA ROUPA e a MINHA POSE", refs=2,
        base="a cena/foto de destino",
        ref1="a MINHA foto de corpo inteiro (a roupa e a pose a manter)",
        ref2="a MINHA foto — SEGUNDO angulo (rosto nitido)",
        prompt=P(
            "Insert me — the person shown in Image 2 and Image 3 — into the scene of Image 1 as a "
            "new person present in that place.\n" + ID_LOCK + "\n"
            "Carry over from Image 2: my clothing and every garment detail, and my body pose and "
            "posture.\n"
            "Keep from Image 1, pixel-faithful: the background, the location, the framing, the "
            "camera angle and everyone already in the frame. Do not remove anyone.\n"
            "Place me at a plausible spot on the ground plane with correct scale for my distance "
            "from the camera, correct perspective and eye-line, a contact shadow where my feet "
            "meet the floor, and correct occlusion behind any object between me and the lens.")),
    dict(
        slug="trocar-o-local", num=6, nome="TROCAR O LOCAL (+ match de iluminacao)", refs=1,
        base="a foto com a pessoa/objeto a manter",
        ref1="o novo local (ou deixe vazio e descreva no prompt)",
        prompt=P(
            "Keep the person/subject of Image 1 exactly as they are — identity, face, clothing, "
            "pose, hands, hair and body outline must stay pixel-faithful — and place them in the "
            "location shown in Image 2 (if provided); otherwise in: <DESCREVA AQUI O NOVO LOCAL>.\n"
            "Rebuild the environment completely: new background, new ground plane, new horizon, "
            "consistent with the camera height and lens of Image 1.\n"
            "Then re-light the subject to belong to the NEW location: match its light direction, "
            "colour temperature and intensity, and add the cast shadow and contact shadow the new "
            "place would produce.")),
]


# ---------------------------------------------------------------- notas (cards)
HOWTO = """# 🎛️ Como usar

**Processo: {num} · {nome}**

## 1. Suba as imagens (coluna da esquerda)
| Slot | O que subir |
|---|---|
| **BASE** | {base} → vira **Image 1** no prompt |
| **REF 1** | {ref1} → vira **Image 2** |
{ref2row}
> A **ordem importa**: o prompt cita as imagens por posicao (`Image 1`, `Image 2`…).
> E assim que estes modelos identificam quem e a base e quem e a referencia.

## 2. Edite o prompt
Esta em **ingles** de proposito — os modelos seguem instrucao em ingles com bem mais fidelidade.
Onde houver `<DESCREVA AQUI ...>`, troque pelo seu texto.

**Nao apague os 3 paragrafos finais.** Eles resolvem, nesta ordem:
1. **Exposicao** — impede o erro classico de colagem (voce bem exposto na frente de uma
   janela estourada). Foi o defeito visivel nas suas geracoes anteriores.
2. **Luz / lente / grao** — casa sombra, temperatura de cor e caracteristica de lente.
3. **Look de celular** — enquadramento casual, sem cara de estudio.

## 3. Run
Saem **dois** arquivos:
- `output/{clean}` → **PNG limpo**, direto do modelo. Use este para **encadear** noutro processo.
- `output/{final}` → **JPG tratado** pela cadeia de realismo. **Este e o entregavel.**

## 4. Se ainda parecer IA
Aumente o tratamento: no grupo de realismo troque para o preset `marcado`
(veja a nota *Realismo* a direita). O bundle ja vem no preset `padrao`.
"""

REALISM_NOTE = """# 📱 Realismo de celular

Os 8 nos verdes rodam **localmente na CPU** — **custo zero**, nao gastam credito.
Sao eles que tiram o aspecto "IA limpa demais".

## Por que isso e necessario
Pedir grao e ruido **no prompt nao funciona**: o modelo entrega uma imagem
matematicamente limpa (gradientes perfeitos, pele sem poro, tudo igualmente nitido).
Foto de celular de verdade tem uma assinatura de sensor que so se reproduz **depois**.

## Presets (medidos, nao chutados)
| Preset | Quando usar |
|---|---|
| `limpo` | luz boa, quer o minimo de tratamento |
| **`padrao`** ← vem assim | **serve para quase tudo** |
| `marcado` | quando o resultado ainda parece "renderizado" |
| `luzbaixa` | foto de noite / ambiente escuro |

## Como trocar de preset
| No | `limpo` | **`padrao`** | `marcado` | `luzbaixa` |
|---|---|---|---|---|
| 2 · `largest_size` | 1024 | **896** | 768 | 720 |
| 3 · `contrast` | 0.97 | **0.95** | 0.93 | 0.90 |
| 3 · `saturation` | 1.06 | **1.08** | 1.10 | 0.98 |
| 4 · `intensity` (CA) | 0.0 | **0.06** | 0.10 | 0.08 |
| 5 · `alpha` (sharpen) | 0.35 | **0.50** | 0.65 | 0.40 |
| 6 · `intensity` (grao) | 0.03 | **0.05** | 0.08 | 0.14 |
| 7 · `strength` (ruido) | 0.006 | **0.010** | 0.016 | 0.030 |
| 8 · `quality` (JPG) | 92 | **90** | 85 | 80 |

> ⚠️ **Nao exagere.** Testado: aberracao cromatica acima de ~0.15 cria franja
> colorida em toda borda e grao acima de ~0.2 vira chuvisco. Ai para de parecer
> celular e passa a parecer JPEG estragado.

## ⚠️ No 2 — `largest_size` e tambem uma trava de seguranca
Ele limita o **lado maior** e preserva a proporcao. Alem de entregar a resolucao
baixa que voce pediu, ele **protege a memoria**: o no 6 (grao) supersampleia 4x
internamente. Sem esse limite, uma foto muito grande **derruba o ComfyUI** —
aconteceu aqui durante a calibracao, com uma imagem de 5248x12800.

**Nao aumente `largest_size` acima de ~2048.** Se precisar de mais resolucao,
suba antes o `resolution` do modelo e mantenha este no baixo.

## No 1 — `ColorMatchV2`
Puxa a paleta da **sua foto BASE** para o resultado. E o que faz a pessoa inserida
"pertencer" aquela foto. `strength 0.45` e o meio-termo; suba para 0.7 se a cena
tiver uma dominante forte (por-do-sol, luz de restaurante).
"""

CARD_NB2 = """# Nano Banana 2 · Gemini 3.1 Flash Image

**No:** `GeminiNanoBanana2` — `partner/image/Gemini`

## 💳 Como pagar / obter acesso
**Nao usa chave de API.** Billing por **creditos comfy.org**:
1. No ComfyUI: **Settings → User → Login** (ou o botao de conta no topo).
2. Entre/crie conta em `platform.comfy.org`.
3. Compre creditos em **Credits** no painel.
4. Pronto — o no passa a executar. Confira o saldo no proprio painel.

> Alternativa por chave (se preferir sair do comfy.org): existe o no `NanoBanana2_fal`
> (`FAL/Image`), que usa `FAL_KEY`. Veja como pegar a chave no README do bundle de video.

## Ajustes que importam
| Widget | Vem como | Nota |
|---|---|---|
| `resolution` | **`1K`** | **Mudei de 2K para 1K.** E o minimo do modelo: mais barato, e resolucao menor ja ajuda no look de celular. `4K` so na finalizacao. |
| `aspect_ratio` | `auto` | `auto` mantem o formato da sua foto BASE. Mudar aqui **reenquadra**. |
| `thinking_level` | `HIGH` | Deixe **HIGH** para inserir pessoa / casar luz. `MINIMAL` e mais barato mas erra perspectiva e sombra. |
| `seed` | `randomize` | Gostou de um resultado? Troque para `fixed` e anote o numero. Repeticao e *best effort*. |
| `system_prompt` | preenchido | Calibrado para compositing fotorrealista. **Nao apague.** |

## Ate 14 referencias
O `Empilha as imagens` aceita **14** slots. Mais fotos suas (angulos diferentes)
= identidade mais travada. E o motivo de este bundle ja vir com **2 slots de rosto**
nos processos de pessoa.

## Saidas
`IMAGE` (a que usamos) · `STRING` (texto, se `response_modalities=IMAGE+TEXT`) ·
`thought_image` (rascunho do raciocinio — util para depurar por que ele errou).
"""

CARD_SEEDREAM = """# Seedream (ByteDance)

**No:** `ByteDanceSeedreamNode` — `partner/image/ByteDance`

## 💳 Como pagar / obter acesso
**Nao usa chave de API.** Billing por **creditos comfy.org**:
1. No ComfyUI: **Settings → User → Login**.
2. Entre/crie conta em `platform.comfy.org` e compre creditos.

> Alternativa por chave: `SeedreamV4Edit_fal` (`FAL/Image`) usa `FAL_KEY`.
> Direto na ByteDance: `console.byteplus.com` → ModelArk → API keys.

## Ajustes que importam
| Widget | Vem como | Nota |
|---|---|---|
| `size_preset` | **`Custom`** | **Mudei.** Todos os presets prontos comecam em 2048 px. So o `Custom` alcanca o minimo real do modelo. |
| `width` / `height` | **1024 × 1360** | **1024 e o minimo aceito** (o no rejeita menos que isso). 1024×1360 = retrato 3:4, o formato de foto de celular. |
| `model` | `seedream 5.0 lite` | O `lite` e o mais barato e basta para edicao. |
| `watermark` | `false` | Sem marca d'agua. |

## ⚠️ Diferenca importante para o Nano Banana
O Seedream **nao tem `aspect_ratio: auto`** — ele **sempre** entrega no tamanho que voce
pedir. Se a sua foto BASE for **paisagem**, troque para `1360 × 1024`; se for **9:16**,
use `1024 × 1820`. Se voce deixar em retrato uma foto paisagem, ele **reenquadra** e
voce perde as bordas.

> Por causa disso, para "me colocar na foto" o **Nano Banana costuma dar menos trabalho**
> (ele preserva o formato sozinho). Rode os dois e compare — e barato no minimo de resolucao.
"""


# ---------------------------------------------------------------- montagem
ENGINES = {
    "nano-banana-2": dict(
        bundle="image-edit-nano-banana-2", node="GeminiNanoBanana2", card=CARD_NB2,
        label="Nano Banana 2", pfx="nb2",
        outputs=[OUT("IMAGE", "IMAGE"), OUT("STRING", "STRING"),
                 OUT("thought_image", "IMAGE")],
        inputs=[IN("images", "IMAGE", shape=7), IN("files", "GEMINI_INPUT_FILES", shape=7)],
        img_slot=0,
    ),
    "seedream": dict(
        bundle="image-edit-seedream", node="ByteDanceSeedreamNode", card=CARD_SEEDREAM,
        label="Seedream", pfx="sd",
        outputs=[OUT("IMAGE", "IMAGE")],
        inputs=[IN("image", "IMAGE", shape=7)],
        img_slot=0,
    ),
}


def engine_widgets(key, prompt):
    if key == "nano-banana-2":
        # [prompt, model, seed, control_after_generate, aspect_ratio,
        #  resolution, response_modalities, thinking_level, system_prompt]
        return [prompt, "Nano Banana 2 (Gemini 3.1 Flash Image)", 42, "randomize",
                "auto", "1K", "IMAGE", "HIGH", SYSPROMPT]
    # [model, prompt, size_preset, width, height, sequential_image_generation,
    #  max_images, seed, control_after_generate, watermark, fail_on_partial]
    return ["seedream 5.0 lite", prompt, "Custom", 1024, 1360, "disabled", 1, 0,
            "randomize", False, True]


def build_image(ekey, proc):
    e = ENGINES[ekey]
    g = G()
    nrefs = proc["refs"]

    ref2row = (f"| **REF 2** | {proc.get('ref2','')} → vira **Image 3** |"
               if nrefs == 2 else "")
    clean = f"edit/{e['pfx']}_{proc['slug']}_limpo_*.png"
    final = f"edit/{e['pfx']}_{proc['slug']}_FINAL_*.jpg"
    note(g, [-40, -1010], [700, 920],
         HOWTO.format(num=proc["num"], nome=proc["nome"], base=proc["base"],
                      ref1=proc["ref1"], ref2row=ref2row, clean=clean, final=final),
         "LEIA PRIMEIRO")
    note(g, [700, -1010], [580, 920], e["card"], "O modelo · billing")
    note(g, [1320, -1010], [660, 920], REALISM_NOTE, "Realismo de celular", bg="#356")

    base = load_image(g, [0, 60], f"BASE (Image 1) — {proc['base']}")
    refs = [load_image(g, [0, 440], f"REF 1 (Image 2) — {proc['ref1']}")]
    if nrefs == 2:
        refs.append(load_image(g, [0, 820], f"REF 2 (Image 3) — {proc['ref2']}"))

    nslots = 1 + nrefs
    binputs = [IN(f"images.image{i}", "IMAGE", shape=(7 if i else None),
                  label=f"image{i}") for i in range(nslots + 1)]
    batch = g.add("BatchImagesNode", [330, 60], [240, 40 + 26 * (nslots + 1)],
                  title="Empilha as imagens  (ordem = Image 1, 2, 3…)",
                  inputs=binputs, outputs=[OUT("IMAGE", "IMAGE")])
    g.link(base, 0, batch, 0, "IMAGE")
    for i, r in enumerate(refs):
        g.link(r, 0, batch, i + 1, "IMAGE")

    api = g.add(e["node"], [620, 60], [430, 640],
                title=f"{e['label']} — {proc['num']} · {proc['nome']}",
                widgets=engine_widgets(ekey, proc["prompt"]),
                inputs=[dict(x) for x in e["inputs"]],
                outputs=[dict(x, links=[]) for x in e["outputs"]],
                color="#323", bgcolor="#535")
    g.link(batch, 0, api, e["img_slot"], "IMAGE")

    sv = g.add("SaveImage", [1100, 60], [300, 300],
               title="PNG limpo (para encadear noutro processo)",
               widgets=[f"edit/{e['pfx']}_{proc['slug']}_limpo"],
               inputs=[IN("images", "IMAGE")])
    g.link(api, 0, sv, 0, "IMAGE")

    realism_chain(g, api, 0, base, f"edit/{e['pfx']}_{proc['slug']}_FINAL",
                  y=760, x0=1100, preset="padrao")

    g.group("1 · ENTRADAS", [-30, -10, 320, 380 * nslots + 20], "#3f789e")
    g.group("2 · EDICAO NO MODELO (paga credito)", [310, -10, 760, 730], "#88A")
    g.dump(os.path.join(ROOT, e["bundle"],
                        f"{e['bundle']}_{proc['slug']}.json"))




# ======================================================================
# BUNDLE: video-person-replace
# ======================================================================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bundle NOVO: trocar a pessoa de um video que EU forneco.

Diferenca central para o bundle antigo (Seedance 2.0 reference):
  - Seedance GERA um video novo a partir de referencias; a coreografia e dele.
  - Wan 2.2 Animate /replace RECEBE o meu video e troca a pessoa dentro dele,
    mantendo o movimento, o enquadramento e o corte originais.
Alem disso: preserva o AUDIO original e o FPS original.
"""

BUNDLE_VID = "video-person-replace"


def widget_in(name, type_):
    return {"name": name, "type": type_, "widget": {"name": name}, "link": None}


HOWTO_VID = """# 🎬 Trocar a pessoa de um video que EU forneco

**Voce da o video. O modelo troca quem aparece nele por VOCE.**
O movimento, o enquadramento, os cortes e a duracao do **seu** video sao mantidos.

## O que subir
| Slot | O que subir |
|---|---|
| **MINHA FOTO** | Uma foto sua, **corpo inteiro**, de frente, rosto nitido, luz neutra, **uma pessoa so** |
| **VIDEO ORIGINAL** | O video onde a pessoa vai ser trocada. **Uma pessoa em cena** funciona muito melhor |

## Regras que mudam o resultado
- **Corpo inteiro na foto.** O modelo precisa ver seu tronco e pernas para vestir
  o seu corpo no movimento. Foto so do rosto → corpo inventado.
- **Video curto.** Comece com **3–6 s**. Custo e risco crescem por segundo.
- **Uma pessoa em cena.** Com varias pessoas ele pode trocar a errada.
- **Roupa parecida ajuda.** Se a pessoa do video usa manga longa e voce esta de
  regata na foto, ele improvisa.

## Resolucao
Ja vem em **`480p`** — o mais baixo do modelo, e o mais barato. Foi pedido de proposito:
480p tambem **ajuda** no look de video de celular. Suba para `720p` so na versao final.

## O que sai
`output/video/replace_*.mp4` — com o **audio original** e o **fps original** preservados.

## Se der erro
| Sintoma | Causa | Correcao |
|---|---|---|
| No vermelho | Falta o pacote fal | Veja o card de chave ao lado |
| `401` / `Unauthorized` | `FAL_KEY` ausente ou invalida | Card ao lado |
| Trocou a pessoa errada | Varias pessoas em cena | Corte o trecho com so uma pessoa |
| Corpo estranho | Foto so do rosto | Use foto de corpo inteiro |
| Video acelerado/lento | fps nao casou | O `fps` ja vem ligado ao video de origem; nao desligue |
"""

KEYCARD = """# 🔑 Chave de API — fal.ai

Este bundle **nao** usa creditos comfy.org. Usa a **fal.ai**, que cobra por execucao.

## Como pegar a chave (5 min)
1. Acesse **https://fal.ai** e crie a conta (login com Google/GitHub serve).
2. Va em **https://fal.ai/dashboard/keys**.
3. Clique em **Add key** → copie o valor (formato `xxxxxxxx-xxxx-...:xxxxxxxxxxxx`).
   ⚠️ Ele so aparece **uma vez**.
4. Adicione credito em **https://fal.ai/dashboard/billing** (cartao; da para comecar com pouco).

## Onde colocar a chave
No arquivo `~/ComfyUI/secrets.env` (permissao `600`, **nunca** commitado):
```bash
FAL_KEY=cole-a-chave-aqui
```
Depois **reinicie o ComfyUI** para ele reler o arquivo.

> ✅ Neste computador o `FAL_KEY` **ja esta carregado** no processo do ComfyUI.
> Se os nos falharem com `401`, a chave expirou ou acabou o credito.

## Custo
Cobrado por segundo de video gerado; **480p custa bem menos que 720p**.
Confira o preco corrente na pagina do modelo:
**https://fal.ai/models/fal-ai/wan/v2.2-14b/animate/replace**

## Alternativas (mesma chave `FAL_KEY`)
| No | Para que serve |
|---|---|
| `PixverseSwapNode_fal` | Swap mais simples, aceita **360p**, e **mantem o audio** sozinho |
| `KlingOmniVideoToVideoReference_fal` | Edicao de video por referencia (Kling) |
| `WanVACEVideoEdit_fal` | Edicao de video por mascara/controle (VACE) |

## Sem chave nenhuma?
O bundle irmao `../video-person-swap-seedance-2/` roda por **creditos comfy.org**
(so login, sem chave) — mas ele **gera** um video novo em vez de editar o seu.
"""

MODELCARD = """# Wan 2.2 Animate 14B · modo *replace*

**No:** `Wan2214b_animate_replace_character_fal` — `FAL/VideoGeneration`

## Por que este e nao o Seedance
| | Wan Animate *replace* | Seedance 2.0 *reference* |
|---|---|---|
| Recebe o **seu** video | ✅ sim, e edita ele | ⚠️ usa como referencia |
| Mantem o movimento original | ✅ | ❌ recria |
| Mantem enquadramento/cortes | ✅ | ❌ |
| Precisa de prompt | ❌ nenhum | ✅ obrigatorio |
| Passo manual de `asset_id` | ❌ | ✅ copiar/colar |

Ele deriva o movimento e a expressao **do proprio video**; por isso **nao tem
campo de prompt**. Menos coisa para errar.

## Widgets que importam
| Widget | Vem como | Nota |
|---|---|---|
| `resolution` | **`480p`** | O mais baixo — mais barato e ja parece video de celular |
| `turbo` | `True` | Bem mais rapido/barato. Desligue so se a qualidade nao servir |
| `num_inference_steps` | `20` | Com `turbo` ligado, subir daqui rende pouco |
| `guidance_scale` | `1.0` | **Nao mexa.** Este modelo e destilado: `>1` borra o video |
| `shift` | `8` | Padrao do modelo |
| `video_quality` | `high` | Qualidade do encode (nao da geracao) |
| `variations` | `1` | `>1` multiplica o custo |

## Saidas
`video_url` (usamos esta) · `frames_zip_url` (so se `return_frames_zip=True`).

## Encadeamento no grafo
`video_url` (texto) → `Load Video (URL)` traz os quadros de volta para o ComfyUI →
`Create Video` remonta usando o **audio** e o **fps do seu video original** →
`Save Video` grava o mp4.
"""

GRAIN_NOTE = """# 📱 Grao de celular (opcional)

Tres nos locais (CPU, **custo zero**) que dao ao resultado a assinatura de
video gravado no celular. O Wan em 480p ja entrega algo proximo; isto so fecha.

| No | Faz |
|---|---|
| `Image Filter Adjustments` | curva HDR de celular (sombra levantada, satura leve) |
| `Image Film Grain` | grao / ruido de ISO |
| `ImageAddNoise` | ruido de sensor |

> ⏱️ **Roda quadro a quadro na CPU.** Num clipe de 5 s (~80 quadros) leva
> alguns minutos. **Com pressa? Apague os tres** e ligue `Load Video (URL) → frames`
> direto no `Create Video`: o video sai igual, sem o tratamento.

> `supersample_factor` esta em **1** de proposito (em imagem parada uso 4).
> Em video, 4 multiplica o tempo por ~16 sem ganho visivel a 480p.
"""


def build_wan():
    g = G()
    note(g, [-40, -1060], [700, 980], HOWTO_VID, "LEIA PRIMEIRO")
    note(g, [700, -1060], [600, 980], KEYCARD, "🔑 Como pegar a chave", bg="#563")
    note(g, [1330, -1060], [620, 980], MODELCARD, "O modelo")
    note(g, [1980, -1060], [560, 980], GRAIN_NOTE, "Grao de celular", bg="#356")

    eu = load_image(g, [0, 60], "MINHA FOTO — corpo inteiro, rosto nitido, 1 pessoa")
    vid = g.add("LoadVideo", [0, 440], [300, 120],
                title="VIDEO ORIGINAL — a pessoa a ser trocada (comece com 3-6 s)",
                widgets=["", "video"], outputs=[OUT("VIDEO", "VIDEO")])

    wan = g.add("Wan2214b_animate_replace_character_fal", [360, 60], [400, 520],
                title="Wan 2.2 Animate · REPLACE — troca a pessoa mantendo o movimento",
                widgets=["", True, "480p", 24, 20, 1.0, 8, "high", "balanced",
                         True, False, False, 1],
                inputs=[IN("image", "IMAGE"), IN("video", "VIDEO", shape=7)],
                outputs=[OUT("video_url", "STRING"), OUT("frames_zip_url", "STRING")],
                color="#432", bgcolor="#653")
    g.link(eu, 0, wan, 0, "IMAGE")
    g.link(vid, 0, wan, 1, "VIDEO")

    # audio + fps do video ORIGINAL
    comp = g.add("GetVideoComponents", [360, 620], [300, 120],
                 title="Pega o AUDIO do video original",
                 inputs=[IN("video", "VIDEO")],
                 outputs=[OUT("images", "IMAGE"), OUT("audio", "AUDIO"),
                          OUT("fps", "FLOAT"), OUT("bit_depth", "INT")])
    g.link(vid, 0, comp, 0, "VIDEO")

    # url -> quadros
    lv = g.add("LoadVideoURL", [810, 60], [360, 260],
               title="Traz o resultado de volta (url → quadros)",
               widgets=["https://example.com/video.mp4", 0, "Disabled", 512, 512,
                        0, 0, 1],
               inputs=[widget_in("url", "STRING")],
               outputs=[OUT("frames", "IMAGE"), OUT("frame_count", "INT"),
                        OUT("video_info", "VHS_VIDEOINFO")])
    g.link(wan, 0, lv, 0, "STRING")

    info = g.add("VHS_VideoInfoLoaded", [810, 360], [300, 140],
                 title="fps real do resultado",
                 inputs=[IN("video_info", "VHS_VIDEOINFO")],
                 outputs=[OUT("fps", "FLOAT"), OUT("frame_count", "INT"),
                          OUT("duration", "FLOAT"), OUT("width", "INT"),
                          OUT("height", "INT")])
    g.link(lv, 2, info, 0, "VHS_VIDEOINFO")

    # --- grao de celular (leve, quadro a quadro) ---
    p = PRESETS["padrao"]
    fa = g.add("Image Filter Adjustments", [1220, 60], [300, 250],
               title="Curva HDR de celular",
               widgets=[0.0, p["contrast"], p["sat"], 1.0, 0, 0.0, 0.0, "false"],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(lv, 0, fa, 0, "IMAGE")
    fg = g.add("Image Film Grain", [1550, 60], [280, 150], title="Grao / ISO",
               widgets=[0.5, 0.04, 1.0, 1],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(fa, 0, fg, 0, "IMAGE")
    an = g.add("ImageAddNoise", [1860, 60], [280, 110], title="Ruido de sensor",
               widgets=[7, "fixed", 0.008],
               inputs=[IN("image", "IMAGE")], outputs=[OUT("IMAGE", "IMAGE")],
               color="#232", bgcolor="#353")
    g.link(fg, 0, an, 0, "IMAGE")

    # remontar: images + audio original + fps do resultado
    cv = g.add("CreateVideo", [2180, 60], [320, 150],
               title="Remonta o video (audio original + fps real)",
               widgets=[30.0, 8],
               inputs=[IN("images", "IMAGE"), IN("audio", "AUDIO", shape=7),
                       widget_in("fps", "FLOAT")],
               outputs=[OUT("VIDEO", "VIDEO")])
    g.link(an, 0, cv, 0, "IMAGE")
    g.link(comp, 1, cv, 1, "AUDIO")
    g.link(info, 0, cv, 2, "FLOAT")

    sv = g.add("SaveVideo", [2540, 60], [340, 380], title="Salvar o mp4",
               widgets=["video/replace", "auto", "auto"],
               inputs=[IN("video", "VIDEO")])
    g.link(cv, 0, sv, 0, "VIDEO")

    g.group("1 · ENTRADAS", [-30, -10, 350, 620], "#3f789e")
    g.group("2 · TROCA (paga fal.ai)", [340, -10, 440, 780], "#a53")
    g.group("3 · VOLTA PARA O COMFYUI", [790, -10, 400, 520], "#88A")
    g.group("4 · GRAO DE CELULAR (CPU, gratis — pode apagar)",
            [1200, -10, 960, 340], "#3f5159")
    g.group("5 · SAIDA", [2160, -10, 740, 460], "#353")
    g.dump(os.path.join(ROOT, BUNDLE_VID, f"{BUNDLE_VID}_wan-animate.json"))


PIX_HOWTO = """# 🎬 Alternativa barata — Pixverse Swap (360p)

Mesmo objetivo do arquivo principal (`_wan-animate.json`), com outro modelo.

## Quando usar este
- Quer o **mais barato / mais rapido** possivel (aceita **360p**).
- Quer que o **audio original venha junto automaticamente**
  (`original_sound_switch=True` — nao precisa remontar nada).

## Quando usar o Wan Animate
- Quando a **semelhanca** importa mais que o preco. O Wan costuma segurar melhor
  o rosto ao longo do clipe.

## O que subir
| Slot | O que |
|---|---|
| **MINHA FOTO** | rosto bem visivel, de frente |
| **VIDEO ORIGINAL** | o video onde a pessoa sera trocada |

## Widgets
| Widget | Vem como | Nota |
|---|---|---|
| `mode` | `person` | `object` e `background` trocam outras coisas |
| `quality` | **`360p`** | o mais baixo. `540p`/`720p` custam mais |
| `keyframe_id` | `1` | qual pessoa trocar quando ha mais de uma em cena |
| `original_sound_switch` | `True` | mantem o audio do video original |

Chave: a **mesma** `FAL_KEY` do arquivo principal — veja o card la.

> Este arquivo entrega a **url** do video pronto (com audio). Baixe pelo link
> mostrado no `Preview`, ou ligue o `Load Video (URL)` como no arquivo principal.
"""


def build_pixverse():
    g = G()
    note(g, [-40, -760], [700, 680], PIX_HOWTO, "LEIA PRIMEIRO")
    eu = load_image(g, [0, 60], "MINHA FOTO — rosto bem visivel")
    vid = g.add("LoadVideo", [0, 440], [300, 120], title="VIDEO ORIGINAL",
                widgets=["", "video"], outputs=[OUT("VIDEO", "VIDEO")])
    px = g.add("PixverseSwapNode_fal", [360, 60], [380, 260],
               title="Pixverse Swap — person @ 360p (audio original incluso)",
               widgets=["person", 1, "360p", True, ""],
               inputs=[IN("image", "IMAGE"), IN("video", "VIDEO", shape=7)],
               outputs=[OUT("video_url", "STRING")],
               color="#432", bgcolor="#653")
    g.link(eu, 0, px, 0, "IMAGE")
    g.link(vid, 0, px, 1, "VIDEO")
    pv = g.add("PreviewAny", [800, 60], [400, 140],
               title="URL do video pronto — clique e baixe",
               inputs=[IN("source", "*")])
    g.link(px, 0, pv, 0, "STRING")
    g.group("1 · ENTRADAS", [-30, -10, 350, 620], "#3f789e")
    g.group("2 · SWAP (paga fal.ai)", [340, -10, 420, 400], "#a53")
    g.dump(os.path.join(ROOT, BUNDLE_VID, f"{BUNDLE_VID}_pixverse-360p.json"))




# ======================================================================
# BUNDLE: foto-realismo-celular
# ======================================================================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bundle avulso: aplica a cadeia de realismo em QUALQUER foto ja existente.

Serve para tratar resultados antigos (as geracoes que ficaram com cara de IA)
sem gastar um unico credito: roda inteiro na CPU local."""

BUNDLE_REAL = "foto-realismo-celular"

HOWTO_REAL = """# 📱 Deixar uma foto com cara de foto de celular

**Custo zero.** Roda 100% na CPU local — nenhum credito, nenhuma chave de API,
nenhuma GPU. Nao chama modelo nenhum.

## Para que serve
Pega **qualquer imagem** — inclusive as suas geracoes antigas que ficaram com
cara de IA — e aplica a assinatura de captura de um celular.

## Por que isso e necessario
Modelo de imagem entrega uma imagem **matematicamente limpa**: gradiente perfeito,
pele sem poro, tudo igualmente nitido, zero ruido de sensor. E esse conjunto que
o olho le como "IA", mesmo quando a composicao esta impecavel.

Pedir grao **no prompt nao resolve** — o modelo desenha uma imitacao de grao, nao
produz a assinatura real do sensor. Ela so entra **depois**, em pixel.

## Como usar
1. Suba a imagem no `FOTO` (esquerda).
2. *(Opcional)* Suba uma **foto de referencia de cor** no `REF DE COR` — pode ser
   uma foto sua de verdade, tirada no celular. O `ColorMatchV2` puxa a paleta dela.
   **Sem referencia, ligue a mesma foto nos dois** (ja vem assim).
3. Run. Sai em `output/celular/`.

## Presets
Vem no **`padrao`**. A tabela completa com os 4 presets esta na nota verde ao lado.

| Preset | Quando |
|---|---|
| `limpo` | so tirar o aspecto plastico |
| **`padrao`** | **serve para quase tudo** |
| `marcado` | quando ainda parece renderizado |
| `luzbaixa` | simular foto noturna / ambiente escuro |

## ⚠️ Limite de tamanho
O no de grao supersampleia **4x** internamente. O no 2 (`largest_size`) segura o
lado maior justamente para isso nao estourar a memoria.
**Nao passe `largest_size` de ~2048** — uma imagem de 5248x12800 derrubou o
ComfyUI durante a calibracao deste bundle.
"""


def build_realismo():
    g = G()
    note(g, [-40, -900], [700, 820], HOWTO_REAL, "LEIA PRIMEIRO")
    foto = load_image(g, [0, 60], "FOTO — a imagem a tratar")
    ref = load_image(g, [0, 440], "REF DE COR — (opcional) uma foto sua de celular")
    realism_chain(g, foto, 0, ref, "celular/foto", y=60, x0=340, preset="padrao")
    g.group("ENTRADA", [-30, -10, 320, 760], "#3f789e")
    g.dump(os.path.join(ROOT, BUNDLE_REAL, f"{BUNDLE_REAL}_tratar-foto.json"))




# ======================================================================
def main():
    print("image-edit-nano-banana-2 / image-edit-seedream")
    for ekey in ENGINES:
        for proc in PROCESSES:
            build_image(ekey, proc)
    print(BUNDLE_VID)
    build_wan()
    build_pixverse()
    print(BUNDLE_REAL)
    build_realismo()
    print("\nOK. Agora rode: python3 scripts/validate_workflows.py")


if __name__ == "__main__":
    main()
