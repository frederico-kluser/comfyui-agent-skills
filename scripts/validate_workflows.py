#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida workflows UI do ComfyUI contra o /object_info AO VIVO.

Uso:  python3 scripts/validate_workflows.py [glob ...]
      COMFY_URL=http://host:8188 python3 scripts/validate_workflows.py

Checa: tipo de no existe, contagem de widgets, slots de link validos,
tipos casando ponta a ponta e ausencia de link orfao."""
import json, sys, glob, os, urllib.request

COMFY = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")


def load_object_info():
    """Le o /object_info AO VIVO -- e a unica fonte de verdade sobre quais nos
    existem nesta instalacao e qual a assinatura de widgets de cada um."""
    try:
        with urllib.request.urlopen(f"{COMFY}/object_info", timeout=180) as r:
            return json.loads(r.read())
    except Exception as e:
        sys.exit(f"ERRO: nao consegui ler {COMFY}/object_info ({e}).\n"
                 f"Suba o ComfyUI (ou ajuste COMFY_URL) e rode de novo.")


OI = load_object_info()

LINKY = {"IMAGE", "MASK", "VIDEO", "AUDIO", "LATENT", "MODEL", "CLIP", "VAE",
         "CONDITIONING", "GEMINI_INPUT_FILES", "COMFY_AUTOGROW_V3",
         "VHS_VIDEOINFO", "STITCHER", "RUNWAY_ALEPH2_KEYFRAME",
         "RUNWAY_ALEPH2_PROMPT_IMAGE", "SEGS", "BBOX", "SAM3_MODEL", "*"}


def widget_spec(ntype):
    """Devolve a lista de widgets esperados, na ordem, para um class_type."""
    if ntype not in OI:
        return None
    out = []
    inp = OI[ntype]["input"]
    for grp in ("required", "optional"):
        for name, spec in inp.get(grp, {}).items():
            t = spec[0]
            o = spec[1] if len(spec) > 1 and isinstance(spec[1], dict) else {}
            if isinstance(t, str) and t in LINKY:
                continue
            out.append(name)
            if o.get("control_after_generate"):
                out.append(f"{name}__control")
            # combos de upload ganham um widget extra de botao no frontend
            if o.get("image_upload") or o.get("video_upload"):
                out.append(f"{name}__upload")
    return out


def check(path):
    errs, warns = [], []
    d = json.load(open(path))
    nodes = {n["id"]: n for n in d["nodes"]}

    for n in d["nodes"]:
        t = n["type"]
        if t == "MarkdownNote":
            continue
        if t not in OI:
            errs.append(f"node {n['id']} tipo INEXISTENTE no servidor: {t}")
            continue
        exp = widget_spec(t)
        got = n.get("widgets_values", [])
        # AUTOGROW/dynamic combos tornam a contagem variavel -> so avisa
        raw = json.dumps(OI[t]["input"])
        dynamic = "AUTOGROW" in raw or "DYNAMICCOMBO" in raw
        if not dynamic and len(got) < len(exp):
            # faltar widget desalinha os valores -> quebra de verdade
            errs.append(
                f"node {n['id']} ({t}): {len(got)} widgets, esperado {len(exp)} -> {exp}")
        elif not dynamic and len(got) > len(exp):
            # sobra e tolerado pelo ComfyUI (valores legados)
            warns.append(f"node {n['id']} ({t}): {len(got)} widgets > {len(exp)}")
        # slots de saida declarados batem?
        decl = OI[t].get("output", [])
        if len(n.get("outputs", [])) > len(decl):
            errs.append(f"node {n['id']} ({t}): {len(n['outputs'])} outputs "
                        f"declarados, servidor tem {len(decl)}")

    seen = set()
    for l in d["links"]:
        lid, src, sslot, dst, dslot, ltype = l
        seen.add(lid)
        if src not in nodes:
            errs.append(f"link {lid}: origem {src} nao existe"); continue
        if dst not in nodes:
            errs.append(f"link {lid}: destino {dst} nao existe"); continue
        sn, dn = nodes[src], nodes[dst]
        if sslot >= len(sn.get("outputs", [])):
            errs.append(f"link {lid}: slot de saida {sslot} invalido em {sn['type']}")
        elif sn["outputs"][sslot]["type"] not in (ltype, "*"):
            errs.append(f"link {lid}: tipo {ltype} != saida "
                        f"{sn['outputs'][sslot]['type']} ({sn['type']})")
        if dslot >= len(dn.get("inputs", [])):
            errs.append(f"link {lid}: slot de entrada {dslot} invalido em {dn['type']}")
        elif dn["inputs"][dslot]["type"] not in (ltype, "*"):
            errs.append(f"link {lid}: tipo {ltype} != entrada "
                        f"{dn['inputs'][dslot]['type']} ({dn['type']})")

    for n in d["nodes"]:
        for i, inp in enumerate(n.get("inputs", [])):
            lk = inp.get("link")
            if lk is not None and lk not in seen:
                errs.append(f"node {n['id']} ({n['type']}) input {inp['name']}: "
                            f"link {lk} orfao")
        for o in n.get("outputs", []):
            for lk in (o.get("links") or []):
                if lk not in seen:
                    errs.append(f"node {n['id']} output {o['name']}: link {lk} orfao")

    if d.get("last_node_id", 0) < max(nodes) if nodes else 0:
        warns.append("last_node_id menor que o maior id de no")
    return errs, warns


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.join(os.path.dirname(here), "workflows-api", "*", "*.json")
    pats = sys.argv[1:] or [default]
    files = sorted(f for p in pats for f in glob.glob(p))
    bad = 0
    for f in files:
        e, w = check(f)
        name = os.path.relpath(f, os.path.join(os.path.dirname(here), "workflows-api"))
        if e:
            bad += 1
            print(f"\n❌ {name}")
            for x in e[:12]:
                print("   ", x)
        else:
            print(f"✅ {name}" + (f"  ({len(w)} avisos)" if w else ""))
    print(f"\n{len(files) - bad}/{len(files)} OK")
    sys.exit(1 if bad else 0)
