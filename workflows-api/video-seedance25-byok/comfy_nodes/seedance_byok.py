"""Seedance BYOK — nos de API que falam DIRETO com a fal.ai usando a sua FAL_KEY.

Por que este arquivo existe: em 2026-08-04 nenhum no instalavel cobre Seedance 2.x
por chave direta. O `ComfyUI-fal-API` para no Seedance 1.x e os nos partner do core
(`ByteDance2ReferenceNode`) cobram creditos do comfy.org e exigem login. Estes nos
fecham a lacuna reaproveitando o `fal_client`, que ja vem instalado como dependencia
do ComfyUI-fal-API.

Contratos extraidos do OpenAPI ao vivo da fal (2026-08-04):
  https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.0/reference-to-video

Regra de nomenclatura que derruba quem adivinha: os endpoints 2.x NAO levam o prefixo
`fal-ai/` (v1/v1.5 levam). O caminho correto e `bytedance/seedance-2.0/...`.
"""

from __future__ import annotations

import io
import os
import time
import wave

import numpy as np
import torch
from PIL import Image

import folder_paths

try:  # disponivel dentro do ComfyUI; ausente em lint isolado
    import comfy.model_management as model_management
except Exception:  # pragma: no cover
    model_management = None

from comfy_api.latest import InputImpl


# --------------------------------------------------------------------------- #
# Endpoints                                                                    #
# --------------------------------------------------------------------------- #

# display -> (segmento do endpoint, resolucoes validas, aceita bitrate_mode)
MODELS = {
    "Seedance 2.5 (assim que a fal publicar)": ("bytedance/seedance-2.5", ["480p", "720p", "1080p", "4k"], False),
    "Seedance 2.0": ("bytedance/seedance-2.0", ["480p", "720p", "1080p", "4k"], True),
    "Seedance 2.0 Fast": ("bytedance/seedance-2.0/fast", ["480p", "720p"], True),
    "Seedance 2.0 Mini (rascunho barato)": ("bytedance/seedance-2.0/mini", ["480p", "720p"], False),
}
MODEL_NAMES = list(MODELS.keys())

RESOLUTIONS = ["480p", "720p", "1080p", "4k"]
ASPECT_RATIOS = ["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
DURATIONS = ["auto"] + [str(n) for n in range(4, 16)]

POLL_SECONDS = 3.0

# --------------------------------------------------------------------------- #
# Rotas de pagamento                                                           #
# --------------------------------------------------------------------------- #
#
# ROTA_FAL   — a sua FAL_KEY (Seedance 2.0/2.5, todos os tiers).
# ROTA_COMFY — os creditos que voce ja pagou no comfy.org (Seedance 2.0 partner).
#
# Mecanismo lido do ComfyUI instalado, nao inferido:
#   - `execution.py` injeta o token quando o no declara
#     "hidden": {"auth_token": "AUTH_TOKEN_COMFY_ORG"}
#   - header: Authorization: Bearer <token>  (ou X-API-KEY)
#   - base:   https://api.comfy.org
#   - upload: POST /customers/storage -> {upload_url, download_url}; depois PUT
#   - criar:  POST /proxy/byteplus/api/v3/contents/generations/tasks
#   - status: GET  /proxy/byteplus-seedance2/api/v3/contents/generations/tasks/{id}
#     (repare a assimetria: criar e no `byteplus`, status no `byteplus-seedance2`)

ROTA_FAL = "Minha chave (fal.ai)"
ROTA_COMFY = "Créditos comfy.org (login) — Seedance 2.0"
ROTAS = [ROTA_FAL, ROTA_COMFY]

COMFY_API_BASE = "https://api.comfy.org"
COMFY_UPLOAD_ENDPOINT = "/customers/storage"
COMFY_TASK_CREATE = "/proxy/byteplus/api/v3/contents/generations/tasks"
COMFY_TASK_STATUS = "/proxy/byteplus-seedance2/api/v3/contents/generations/tasks"

# Nome no widget -> id do modelo partner. O 2.5 ainda nao existe nesta rota.
COMFY_SEEDANCE_MODELS = {
    "Seedance 2.0": "dreamina-seedance-2-0-260128",
    "Seedance 2.0 Fast": "dreamina-seedance-2-0-fast-260128",
}


def _comfy_base() -> str:
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
        "Faça login em platform.comfy.org pela interface do ComfyUI e rode de novo."
    )


def _comfy_upload_bytes(data: bytes, filename: str, mime: str, headers: dict) -> str:
    import requests

    base = _comfy_base()
    create = requests.post(
        f"{base}{COMFY_UPLOAD_ENDPOINT}",
        headers={**headers, "Content-Type": "application/json"},
        json={"file_name": filename, "content_type": mime},
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
    put = requests.put(upload_url, data=data, headers={"Content-Type": mime}, timeout=900)
    if put.status_code not in (200, 201, 204):
        raise RuntimeError(f"PUT do upload falhou (HTTP {put.status_code})")
    return download_url


def _comfy_upload_image(image: torch.Tensor, headers: dict) -> str:
    frame = image[0] if image.dim() == 4 else image
    array = np.clip(frame.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    pil = Image.fromarray(array)
    if pil.mode not in ("RGB", "RGBA"):
        pil = pil.convert("RGB")
    buffer = io.BytesIO()
    pil.save(buffer, format="PNG")
    return _comfy_upload_bytes(
        buffer.getvalue(), f"seedance_{time.time_ns()}.png", "image/png", headers
    )


def _comfy_upload_video(video, headers: dict) -> str:
    path = _temp_path(".mp4")
    try:
        video.save_to(path)
        with open(path, "rb") as fh:
            data = fh.read()
    finally:
        _cleanup(path)
    return _comfy_upload_bytes(
        data, f"seedance_{time.time_ns()}.mp4", "video/mp4", headers
    )


def _translate_labels_to_partner(prompt: str) -> str:
    """`@Image1` (sintaxe fal) -> `Image 1` (sintaxe partner).

    Sem isto a troca de rota falha em silêncio: o modelo recebe um token que não
    reconhece e simplesmente ignora a referência.
    """
    import re

    translated = re.sub(r"@(Image|Video|Audio)\s*(\d{1,2})", r"\1 \2", prompt)
    if translated != prompt:
        print("[Seedance BYOK] prompt traduzido para a sintaxe partner (@Image1 -> Image 1).")
    return translated


def _run_comfy_seedance(body: dict, headers: dict) -> str:
    """Cria a tarefa nos créditos comfy.org, faz polling e devolve a URL do vídeo."""
    import requests

    base = _comfy_base()
    print(f"[Seedance BYOK] POST {base}{COMFY_TASK_CREATE}  model={body.get('model')}  "
          "(créditos comfy.org)")
    response = requests.post(
        f"{base}{COMFY_TASK_CREATE}",
        headers={**headers, "Content-Type": "application/json"},
        json=body,
        timeout=300,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"comfy.org HTTP {response.status_code}: {response.text[:400]}\n"
            "401/403 = login expirado · 402 = sem crédito · 400 = payload recusado."
        )
    task_id = response.json().get("id")
    if not task_id:
        raise RuntimeError(f"resposta sem id de tarefa: {response.text[:300]}")
    print(f"[Seedance BYOK] task_id={task_id}")

    started = time.time()
    last = ""
    while True:
        if model_management is not None:
            model_management.throw_exception_if_processing_interrupted()
        poll = requests.get(
            f"{base}{COMFY_TASK_STATUS}/{task_id}", headers=headers, timeout=120
        )
        if poll.status_code != 200:
            raise RuntimeError(f"polling HTTP {poll.status_code}: {poll.text[:300]}")
        task = poll.json()
        status = task.get("status", "")
        if status != last:
            print(f"[Seedance BYOK] {status}… {int(time.time() - started)}s")
            last = status
        if status == "succeeded":
            url = (task.get("content") or {}).get("video_url")
            if not url:
                raise RuntimeError(f"tarefa concluída sem URL: {str(task)[:300]}")
            print(f"[Seedance BYOK] pronto em {int(time.time() - started)}s")
            return url
        if status in ("failed", "cancelled"):
            err = task.get("error") or {}
            raise RuntimeError(f"tarefa {status}: {err.get('message') or str(task)[:300]}")
        time.sleep(POLL_SECONDS)

# Limites do modelo (o servidor tambem valida; validamos antes para nao gastar credito).
MAX_IMAGES, MAX_VIDEOS, MAX_AUDIOS, MAX_FILES_TOTAL = 9, 3, 3, 12


# --------------------------------------------------------------------------- #
# Chave e cliente                                                              #
# --------------------------------------------------------------------------- #

def _read_secrets_env(path: str) -> str | None:
    """Le FAL_KEY de um arquivo estilo dotenv sem depender de biblioteca externa."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].strip()
                key, _, value = line.partition("=")
                if key.strip() == "FAL_KEY":
                    return value.strip().strip("'\"") or None
    except OSError:
        pass
    return None


def _get_key() -> str:
    key = os.environ.get("FAL_KEY")
    if key:
        return key
    # Fallback: o run.sh do projeto da source no secrets.env, mas se o servidor
    # subiu por outro caminho a env var pode nao estar la.
    for candidate in (
        os.path.join(os.path.expanduser("~"), "ComfyUI", "secrets.env"),
        os.path.join(os.path.dirname(folder_paths.base_path), "secrets.env"),
        os.path.join(folder_paths.base_path, "secrets.env"),
    ):
        key = _read_secrets_env(candidate)
        if key:
            os.environ["FAL_KEY"] = key
            return key
    raise RuntimeError(
        "FAL_KEY nao encontrada. Grave a chave e reinicie o ComfyUI:\n"
        "  printf 'FAL_KEY=%s\\n' \"SUA_CHAVE\" >> ~/ComfyUI/secrets.env\n"
        "  chmod 600 ~/ComfyUI/secrets.env\n"
        "Pegue a chave em https://fal.ai/dashboard/keys (o valor so aparece uma vez)."
    )


def _client():
    try:
        from fal_client.client import SyncClient
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "fal_client nao instalado. Ele vem junto do ComfyUI-fal-API; se voce nao usa "
            "esse pacote, instale no venv do ComfyUI:  pip install fal-client"
        ) from exc
    return SyncClient(key=_get_key())


def _temp_path(suffix: str) -> str:
    directory = folder_paths.get_temp_directory()
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"seedance_byok_{os.getpid()}_{time.time_ns()}{suffix}")


# --------------------------------------------------------------------------- #
# Upload das referencias                                                       #
# --------------------------------------------------------------------------- #

def _upload_image(client, image: torch.Tensor) -> str:
    """IMAGE (B,H,W,C float 0..1) -> PNG temporario -> URL da fal."""
    frame = image[0] if image.dim() == 4 else image
    array = np.clip(frame.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    pil = Image.fromarray(array)
    if pil.mode not in ("RGB", "RGBA"):
        pil = pil.convert("RGB")
    width, height = pil.size
    # Limite documentado do modelo: lado entre 300 e 6000 px, proporcao 0.4..2.5.
    if min(width, height) < 300:
        raise ValueError(
            f"Imagem de referencia pequena demais ({width}x{height}). O modelo exige "
            "lado minimo de 300 px. Use uma foto maior."
        )
    path = _temp_path(".png")
    pil.save(path, format="PNG")
    try:
        return client.upload_file(path)
    finally:
        _cleanup(path)


def _upload_video(client, video) -> str:
    """VIDEO nativo -> mp4 temporario -> URL da fal."""
    source = None
    try:
        source = video.get_stream_source()
    except Exception:
        source = None
    if isinstance(source, str) and os.path.isfile(source):
        return client.upload_file(source)

    path = _temp_path(".mp4")
    try:
        video.save_to(path)
        return client.upload_file(path)
    finally:
        _cleanup(path)


def _upload_audio(client, audio) -> str:
    """AUDIO ({waveform, sample_rate}) -> WAV 16-bit temporario -> URL da fal."""
    waveform = audio["waveform"]
    sample_rate = int(audio["sample_rate"])
    if waveform.dim() == 3:
        waveform = waveform[0]
    samples = waveform.cpu().numpy()
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16).T  # (frames, canais)

    path = _temp_path(".wav")
    try:
        with wave.open(path, "wb") as handle:
            handle.setnchannels(pcm.shape[1])
            handle.setsampwidth(2)
            handle.setframerate(sample_rate)
            handle.writeframes(pcm.tobytes())
        return client.upload_file(path)
    finally:
        _cleanup(path)


def _cleanup(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Fila da fal                                                                  #
# --------------------------------------------------------------------------- #

def _run(app: str, arguments: dict) -> dict:
    """Submete na fila e faz polling. Interrompivel pelo botao Cancel do ComfyUI."""
    from fal_client import Completed, InProgress, Queued

    client = _client()
    print(f"[Seedance BYOK] POST {app}")
    handle = client.submit(app, arguments=arguments)
    print(f"[Seedance BYOK] request_id={handle.request_id}")

    started = time.time()
    last_note = ""
    while True:
        if model_management is not None:
            # Sem isto o no ignora o Cancel e so morre reiniciando o servidor —
            # exatamente a queixa conhecida dos nos *_fal.
            model_management.throw_exception_if_processing_interrupted()

        status = handle.status(with_logs=False)
        if isinstance(status, Completed):
            break

        if isinstance(status, Queued):
            note = f"na fila (posicao {status.position})"
        elif isinstance(status, InProgress):
            note = "gerando"
        else:
            note = type(status).__name__
        if note != last_note:
            print(f"[Seedance BYOK] {note}… {int(time.time() - started)}s")
            last_note = note
        time.sleep(POLL_SECONDS)

    result = handle.get()
    print(f"[Seedance BYOK] pronto em {int(time.time() - started)}s")
    return result


def _download_video(url: str):
    """Baixa o MP4 inteiro e devolve VIDEO nativo — o audio vem junto no container.

    Nao use LoadVideoURL aqui: ele extrai frames (IMAGE) e o audio se perde.
    """
    import requests

    response = requests.get(url, timeout=600)
    response.raise_for_status()
    return InputImpl.VideoFromFile(io.BytesIO(response.content))


# --------------------------------------------------------------------------- #
# Validacao                                                                    #
# --------------------------------------------------------------------------- #

def _validate(prompt, images, videos, audios, model_name, resolution):
    if not prompt or not prompt.strip():
        raise ValueError("O prompt e obrigatorio no Seedance reference-to-video.")

    n_img, n_vid, n_aud = len(images), len(videos), len(audios)
    if n_img > MAX_IMAGES:
        raise ValueError(f"Maximo {MAX_IMAGES} imagens de referencia; recebi {n_img}.")
    if n_vid > MAX_VIDEOS:
        raise ValueError(f"Maximo {MAX_VIDEOS} videos de referencia; recebi {n_vid}.")
    if n_aud > MAX_AUDIOS:
        raise ValueError(f"Maximo {MAX_AUDIOS} audios de referencia; recebi {n_aud}.")
    if n_img + n_vid + n_aud > MAX_FILES_TOTAL:
        raise ValueError(
            f"Maximo {MAX_FILES_TOTAL} arquivos somando todas as modalidades; recebi "
            f"{n_img + n_vid + n_aud}."
        )
    if n_aud and not (n_img or n_vid):
        raise ValueError("Audio de referencia exige pelo menos uma imagem ou um video.")

    _, allowed, _ = MODELS[model_name]
    if resolution not in allowed:
        raise ValueError(
            f"'{model_name}' nao aceita {resolution}. Resolucoes validas: {', '.join(allowed)}."
        )

    # Aviso barato que evita a queixa mais comum: referencia ignorada porque o
    # prompt nunca a citou.
    missing = [
        label
        for label, count in (("@Image", n_img), ("@Video", n_vid), ("@Audio", n_aud))
        if count and label not in prompt
    ]
    if missing:
        print(
            "[Seedance BYOK] AVISO: voce ligou referencias mas o prompt nao cita "
            f"{', '.join(m + '1' for m in missing)}. O modelo tende a ignora-las."
        )


def _collect(*values):
    return [v for v in values if v is not None]


# --------------------------------------------------------------------------- #
# Nos                                                                          #
# --------------------------------------------------------------------------- #

class SeedanceBYOKReferenceToVideo:
    """Reference-to-video: monta uma cena NOVA a partir de fotos/videos/audios de referencia."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (MODEL_NAMES, {"default": "Seedance 2.0"}),
                "rota": (
                    ROTAS,
                    {
                        "default": ROTA_FAL,
                        "tooltip": "Quem paga. 'Créditos comfy.org' usa o saldo já comprado "
                                   "(exige login na interface) e só serve para Seedance 2.0 / "
                                   "2.0 Fast. ⚠️ Nessa rota, foto/vídeo de PESSOA REAL é "
                                   "recusado — exige o fluxo de asset verificado do bundle "
                                   "../video-person-swap-seedance-2/.",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "@Image1 walks into the scene of @Image2, cinematic lighting.",
                        "tooltip": "Cite cada referencia por @Image1/@Video1/@Audio1 na ORDEM em que "
                                   "elas estao ligadas. Sem isso o modelo tende a ignora-las.",
                    },
                ),
                "resolution": (RESOLUTIONS, {"default": "720p"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "auto"}),
                "duration": (DURATIONS, {"default": "auto", "tooltip": "Segundos (4-15) ou auto."}),
                "generate_audio": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Gera audio NOVO. Custa o mesmo ligado ou desligado."},
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 2147483647,
                        "control_after_generate": True,
                        "tooltip": "NAO vai para a API (o Seedance 2.x na fal nao aceita seed). "
                                   "Serve so para forcar re-execucao do no.",
                    },
                ),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "video_1": ("VIDEO",),
                "video_2": ("VIDEO",),
                "audio_1": ("AUDIO",),
                "bitrate_mode": (["standard", "high"], {"default": "standard"}),
                "end_user_id": (
                    "STRING",
                    {"default": "", "tooltip": "Opcional: identificador do usuario final (atribuicao de abuso)."},
                ),
            },
            # Injetado pelo ComfyUI quando voce esta logado no platform.comfy.org.
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "comfy_api_key": "API_KEY_COMFY_ORG",
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "video_url")
    FUNCTION = "generate"
    CATEGORY = "Seedance BYOK"
    DESCRIPTION = (
        "Seedance reference-to-video com a SUA FAL_KEY ou com os créditos do comfy.org "
        "(seletor `rota`). Gera uma cena nova guiada por referências — não edita o vídeo."
    )

    def generate(
        self,
        model,
        rota,
        prompt,
        resolution,
        aspect_ratio,
        duration,
        generate_audio,
        seed,
        image_1=None,
        image_2=None,
        image_3=None,
        image_4=None,
        video_1=None,
        video_2=None,
        audio_1=None,
        bitrate_mode="standard",
        end_user_id="",
        auth_token=None,
        comfy_api_key=None,
    ):
        images = _collect(image_1, image_2, image_3, image_4)
        videos = _collect(video_1, video_2)
        audios = _collect(audio_1)

        # ------------------------------------------------------------------ #
        # Rota dos créditos comfy.org                                        #
        # ------------------------------------------------------------------ #
        if rota == ROTA_COMFY:
            partner_model = COMFY_SEEDANCE_MODELS.get(model)
            if partner_model is None:
                disponiveis = ", ".join(COMFY_SEEDANCE_MODELS)
                raise ValueError(
                    f"A rota de créditos comfy.org só tem: {disponiveis}. "
                    f"O modelo '{model}' só existe na rota '{ROTA_FAL}'. "
                    "Troque o modelo ou troque a rota."
                )
            _validate(prompt, images, videos, audios, model, resolution)

            headers = _comfy_headers(auth_token, comfy_api_key)
            content = [{"type": "text", "text": _translate_labels_to_partner(prompt)}]
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": _comfy_upload_image(img, headers)},
                    "role": "reference_image",
                })
            for vid in videos:
                content.append({
                    "type": "video_url",
                    "video_url": {"url": _comfy_upload_video(vid, headers)},
                    "role": "reference_video",
                })
            if audios:
                print(
                    "[Seedance BYOK] AVISO: áudio de referência não foi enviado na rota "
                    "comfy.org (o upload de áudio não está implementado aqui). Use a rota "
                    f"'{ROTA_FAL}' se precisar dele."
                )

            body = {
                "model": partner_model,
                "content": content,
                "generate_audio": bool(generate_audio),
                "resolution": resolution,
                "ratio": "adaptive" if aspect_ratio == "auto" else aspect_ratio,
                "watermark": False,
            }
            if duration != "auto":
                body["duration"] = int(duration)

            url = _run_comfy_seedance(body, headers)
            return (_download_video(url), url)

        _validate(prompt, images, videos, audios, model, resolution)

        endpoint, _, supports_bitrate = MODELS[model]
        client = _client()

        arguments = {
            "prompt": prompt,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "generate_audio": bool(generate_audio),
        }
        if images:
            arguments["image_urls"] = [_upload_image(client, img) for img in images]
        if videos:
            arguments["video_urls"] = [_upload_video(client, vid) for vid in videos]
        if audios:
            arguments["audio_urls"] = [_upload_audio(client, aud) for aud in audios]
        if supports_bitrate:
            arguments["bitrate_mode"] = bitrate_mode
        if end_user_id.strip():
            arguments["end_user_id"] = end_user_id.strip()

        result = _run(f"{endpoint}/reference-to-video", arguments)
        url = result["video"]["url"]
        return (_download_video(url), url)


class SeedanceBYOKImageToVideo:
    """Image-to-video com primeiro (e opcionalmente ultimo) frame — o encadeador de clipes."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (MODEL_NAMES, {"default": "Seedance 2.0"}),
                "first_frame": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "The camera slowly pushes in."}),
                "resolution": (RESOLUTIONS, {"default": "720p"}),
                "aspect_ratio": (ASPECT_RATIOS, {"default": "auto"}),
                "duration": (DURATIONS, {"default": "auto"}),
                "generate_audio": ("BOOLEAN", {"default": True}),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True},
                ),
            },
            "optional": {
                "last_frame": ("IMAGE", {"tooltip": "Opcional: fecha o clipe neste frame."}),
                "bitrate_mode": (["standard", "high"], {"default": "standard"}),
                "end_user_id": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "video_url")
    FUNCTION = "generate"
    CATEGORY = "Seedance BYOK"
    DESCRIPTION = (
        "Seedance image-to-video (first/last frame) pela fal.ai com a SUA FAL_KEY. "
        "Use para encadear clipes e passar dos 15 s."
    )

    def generate(
        self,
        model,
        first_frame,
        prompt,
        resolution,
        aspect_ratio,
        duration,
        generate_audio,
        seed,
        last_frame=None,
        bitrate_mode="standard",
        end_user_id="",
    ):
        if not prompt or not prompt.strip():
            raise ValueError("O prompt e obrigatorio.")
        endpoint, allowed, supports_bitrate = MODELS[model]
        if resolution not in allowed:
            raise ValueError(
                f"'{model}' nao aceita {resolution}. Validas: {', '.join(allowed)}."
            )

        client = _client()
        arguments = {
            "prompt": prompt,
            "image_url": _upload_image(client, first_frame),
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "generate_audio": bool(generate_audio),
        }
        if last_frame is not None:
            arguments["end_image_url"] = _upload_image(client, last_frame)
        if supports_bitrate:
            arguments["bitrate_mode"] = bitrate_mode
        if end_user_id.strip():
            arguments["end_user_id"] = end_user_id.strip()

        result = _run(f"{endpoint}/image-to-video", arguments)
        url = result["video"]["url"]
        return (_download_video(url), url)


class WanAnimateBYOK:
    """O oposto do Seedance: EDITA o seu video, preservando o plano.

    Wan 2.2 Animate recebe o video original e troca (replace) ou anima (move) a
    pessoa nele, mantendo movimento, enquadramento, cortes e fundo. Nao tem prompt
    e nao tem mascara — a performance sai do proprio video.
    """

    MODES = {
        "replace — trocar a pessoa do video": "fal-ai/wan/v2.2-14b/animate/replace",
        "move — animar a foto com o movimento do video": "fal-ai/wan/v2.2-14b/animate/move",
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(cls.MODES.keys()), {"default": "replace — trocar a pessoa do video"}),
                "image": ("IMAGE", {"tooltip": "A pessoa que ENTRA. Foto de corpo inteiro."}),
                "video": ("VIDEO", {"tooltip": "O video a EDITAR. Comece com 3-6 s."}),
                "resolution": (["480p", "580p", "720p"], {"default": "480p"}),
                "use_turbo": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Rota rapida e barata, com otimizacao automatica."},
                ),
                "num_inference_steps": ("INT", {"default": 20, "min": 1, "max": 40}),
                "guidance_scale": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 1.0,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "⚠️ Modelo destilado: acima de 1.0 BORRA o video. Deixe em 1.0.",
                    },
                ),
                "shift": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 10.0, "step": 0.1}),
                "video_quality": (["low", "medium", "high", "maximum"], {"default": "high"}),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 2147483647,
                        "control_after_generate": True,
                        "tooltip": "Este endpoint ACEITA seed de verdade — 0 usa aleatoria.",
                    },
                ),
            },
            "optional": {
                "enable_safety_checker": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING", "STRING")
    RETURN_NAMES = ("video", "video_url", "prompt_gerado")
    FUNCTION = "generate"
    CATEGORY = "Seedance BYOK"
    DESCRIPTION = (
        "Wan 2.2 Animate pela fal.ai com a SUA FAL_KEY. EDITA o video original preservando "
        "movimento, enquadramento, cortes e fundo — o contrario do Seedance."
    )

    def generate(self, mode, image, video, resolution, use_turbo, num_inference_steps,
                 guidance_scale, shift, video_quality, seed, enable_safety_checker=False):
        if guidance_scale > 1.0:
            print(
                "[Wan Animate BYOK] AVISO: guidance_scale > 1.0 num modelo destilado costuma "
                "BORRAR o video. O valor recomendado e 1.0."
            )
        client = _client()
        arguments = {
            "image_url": _upload_image(client, image),
            "video_url": _upload_video(client, video),
            "resolution": resolution,
            "use_turbo": bool(use_turbo),
            "num_inference_steps": int(num_inference_steps),
            "guidance_scale": float(guidance_scale),
            "shift": float(shift),
            "video_quality": video_quality,
            "enable_safety_checker": bool(enable_safety_checker),
        }
        if seed:
            arguments["seed"] = int(seed)

        result = _run(self.MODES[mode], arguments)
        url = result["video"]["url"]
        return (_download_video(url), url, result.get("prompt") or "")


class VideoUpscaleBYOK:
    """Passe final de upscale — mais pixel no rosto, que e onde a identidade mora.

    O equivalente em video do passe de restauracao de rosto em foto: rodar o clipe
    barato (480p/720p) e so depois ampliar custa menos e entrega mais detalhe do que
    gerar direto em alta.

    Dois motores, com forcas diferentes:
      Topaz  — controle fino (denoise, compressao, grao, recuperacao de detalhe) e
               interpolacao de fps opcional. Melhor para material degradado.
      SeedVR — difusao; reconstroi detalhe em vez de so interpolar. Costuma ser melhor
               em ROSTO, que e o caso deste bundle.
    """

    ENGINES = {
        "SeedVR — melhor em rosto (padrão)": "fal-ai/seedvr/upscale/video",
        "Topaz — controle fino e fps": "fal-ai/topaz/upscale/video",
    }

    TOPAZ_MODELS = ["Proteus", "Artemis HQ", "Artemis MQ", "Gaia HQ", "Nyx", "Starlight HQ"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "engine": (list(cls.ENGINES.keys()), {"default": list(cls.ENGINES.keys())[0]}),
                "upscale_factor": (
                    "FLOAT",
                    {
                        "default": 2.0,
                        "min": 1.0,
                        "max": 4.0,
                        "step": 0.5,
                        "tooltip": "2.0 dobra largura e altura. 480p -> 960p.",
                    },
                ),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True},
                ),
            },
            "optional": {
                "seedvr_output_quality": (
                    ["low", "medium", "high", "maximum"],
                    {"default": "high", "tooltip": "Só o SeedVR usa."},
                ),
                "topaz_model": (
                    cls.TOPAZ_MODELS,
                    {"default": "Proteus", "tooltip": "Só o Topaz usa. Proteus serve à maioria."},
                ),
                "topaz_target_fps": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 120,
                        "tooltip": "Só o Topaz. 0 = não interpola. >0 liga interpolação de frames.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "video_url")
    FUNCTION = "upscale"
    CATEGORY = "Seedance BYOK"
    DESCRIPTION = (
        "Upscale de vídeo pela fal com a SUA FAL_KEY (SeedVR ou Topaz). Passe final: "
        "gere barato em 480p/720p e amplie depois — mais pixel de rosto pelo mesmo dinheiro."
    )

    def upscale(self, video, engine, upscale_factor, seed,
                seedvr_output_quality="high", topaz_model="Proteus", topaz_target_fps=0):
        endpoint = self.ENGINES[engine]
        client = _client()
        video_url = _upload_video(client, video)

        if "seedvr" in endpoint:
            arguments = {
                "video_url": video_url,
                "upscale_mode": "factor",
                "upscale_factor": float(upscale_factor),
                "output_quality": seedvr_output_quality,
            }
            if seed:
                arguments["seed"] = int(seed)
        else:
            arguments = {
                "video_url": video_url,
                "upscale_factor": float(upscale_factor),
                "model": topaz_model,
            }
            if topaz_target_fps > 0:
                arguments["target_fps"] = int(topaz_target_fps)

        result = _run(endpoint, arguments)
        info = result.get("video") or {}
        url = info.get("url") if isinstance(info, dict) else None
        if not url:
            raise RuntimeError(f"resposta sem vídeo: {str(result)[:400]}")
        return (_download_video(url), url)


class SeedanceBYOKLastFrame:
    """Ultimo frame de um VIDEO como IMAGE — a emenda entre clipes encadeados."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "offset_from_end": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 60,
                        "tooltip": "0 = ultimo frame. Suba 1-3 se o ultimo frame estiver borrado.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "extract"
    CATEGORY = "Seedance BYOK"
    DESCRIPTION = "Extrai o ultimo frame de um VIDEO para alimentar o proximo clipe."

    def extract(self, video, offset_from_end):
        components = video.get_components()
        frames = components.images
        if frames is None or len(frames) == 0:
            raise ValueError("O video nao tem frames.")
        index = max(0, len(frames) - 1 - int(offset_from_end))
        return (frames[index : index + 1],)


class SeedanceBYOKCheckKey:
    """Diagnostico barato: a chave existe e a fal responde? Rode ANTES de gastar credito."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "check"
    CATEGORY = "Seedance BYOK"
    OUTPUT_NODE = True
    DESCRIPTION = "Confere se a FAL_KEY esta carregada e quais endpoints Seedance respondem."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # sempre reexecuta

    def check(self):
        import requests

        lines = []
        try:
            key = _get_key()
            lines.append(f"FAL_KEY: carregada (…{key[-4:]})")
        except RuntimeError as exc:
            return (f"FAL_KEY: AUSENTE\n\n{exc}",)

        targets = [(name, f"{ep}/reference-to-video") for name, (ep, _, _) in MODELS.items()]
        targets += [(f"Wan Animate ({mode.split(' ')[0]})", ep)
                    for mode, ep in WanAnimateBYOK.MODES.items()]

        for name, endpoint in targets:
            url = f"https://fal.ai/api/openapi/queue/openapi.json?endpoint_id={endpoint}"
            try:
                code = requests.get(url, timeout=20).status_code
            except Exception as exc:  # pragma: no cover
                lines.append(f"{name}: erro de rede ({exc})")
                continue
            verdict = "roteavel" if code == 200 else f"INDISPONIVEL (HTTP {code})"
            lines.append(f"{name}: {verdict}")

        lines.append(
            "\nObs.: 'roteavel' significa que o endpoint EXISTE e responde. Se o Seedance 2.5 "
            "ainda nao estiver liberado publicamente, a geracao pode falhar na submissao "
            "mesmo com o endpoint roteavel."
        )
        return ("\n".join(lines),)


NODE_CLASS_MAPPINGS = {
    "SeedanceBYOKReferenceToVideo": SeedanceBYOKReferenceToVideo,
    "SeedanceBYOKImageToVideo": SeedanceBYOKImageToVideo,
    "WanAnimateBYOK": WanAnimateBYOK,
    "VideoUpscaleBYOK": VideoUpscaleBYOK,
    "SeedanceBYOKLastFrame": SeedanceBYOKLastFrame,
    "SeedanceBYOKCheckKey": SeedanceBYOKCheckKey,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceBYOKReferenceToVideo": "Seedance BYOK · Reference to Video",
    "SeedanceBYOKImageToVideo": "Seedance BYOK · Image to Video (first/last)",
    "WanAnimateBYOK": "Wan Animate BYOK · Editar o video original",
    "VideoUpscaleBYOK": "Video BYOK · Upscale (passe final)",
    "SeedanceBYOKLastFrame": "Seedance BYOK · Ultimo Frame",
    "SeedanceBYOKCheckKey": "Seedance BYOK · Testar Chave",
}
