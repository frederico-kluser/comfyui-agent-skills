#!/usr/bin/env python3
"""run_api.py — roda um workflow do ComfyUI pela API HTTP (sem abrir a UI).

Faz: upload da imagem (e máscara) -> injeta no workflow API JSON -> POST /prompt ->
espera concluir (poll /history) -> baixa os outputs (/view).

IMPORTANTE: o --workflow deve ser o JSON em FORMATO API ("Save (API Format)" com Dev mode ON),
não o JSON da UI. Ver knowledge-comfyui-api / docs/image-editing.md §3.5.

Uso:
  python run_api.py --workflow wf_api.json --image original.png --out-dir out/ \
                    --image-node 10 --seed 12345 [--mask mask.png --mask-node 11] \
                    [--prompt "a red sports car" --prompt-node 6]
Requisitos: requests  (urllib é stdlib). WebSocket é opcional (este cliente faz polling).
"""
import argparse, json, os, time, uuid, urllib.request, urllib.parse


def http_json(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def upload_image(server, path, image_type="input", overwrite=True):
    import requests
    name = os.path.basename(path)
    with open(path, "rb") as f:
        r = requests.post(f"http://{server}/upload/image",
                          files={"image": (name, f, "image/png")},
                          data={"type": image_type, "overwrite": str(overwrite).lower()})
    r.raise_for_status()
    j = r.json()
    # ComfyUI devolve {"name","subfolder","type"}; o LoadImage usa "name" (ou "subfolder/name")
    return (j["subfolder"] + "/" + j["name"]) if j.get("subfolder") else j["name"]


def main():
    ap = argparse.ArgumentParser(description="Roda um workflow ComfyUI (API format) por HTTP.")
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--workflow", required=True, help="JSON em formato API")
    ap.add_argument("--image", help="imagem de entrada (upload)")
    ap.add_argument("--image-node", help="id do nó LoadImage que recebe --image")
    ap.add_argument("--mask", help="máscara (upload, opcional)")
    ap.add_argument("--mask-node", help="id do nó LoadImage(Mask) que recebe --mask")
    ap.add_argument("--prompt", help="texto (opcional)")
    ap.add_argument("--prompt-node", help="id do nó CLIPTextEncode que recebe --prompt")
    ap.add_argument("--seed", type=int, help="seed (muda p/ não cair no cache)")
    ap.add_argument("--seed-node", help="id do nó do sampler p/ a seed")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args()

    wf = json.load(open(a.workflow))

    def set_input(node_id, key, val):
        if node_id and node_id in wf:
            wf[node_id]["inputs"][key] = val
        elif node_id:
            print(f"aviso: nó {node_id} não existe no workflow")

    if a.image:
        name = upload_image(a.server, a.image)
        set_input(a.image_node, "image", name)
    if a.mask:
        mname = upload_image(a.server, a.mask)
        set_input(a.mask_node, "image", mname)
    if a.prompt is not None:
        set_input(a.prompt_node, "text", a.prompt)
    if a.seed is not None:
        set_input(a.seed_node, "seed", a.seed)

    client_id = str(uuid.uuid4())
    pid = http_json(f"http://{a.server}/prompt", {"prompt": wf, "client_id": client_id})["prompt_id"]
    print(f"enfileirado: {pid}  — aguardando...")

    while True:                                    # poll /history até concluir
        hist = http_json(f"http://{a.server}/history/{pid}")
        if pid in hist and hist[pid].get("outputs"):
            break
        time.sleep(1.0)

    os.makedirs(a.out_dir, exist_ok=True)
    saved = 0
    for _node, out in hist[pid]["outputs"].items():
        for img in out.get("images", []):
            q = urllib.parse.urlencode({"filename": img["filename"],
                                        "subfolder": img.get("subfolder", ""),
                                        "type": img.get("type", "output")})
            with urllib.request.urlopen(f"http://{a.server}/view?{q}") as r:
                open(os.path.join(a.out_dir, img["filename"]), "wb").write(r.read())
            saved += 1
            print(f"  salvo: {a.out_dir}/{img['filename']}")
    print(f"OK — {saved} imagem(ns).")


if __name__ == "__main__":
    main()
