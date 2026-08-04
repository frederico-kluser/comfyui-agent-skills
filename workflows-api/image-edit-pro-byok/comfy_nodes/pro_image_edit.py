"""Pro Image Edit BYOK — os melhores editores de imagem por API, num no so.

Por que existe: o bundle `image-edit-nano-banana-2` roda em UM modelo (Gemini) e em
`1K`. Quando o modelo erra o rosto, nao ha para onde ir. Aqui o modelo e um dropdown:
o MESMO prompt e as MESMAS referencias atravessam quatro motores diferentes, entao da
para decidir qual acerta o SEU rosto — que e a unica medida que importa.

Contratos extraidos do OpenAPI ao vivo da fal em 2026-08-04. Todos os quatro aceitam
`prompt` + `image_urls`, mas divergem em tudo o mais (tamanho, seed, teto de refs),
e o no normaliza essas diferencas.

Reconferir um schema:
  curl -s "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>" | jq .
"""

from __future__ import annotations

import io
import os
import time

import numpy as np
import torch
from PIL import Image, ImageOps

import folder_paths

try:  # disponivel dentro do ComfyUI
    import comfy.model_management as model_management
except Exception:  # pragma: no cover
    model_management = None


# --------------------------------------------------------------------------- #
# Catalogo de modelos                                                          #
# --------------------------------------------------------------------------- #
#
# capabilities por modelo:
#   size_mode : 'image_size'  -> manda image_size (string preset)
#               'resolution'  -> manda resolution ('1K'|'2K'|'4K') + aspect_ratio
#   max_px    : teto de resolucao efetivo (para avisar quando o pedido for clampeado)
#   seed      : aceita seed?
#   system    : aceita system_prompt?
#   safety    : maior valor aceito em safety_tolerance (None = nao aceita)
#   mask      : aceita mask_url?
#   max_refs  : teto documentado de imagens de referencia

MODELS = {
    "Seedream 5.0 Pro — 10 referências (padrão p/ rosto)": {
        "endpoint": "bytedance/seedream/v5/pro/edit",
        "size_mode": "image_size",
        "max_res": "2K",
        "seed": False,
        "system": False,
        "safety": None,
        "mask": False,
        "max_refs": 10,
    },
    "FLUX.2 Pro — melhor pele e anatomia": {
        "endpoint": "fal-ai/flux-2-pro/edit",
        "size_mode": "image_size",
        "max_res": "auto",
        "seed": True,
        "system": False,
        "safety": 5,
        "mask": False,
        "max_refs": 10,
    },
    "Nano Banana Pro — Gemini 3 Pro, até 4K": {
        "endpoint": "fal-ai/nano-banana-pro/edit",
        "size_mode": "resolution",
        "max_res": "4K",
        "seed": True,
        "system": True,
        "safety": 6,
        "mask": False,
        "max_refs": 14,
    },
    "GPT Image 2 — 16 referências + máscara": {
        "endpoint": "openai/gpt-image-2/edit",
        "size_mode": "image_size",
        "max_res": "auto",
        "seed": False,
        "system": False,
        "safety": None,
        "mask": True,
        "max_refs": 16,
        "quality": True,
    },
    "Seedream 5.0 Lite — rascunho barato": {
        "endpoint": "bytedance/seedream/v5/lite/edit",
        "size_mode": "image_size",
        "max_res": "2K",
        "seed": False,
        "system": False,
        "safety": None,
        "mask": False,
        "max_refs": 10,
    },
}
MODEL_NAMES = list(MODELS)

RESOLUTIONS = ["auto (recomendado)", "1K", "2K", "4K"]
ASPECT_RATIOS = ["auto", "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"]

POLL_SECONDS = 2.0

# --------------------------------------------------------------------------- #
# Rotas de pagamento                                                           #
# --------------------------------------------------------------------------- #
#
# ROTA_FAL     — a sua FAL_KEY. Todos os 5 modelos do dropdown.
# ROTA_COMFY   — os creditos que voce ja pagou no comfy.org. Só existe partner para
#                UM dos motores deste bundle (Seedream), entao a rota forca esse
#                modelo e diz isso no console em vez de falhar em silencio.
#
# Mecanismo (lido do proprio ComfyUI instalado, nao inferido):
#   - `execution.py` injeta o token quando o no declara
#     "hidden": {"auth_token": "AUTH_TOKEN_COMFY_ORG"}
#   - header: Authorization: Bearer <token>   (ou X-API-KEY com a api key)
#   - base:   https://api.comfy.org           (--comfy-api-base sobrescreve)
#   - upload: POST /customers/storage -> {upload_url, download_url}; depois PUT
#   - Seedream: POST /proxy/byteplus/api/v3/images/generations

ROTA_FAL = "Minha chave (fal.ai)"
ROTA_COMFY = "Créditos comfy.org (login) — só Seedream"
ROTAS = [ROTA_FAL, ROTA_COMFY]

COMFY_API_BASE = "https://api.comfy.org"
COMFY_SEEDREAM_ENDPOINT = "/proxy/byteplus/api/v3/images/generations"
COMFY_UPLOAD_ENDPOINT = "/customers/storage"

# Modelo partner e o piso de pixels que ele valida no cliente.
COMFY_SEEDREAM_MODEL = "seedream-5-0-260128"   # rotulado "Seedream 5.0 lite" no core
COMFY_SEEDREAM_MIN_PX = 3_686_400              # abaixo disso a API recusa ANTES de cobrar

# Tamanhos que satisfazem o piso, por proporção.
COMFY_SEEDREAM_SIZES = {
    "auto": (2048, 2048),
    "1:1": (2048, 2048),
    "16:9": (2560, 1440),
    "9:16": (1440, 2560),
    "4:3": (2304, 1728),
    "3:4": (1728, 2304),
    "21:9": (3024, 1296),
    "3:2": (2400, 1600),
    "2:3": (1600, 2400),
    "5:4": (2160, 1728),
    "4:5": (1728, 2160),
}


def _comfy_base() -> str:
    """Respeita --comfy-api-base, igual aos nós partner do core."""
    try:
        from comfy.cli_args import args
        return str(getattr(args, "comfy_api_base", COMFY_API_BASE)).rstrip("/")
    except Exception:
        return COMFY_API_BASE


def _comfy_headers(auth_token: str | None, api_key: str | None) -> dict:
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    if api_key:
        return {"X-API-KEY": api_key}
    raise RuntimeError(
        "Rota 'Créditos comfy.org' escolhida, mas o ComfyUI não passou credencial.\n"
        "Faça login em platform.comfy.org pela própria interface do ComfyUI "
        "(menu do usuário) e rode de novo. Sem login não há crédito a consumir."
    )


def _comfy_upload_image(image: torch.Tensor, headers: dict) -> str:
    """Sobe a imagem para o storage do comfy.org e devolve a URL de download."""
    import requests

    pil = _tensor_to_pil(image)
    buffer = io.BytesIO()
    pil.save(buffer, format="PNG")
    buffer.seek(0)

    base = _comfy_base()
    create = requests.post(
        f"{base}{COMFY_UPLOAD_ENDPOINT}",
        headers={**headers, "Content-Type": "application/json"},
        json={"file_name": f"pro_edit_{time.time_ns()}.png", "content_type": "image/png"},
        timeout=120,
    )
    if create.status_code != 200:
        raise RuntimeError(
            f"upload comfy.org falhou (HTTP {create.status_code}): {create.text[:300]}"
        )
    payload = create.json()
    upload_url, download_url = payload.get("upload_url"), payload.get("download_url")
    if not upload_url or not download_url:
        raise RuntimeError(f"resposta de upload inesperada: {str(payload)[:300]}")

    put = requests.put(upload_url, data=buffer.getvalue(),
                       headers={"Content-Type": "image/png"}, timeout=600)
    if put.status_code not in (200, 201, 204):
        raise RuntimeError(f"PUT do upload falhou (HTTP {put.status_code})")
    return download_url


def _comfy_seedream_size(aspect_ratio: str) -> tuple[int, int]:
    width, height = COMFY_SEEDREAM_SIZES.get(aspect_ratio, COMFY_SEEDREAM_SIZES["auto"])
    if width * height < COMFY_SEEDREAM_MIN_PX:  # rede de segurança
        return COMFY_SEEDREAM_SIZES["auto"]
    return width, height


def _run_comfy_seedream(prompt: str, image_urls: list[str], aspect_ratio: str,
                        num_images: int, seed: int, headers: dict) -> list[str]:
    """Chama o Seedream partner pelos créditos do comfy.org."""
    import requests

    width, height = _comfy_seedream_size(aspect_ratio)
    body = {
        "model": COMFY_SEEDREAM_MODEL,
        "prompt": prompt,
        "image": image_urls,
        "size": f"{width}x{height}",
        "seed": int(seed) if seed else 0,
        "sequential_image_generation": "disabled",
        "sequential_image_generation_options": {"max_images": max(1, int(num_images))},
        "watermark": False,
        "response_format": "url",
        "output_format": "png",
    }
    base = _comfy_base()
    print(f"[Pro Edit] POST {base}{COMFY_SEEDREAM_ENDPOINT}  "
          f"model={COMFY_SEEDREAM_MODEL} size={width}x{height}  (créditos comfy.org)")

    response = requests.post(
        f"{base}{COMFY_SEEDREAM_ENDPOINT}",
        headers={**headers, "Content-Type": "application/json"},
        json=body,
        timeout=900,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"comfy.org HTTP {response.status_code}: {response.text[:400]}\n"
            "401/403 = login expirado · 402 = sem crédito · 400 = payload recusado."
        )
    payload = response.json()
    error = payload.get("error") or {}
    if error:
        raise RuntimeError(f"comfy.org recusou: {error}")
    urls = [d["url"] for d in payload.get("data", [])
            if isinstance(d, dict) and d.get("url")]
    if not urls:
        raise RuntimeError(f"resposta sem imagens: {str(payload)[:400]}")
    return urls


# --------------------------------------------------------------------------- #
# Chave e cliente                                                              #
# --------------------------------------------------------------------------- #

def _read_secrets_env(path: str, name: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].strip()
                key, _, value = line.partition("=")
                if key.strip() == name:
                    return value.strip().strip("'\"") or None
    except OSError:
        pass
    return None


def _get_key() -> str:
    key = os.environ.get("FAL_KEY")
    if key:
        return key
    for candidate in (
        os.path.join(os.path.expanduser("~"), "ComfyUI", "secrets.env"),
        os.path.join(folder_paths.base_path, "secrets.env"),
    ):
        key = _read_secrets_env(candidate, "FAL_KEY")
        if key:
            os.environ["FAL_KEY"] = key
            return key
    raise RuntimeError(
        "FAL_KEY nao encontrada. Grave a chave e reinicie o ComfyUI:\n"
        "  printf 'FAL_KEY=%s\\n' \"SUA_CHAVE\" >> ~/ComfyUI/secrets.env\n"
        "  chmod 600 ~/ComfyUI/secrets.env\n"
        "Pegue em https://fal.ai/dashboard/keys (o valor aparece UMA vez so)."
    )


def _client():
    try:
        from fal_client.client import SyncClient
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "fal_client nao instalado. Ele vem junto do ComfyUI-fal-API; senao:\n"
            "  ~/ComfyUI/venv/bin/python -m pip install fal-client"
        ) from exc
    return SyncClient(key=_get_key())


def _temp_path(suffix: str) -> str:
    directory = folder_paths.get_temp_directory()
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"pro_edit_{os.getpid()}_{time.time_ns()}{suffix}")


def _cleanup(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Conversao e upload                                                           #
# --------------------------------------------------------------------------- #

def _tensor_to_pil(image: torch.Tensor) -> Image.Image:
    frame = image[0] if image.dim() == 4 else image
    array = np.clip(frame.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    pil = Image.fromarray(array)
    return pil if pil.mode in ("RGB", "RGBA") else pil.convert("RGB")


def _upload_image(client, image: torch.Tensor) -> str:
    """Sobe como PNG. PNG e sem perda — JPEG na ENTRADA ja custa detalhe de rosto."""
    pil = _tensor_to_pil(image)
    path = _temp_path(".png")
    pil.save(path, format="PNG")
    try:
        return client.upload_file(path)
    finally:
        _cleanup(path)


def _upload_mask(client, mask: torch.Tensor) -> str:
    """MASK (B,H,W) -> PNG em escala de cinza."""
    m = mask[0] if mask.dim() == 3 else mask
    array = np.clip(m.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    pil = Image.fromarray(array, mode="L")
    path = _temp_path(".png")
    pil.save(path, format="PNG")
    try:
        return client.upload_file(path)
    finally:
        _cleanup(path)


def _pil_to_tensor(pil: Image.Image) -> torch.Tensor:
    pil = ImageOps.exif_transpose(pil)
    if pil.mode != "RGB":
        pil = pil.convert("RGB")
    array = np.array(pil).astype(np.float32) / 255.0
    return torch.from_numpy(array)[None, ...]


def _download_images(urls: list[str]) -> torch.Tensor:
    """Baixa as imagens e empilha num batch IMAGE.

    Se vierem tamanhos diferentes, empilhar quebraria — nesse caso devolve so a
    primeira e avisa, em vez de estourar com um erro de shape ilegivel.
    """
    import requests

    tensors = []
    for url in urls:
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        tensors.append(_pil_to_tensor(Image.open(io.BytesIO(response.content))))

    if not tensors:
        raise RuntimeError("a API nao devolveu nenhuma imagem.")
    shapes = {tuple(t.shape[1:3]) for t in tensors}
    if len(shapes) > 1:
        print(
            f"[Pro Edit] AVISO: o modelo devolveu tamanhos diferentes {shapes}; "
            "devolvendo apenas a primeira imagem. Para comparar todas, baixe pelas URLs."
        )
        return tensors[0]
    return torch.cat(tensors, dim=0)


# --------------------------------------------------------------------------- #
# Fila da fal                                                                  #
# --------------------------------------------------------------------------- #

def _run(app: str, arguments: dict) -> dict:
    from fal_client import Completed, InProgress, Queued

    client = _client()
    print(f"[Pro Edit] POST {app}")
    handle = client.submit(app, arguments=arguments)
    print(f"[Pro Edit] request_id={handle.request_id}")

    started = time.time()
    last = ""
    while True:
        if model_management is not None:
            model_management.throw_exception_if_processing_interrupted()
        status = handle.status(with_logs=False)
        if isinstance(status, Completed):
            break
        note = (f"na fila (posição {status.position})" if isinstance(status, Queued)
                else "gerando" if isinstance(status, InProgress) else type(status).__name__)
        if note != last:
            print(f"[Pro Edit] {note}… {int(time.time() - started)}s")
            last = note
        time.sleep(POLL_SECONDS)

    print(f"[Pro Edit] pronto em {int(time.time() - started)}s")
    return handle.get()


# --------------------------------------------------------------------------- #
# Normalizacao de parametros entre modelos                                     #
# --------------------------------------------------------------------------- #

def _apply_size(arguments: dict, spec: dict, resolucao: str, aspect_ratio: str) -> None:
    """Traduz a resolucao pedida para o parametro que ESTE modelo entende."""
    pedido = resolucao.split(" ")[0]  # "auto (recomendado)" -> "auto"

    if spec["size_mode"] == "resolution":  # Nano Banana Pro
        arguments["resolution"] = "2K" if pedido == "auto" else pedido
        arguments["aspect_ratio"] = aspect_ratio
        return

    # image_size (Seedream, FLUX.2, GPT Image 2)
    if spec["max_res"] == "2K":  # Seedream: teto real de 2048x2048
        if pedido == "4K":
            print("[Pro Edit] AVISO: Seedream não passa de 2K (teto de 2048×2048). Usando 2K.")
        arguments["image_size"] = "auto_1K" if pedido == "1K" else "auto_2K"
    else:
        # FLUX.2 Pro e GPT Image 2 só têm 'auto' + presets de proporção.
        arguments["image_size"] = "auto"
        if pedido not in ("auto", ""):
            print(
                f"[Pro Edit] nota: este modelo não tem controle discreto de resolução; "
                f"'{pedido}' foi ignorado e o tamanho sai do próprio input."
            )


def _collect(*values):
    return [v for v in values if v is not None]


# --------------------------------------------------------------------------- #
# Nos                                                                          #
# --------------------------------------------------------------------------- #

class ProImageEditBYOK:
    """Edição de foto multi-referência nos 4 melhores motores, por chave direta."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (MODEL_NAMES, {"default": MODEL_NAMES[0]}),
                "rota": (
                    ROTAS,
                    {
                        "default": ROTA_FAL,
                        "tooltip": "Quem paga. 'Créditos comfy.org' usa o saldo que você já "
                                   "comprou (exige login na interface) e IGNORA o dropdown de "
                                   "modelo — só o Seedream tem nó partner. 'Minha chave' usa a "
                                   "FAL_KEY e dá acesso aos 5 motores.",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Replace the person in Image 1 with the person shown in Image 2 and Image 3. Only the identity changes.",
                        "tooltip": "Cite as imagens como 'Image 1', 'Image 2'… na ORDEM dos slots.",
                    },
                ),
                "resolucao": (
                    RESOLUTIONS,
                    {
                        "default": "2K",
                        "tooltip": "Resolução da SAÍDA. Rosto precisa de pixel: 1K só para rascunho.",
                    },
                ),
                "num_images": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 4,
                        "tooltip": "Gera N variações na MESMA chamada. Subir para 3-4 é a forma "
                                   "mais barata de vencer a loteria da identidade — escolha o melhor rosto.",
                    },
                ),
                "output_format": (
                    ["png", "jpeg"],
                    {"default": "png", "tooltip": "PNG é sem perda. JPEG já custa detalhe de pele."},
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 2147483647,
                        "control_after_generate": True,
                        "tooltip": "Só FLUX.2 Pro e Nano Banana Pro aceitam seed; nos outros serve "
                                   "apenas para forçar re-execução.",
                    },
                ),
            },
            "optional": {
                "image_1": ("IMAGE", {"tooltip": "A foto BASE — a que vai ser editada."}),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "image_6": ("IMAGE",),
                "mask": ("MASK", {"tooltip": "Só o GPT Image 2 usa. Marca a região a editar."}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "auto"}),
                "system_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Só o Nano Banana Pro aceita. Vazio = não enviado.",
                    },
                ),
                "safety_tolerance": (
                    ["1", "2", "3", "4", "5"],
                    {"default": "4", "tooltip": "Maior = menos bloqueio. Ignorado por quem não aceita."},
                ),
            },
            # Injetado pelo ComfyUI quando você está logado no platform.comfy.org.
            # É o que permite gastar o crédito já pago em vez da FAL_KEY.
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "comfy_api_key": "API_KEY_COMFY_ORG",
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "image_url", "descricao")
    FUNCTION = "edit"
    CATEGORY = "Pro Image Edit BYOK"
    DESCRIPTION = (
        "Edição de foto multi-referência nos melhores motores por API (Seedream 5 Pro, "
        "FLUX.2 Pro, Nano Banana Pro, GPT Image 2) com a SUA FAL_KEY. Troque o modelo no "
        "dropdown e compare no seu próprio rosto."
    )

    def edit(self, model, rota, prompt, resolucao, num_images, output_format, seed,
             image_1=None, image_2=None, image_3=None, image_4=None, image_5=None,
             image_6=None, mask=None, aspect_ratio="auto", system_prompt="",
             safety_tolerance="4", auth_token=None, comfy_api_key=None):
        if not prompt or not prompt.strip():
            raise ValueError("O prompt é obrigatório em todos os modelos.")

        images = _collect(image_1, image_2, image_3, image_4, image_5, image_6)
        if not images:
            raise ValueError(
                "Nenhuma imagem ligada. Estes endpoints são de EDIÇÃO: exigem ao menos a "
                "foto base no image_1."
            )

        # ------------------------------------------------------------------ #
        # Rota dos créditos comfy.org                                        #
        # ------------------------------------------------------------------ #
        if rota == ROTA_COMFY:
            if model != MODEL_NAMES[0] and "Seedream" not in model:
                print(
                    f"[Pro Edit] NOTA: a rota de créditos comfy.org só tem nó partner para o "
                    f"Seedream. O modelo '{model}' foi ignorado e a chamada vai para "
                    f"'{COMFY_SEEDREAM_MODEL}'. Para usar {model}, escolha a rota "
                    f"'{ROTA_FAL}'."
                )
            if len(images) > 10:
                raise ValueError(
                    f"O Seedream partner aceita até 10 imagens; recebi {len(images)}."
                )
            if mask is not None:
                print("[Pro Edit] AVISO: a rota comfy.org (Seedream) não aceita máscara — ignorada.")

            headers = _comfy_headers(auth_token, comfy_api_key)
            image_urls = [_comfy_upload_image(img, headers) for img in images]
            urls = _run_comfy_seedream(
                prompt, image_urls, aspect_ratio, num_images, seed, headers
            )
            return (_download_images(urls), urls[0], "")

        spec = MODELS[model]
        if len(images) > spec["max_refs"]:
            raise ValueError(
                f"'{model}' aceita no máximo {spec['max_refs']} imagens; recebi {len(images)}."
            )

        client = _client()
        arguments = {
            "prompt": prompt,
            "image_urls": [_upload_image(client, img) for img in images],
            "num_images": int(num_images),
            "output_format": output_format,
        }
        _apply_size(arguments, spec, resolucao, aspect_ratio)

        if spec.get("seed") and seed:
            arguments["seed"] = int(seed)
        if spec.get("system") and system_prompt.strip():
            arguments["system_prompt"] = system_prompt.strip()
        if spec.get("safety") is not None:
            arguments["safety_tolerance"] = safety_tolerance
        if spec.get("quality"):
            arguments["quality"] = "high"

        if mask is not None:
            if spec.get("mask"):
                arguments["mask_url"] = _upload_mask(client, mask)
            else:
                print(
                    f"[Pro Edit] AVISO: '{model}' não aceita máscara — ela foi IGNORADA. "
                    "Para editar por máscara, escolha 'GPT Image 2'."
                )

        result = _run(f"{spec['endpoint']}", arguments)

        urls = [item["url"] for item in result.get("images", []) if item.get("url")]
        if not urls:
            raise RuntimeError(f"resposta sem imagens: {str(result)[:400]}")

        descricao = result.get("description") or ""
        return (_download_images(urls), urls[0], descricao)


class ProFaceRestoreBYOK:
    """Passe de restauracao de rosto — a etapa que faltava.

    A literatura de face swap de 2026 é consistente num ponto: um passe de restauracao
    (CodeFormer/GFPGAN) DEPOIS da geracao responde por boa parte do ganho de qualidade.
    Ele limpa artefato de geracao e devolve microtextura de pele — exatamente o que faz
    um rosto parecer fotografado em vez de renderizado.

    O botao que importa e `fidelity`:
      alto  (0.7-0.9) -> fica FIEL ao rosto que entrou. E o que voce quer aqui.
      baixo (0.0-0.3) -> "melhora" mais, e nesse caminho ele TROCA tracos.
    """

    ENDPOINT = "fal-ai/codeformer"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "fidelity": (
                    "FLOAT",
                    {
                        "default": 0.8,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.05,
                        "tooltip": "Fidelidade ao rosto de ENTRADA. Alto = preserva identidade. "
                                   "Baixo = 'embeleza' e troca traços. Para o seu rosto: 0.7–0.9.",
                    },
                ),
                "upscale_factor": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 1.0,
                        "max": 4.0,
                        "step": 0.5,
                        "tooltip": "1.0 = não amplia (só restaura). Suba se quiser mais pixel de rosto.",
                    },
                ),
                "face_upscale": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Amplia a região do rosto especificamente."},
                ),
                "only_center_face": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "True = mexe só no rosto central. Use quando há outras pessoas "
                                   "no quadro e você não quer alterá-las.",
                    },
                ),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True},
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_url")
    FUNCTION = "restore"
    CATEGORY = "Pro Image Edit BYOK"
    DESCRIPTION = (
        "Passe de restauração de rosto (CodeFormer) pela fal com a SUA FAL_KEY. Rode DEPOIS "
        "da edição: limpa artefato e devolve textura de pele. `fidelity` alto preserva identidade."
    )

    def restore(self, image, fidelity, upscale_factor, face_upscale, only_center_face, seed):
        if fidelity < 0.5:
            print(
                f"[Face Restore] AVISO: fidelity={fidelity:.2f} é baixo. Abaixo de 0.5 o "
                "CodeFormer prioriza 'qualidade' sobre fidelidade e costuma TROCAR traços do "
                "rosto. Para preservar identidade use 0.7–0.9."
            )
        client = _client()
        arguments = {
            "image_url": _upload_image(client, image),
            "fidelity": float(fidelity),
            "upscale_factor": float(upscale_factor),
            "face_upscale": bool(face_upscale),
            "only_center_face": bool(only_center_face),
        }
        if seed:
            arguments["seed"] = int(seed)

        result = _run(self.ENDPOINT, arguments)
        image_info = result.get("image") or {}
        url = image_info.get("url") if isinstance(image_info, dict) else None
        if not url:
            raise RuntimeError(f"resposta sem imagem: {str(result)[:400]}")
        return (_download_images([url]), url)


class ProImageEditCheckKey:
    """Diagnóstico de custo zero: a chave existe e os 4 motores respondem?"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "check"
    CATEGORY = "Pro Image Edit BYOK"
    OUTPUT_NODE = True
    DESCRIPTION = "Confere a FAL_KEY e quais motores de edição estão roteáveis agora."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def check(self):
        import requests

        lines = []
        try:
            key = _get_key()
            lines.append(f"FAL_KEY: carregada (…{key[-4:]})")
        except RuntimeError as exc:
            return (f"FAL_KEY: AUSENTE\n\n{exc}",)

        for name, spec in MODELS.items():
            url = ("https://fal.ai/api/openapi/queue/openapi.json"
                   f"?endpoint_id={spec['endpoint']}")
            try:
                code = requests.get(url, timeout=20).status_code
            except Exception as exc:  # pragma: no cover
                lines.append(f"{name}: erro de rede ({exc})")
                continue
            lines.append(f"{name}: {'roteável' if code == 200 else f'INDISPONÍVEL (HTTP {code})'}")

        lines.append(
            "\nObs.: 'roteável' confirma que o endpoint existe. Não confirma saldo — "
            "sem crédito na fal a geração falha com 401/402."
        )
        return ("\n".join(lines),)


NODE_CLASS_MAPPINGS = {
    "ProImageEditBYOK": ProImageEditBYOK,
    "ProFaceRestoreBYOK": ProFaceRestoreBYOK,
    "ProImageEditCheckKey": ProImageEditCheckKey,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ProImageEditBYOK": "Pro Image Edit BYOK · Editar foto",
    "ProFaceRestoreBYOK": "Pro Image Edit BYOK · Restaurar rosto (passe final)",
    "ProImageEditCheckKey": "Pro Image Edit BYOK · Testar Chave",
}
