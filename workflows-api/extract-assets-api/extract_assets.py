#!/usr/bin/env python3
"""extract_assets.py — separa assets de UMA imagem (UI/mockup gerado por IA) em N PNGs transparentes.

Para CADA texto de elemento que você passar, roda o workflow por API:
  LoadImage -> NanoBananaPro_fal (ISOLA o elemento) -> RecraftRemoveBackgroundNode (alpha) -> SaveImage
e baixa 1 PNG transparente. N ilimitado (sem os 5 limites das lanes do workflow visual).

Tudo roda por API (sem GPU): Nano Banana Pro = fal (FAL_KEY) · Recraft = créditos comfy.org (login).
A imagem é enviada UMA vez; só o prompt e o nome de saída mudam por elemento.

Uso:
  python extract_assets.py interface.png "the blue 'Sign in' button" "the user avatar" "the company logo"
  python extract_assets.py interface.png "o card de preço do meio" --out ./assets --resolution 4K
  python extract_assets.py interface.png "ICON: a sacola de compras" --raw-prompt   # prompt já pronto

Requisitos: `requests` (urllib é stdlib). O ComfyUI tem de estar rodando (:8188) com ComfyUI-fal-API
instalado, FAL_KEY configurada e login feito em platform.comfy.org. Ver knowledge-comfyui-api.
"""
import argparse, json, os, re, sys, time, uuid, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WF = os.path.join(HERE, "extract-assets-api.api.json")


def build_prompt(element: str) -> str:
    """Mesma instrução de isolamento usada no workflow visual."""
    return (
        f"Extract ONLY {element} from this user-interface image. "
        "Render it alone, centered, at its original scale, on a plain solid WHITE background, "
        "with nothing else in the frame. Preserve its exact shape, colors, text, icons, corners and "
        "styling; if any part is occluded or cropped behind another element, reconstruct it cleanly. "
        "Flat, front-facing, product-style cutout — no drop shadow, no reflection, no surrounding UI."
    )


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s or "asset")[:60]


def http_json(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers)) as r:
        return json.loads(r.read())


def upload_image(server, path):
    import requests  # multipart é mais simples com requests
    name = os.path.basename(path)
    with open(path, "rb") as f:
        r = requests.post(f"http://{server}/upload/image",
                          files={"image": (name, f, "image/png")},
                          data={"type": "input", "overwrite": "true"})
    r.raise_for_status()
    j = r.json()
    return (j["subfolder"] + "/" + j["name"]) if j.get("subfolder") else j["name"]


def node_id_by_class(wf, class_type):
    for nid, node in wf.items():
        if node.get("class_type") == class_type:
            return nid
    raise SystemExit(f"erro: nó '{class_type}' não está no workflow {DEFAULT_WF}")


def wait_outputs(server, pid, timeout):
    """Poll /history até concluir. Nós de API bloqueiam sem barra; cold-start ~minutos é normal."""
    t0 = time.time()
    while True:
        hist = http_json(f"http://{server}/history/{pid}")
        if pid in hist:
            h = hist[pid]
            status = h.get("status", {})
            if status.get("status_str") == "error":
                msgs = [m for m in status.get("messages", []) if m and m[0] == "execution_error"]
                raise RuntimeError(f"execução falhou: {msgs or status}")
            if h.get("outputs"):
                return h["outputs"]
        if time.time() - t0 > timeout:
            raise TimeoutError(f"timeout ({timeout}s) esperando {pid}")
        time.sleep(2.0)


def download(server, out_dir, outputs, slug):
    saved = []
    imgs = [img for out in outputs.values() for img in out.get("images", []) if img.get("type") != "temp"]
    for k, img in enumerate(imgs):
        q = urllib.parse.urlencode({"filename": img["filename"],
                                    "subfolder": img.get("subfolder", ""),
                                    "type": img.get("type", "output")})
        dst = os.path.join(out_dir, f"{slug}.png" if len(imgs) == 1 else f"{slug}_{k+1}.png")
        with urllib.request.urlopen(f"http://{server}/view?{q}") as r:
            open(dst, "wb").write(r.read())
        saved.append(dst)
    return saved


def main():
    ap = argparse.ArgumentParser(description="Separa assets de uma UI em PNGs transparentes (por API).")
    ap.add_argument("image", help="imagem da interface (UI/mockup)")
    ap.add_argument("elements", nargs="+", help="um texto por elemento a extrair (entre aspas)")
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--out", default="./assets", help="pasta de saída (default ./assets)")
    ap.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    ap.add_argument("--raw-prompt", action="store_true",
                    help="usa cada elemento como o PROMPT completo (não embrulha no template de isolamento)")
    ap.add_argument("--workflow", default=DEFAULT_WF, help="workflow API JSON (default: o do bundle)")
    ap.add_argument("--timeout", type=int, default=600, help="segundos por elemento (cold-start fal)")
    a = ap.parse_args()

    if not os.path.isfile(a.image):
        sys.exit(f"erro: imagem não encontrada: {a.image}")
    wf_tmpl = json.load(open(a.workflow))
    n_load = node_id_by_class(wf_tmpl, "LoadImage")
    n_nano = node_id_by_class(wf_tmpl, "NanoBananaPro_fal")
    n_save = node_id_by_class(wf_tmpl, "SaveImage")
    os.makedirs(a.out, exist_ok=True)

    print(f">> upload {a.image} -> {a.server}")
    img_name = upload_image(a.server, a.image)
    print(f">> {len(a.elements)} elemento(s). Custo ≈ {len(a.elements)}× (Nano Banana Pro fal + Recraft ~US$0.01).")

    ok, fail = 0, 0
    for i, element in enumerate(a.elements, 1):
        slug = slugify(element)
        wf = json.loads(json.dumps(wf_tmpl))  # cópia
        wf[n_load]["inputs"]["image"] = img_name
        wf[n_nano]["inputs"]["prompt"] = element if a.raw_prompt else build_prompt(element)
        wf[n_nano]["inputs"]["resolution"] = a.resolution
        wf[n_save]["inputs"]["filename_prefix"] = f"extract/{slug}"
        print(f"\n[{i}/{len(a.elements)}] {element!r} -> {slug}.png")
        try:
            pid = http_json(f"http://{a.server}/prompt",
                            {"prompt": wf, "client_id": str(uuid.uuid4())})["prompt_id"]
            print(f"    enfileirado {pid} — aguardando (API bloqueia sem barra; cold-start pode levar min)...")
            outputs = wait_outputs(a.server, pid, a.timeout)
            for dst in download(a.server, a.out, outputs, slug):
                print(f"    ✓ salvo: {dst}")
            ok += 1
        except Exception as e:
            print(f"    ✗ falhou: {e}")
            fail += 1

    print(f"\nConcluído — {ok} ok, {fail} falha(s). Assets em: {os.path.abspath(a.out)}/")
    sys.exit(1 if fail and not ok else 0)


if __name__ == "__main__":
    main()
