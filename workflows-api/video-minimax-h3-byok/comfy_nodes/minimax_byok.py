"""MiniMax H3 BYOK — nos que falam DIRETO com a API v2 da MiniMax usando a sua chave.

Rota 100% online: nenhum modelo roda nesta maquina. (O tutorial do comfy.org para o
MiniMax H3 e sobre os pesos ABERTOS rodando em GPU local — outra coisa; ver o README.)

Contrato confirmado ao vivo em 2026-08-04:
  POST https://api.minimax.io/v1/files/upload            (multipart, purpose=video_generation_input)
  POST https://api.minimax.io/v2/video_generation        -> {"task_id": "..."}
  GET  https://api.minimax.io/v2/query/video_generation/{task_id}
       -> {"task": {"status": "...", "content": {"url": "..."}}}
  Header: Authorization: Bearer <MINIMAX_API_KEY>

Docs: https://platform.minimax.io/docs/api-reference/video-generation-v2-create
"""

from __future__ import annotations

import io
import json
import os
import time
import wave

import numpy as np
import torch
from PIL import Image

import folder_paths

try:  # disponivel dentro do ComfyUI
    import comfy.model_management as model_management
except Exception:  # pragma: no cover
    model_management = None

from comfy_api.latest import InputImpl


# --------------------------------------------------------------------------- #
# Constantes da API                                                            #
# --------------------------------------------------------------------------- #

DEFAULT_HOST = "https://api.minimax.io"
MODEL_ID = "MiniMax-H3"

RESOLUTIONS = ["768P", "2K"]
# 'adaptive' herda o formato da imagem/video de entrada. Text-to-video EXIGE um explicito.
RATIOS_EXPLICIT = ["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]
RATIOS = ["adaptive"] + RATIOS_EXPLICIT
DURATIONS = [str(n) for n in range(4, 16)]

POLL_SECONDS = 5.0
PROMPT_MAX_CHARS = 7000

# Limites documentados (o servidor recusa se passar; validamos antes de gastar).
MAX_REF_IMAGES, MAX_REF_VIDEOS, MAX_REF_AUDIOS = 9, 3, 3
IMG_MIN_PX, IMG_MAX_PX = 256, 5760
IMG_MIN_RATIO, IMG_MAX_RATIO = 0.4, 2.5


def _host() -> str:
    """Permite apontar para outro host (ex.: a plataforma da China) sem editar codigo."""
    return os.environ.get("MINIMAX_API_HOST", DEFAULT_HOST).rstrip("/")


# --------------------------------------------------------------------------- #
# Chave                                                                        #
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
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key
    for candidate in (
        os.path.join(os.path.expanduser("~"), "ComfyUI", "secrets.env"),
        os.path.join(folder_paths.base_path, "secrets.env"),
    ):
        key = _read_secrets_env(candidate, "MINIMAX_API_KEY")
        if key:
            os.environ["MINIMAX_API_KEY"] = key
            return key
    raise RuntimeError(
        "MINIMAX_API_KEY nao encontrada. Grave a chave e reinicie o ComfyUI:\n"
        "  printf 'MINIMAX_API_KEY=%s\\n' \"SUA_CHAVE\" >> ~/ComfyUI/secrets.env\n"
        "  chmod 600 ~/ComfyUI/secrets.env\n"
        "Como pegar a chave: platform.minimax.io -> Console -> API Keys "
        "(o valor aparece UMA vez so). Passo a passo no README do bundle."
    )


def _headers(json_body: bool = True) -> dict:
    head = {"Authorization": f"Bearer {_get_key()}"}
    if json_body:
        head["Content-Type"] = "application/json"
    return head


def _temp_path(suffix: str) -> str:
    directory = folder_paths.get_temp_directory()
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"minimax_byok_{os.getpid()}_{time.time_ns()}{suffix}")


def _cleanup(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Upload -> mm_file://                                                         #
# --------------------------------------------------------------------------- #

def _upload_path(path: str) -> str:
    """Sobe o arquivo e devolve a referencia `mm_file://<id>` (vale 7 dias).

    Preferimos upload a data-URI base64: o corpo do POST de geracao tem teto de
    64 MB e base64 infla ~33%, entao um video de referencia estoura facil.
    """
    import requests

    url = f"{_host()}/v1/files/upload"
    with open(path, "rb") as fh:
        response = requests.post(
            url,
            headers=_headers(json_body=False),
            data={"purpose": "video_generation_input"},
            files={"file": (os.path.basename(path), fh)},
            timeout=600,
        )
    if response.status_code != 200:
        raise RuntimeError(f"upload falhou (HTTP {response.status_code}): {response.text[:500]}")

    payload = response.json()
    base = payload.get("base_resp") or {}
    if base.get("status_code") not in (0, None):
        raise RuntimeError(f"upload recusado: {base.get('status_msg')} (code {base.get('status_code')})")
    file_id = (payload.get("file") or {}).get("file_id")
    if not file_id:
        raise RuntimeError(f"upload sem file_id na resposta: {json.dumps(payload)[:500]}")
    return f"mm_file://{file_id}"


def _upload_image(image: torch.Tensor) -> str:
    frame = image[0] if image.dim() == 4 else image
    array = np.clip(frame.cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    pil = Image.fromarray(array)
    if pil.mode not in ("RGB", "RGBA"):
        pil = pil.convert("RGB")
    width, height = pil.size
    if not (IMG_MIN_PX <= width <= IMG_MAX_PX and IMG_MIN_PX <= height <= IMG_MAX_PX):
        raise ValueError(
            f"Imagem {width}x{height} fora do limite da API (cada lado entre "
            f"{IMG_MIN_PX} e {IMG_MAX_PX} px)."
        )
    ratio = width / height
    if not (IMG_MIN_RATIO <= ratio <= IMG_MAX_RATIO):
        raise ValueError(
            f"Proporcao {ratio:.2f} fora do limite da API ({IMG_MIN_RATIO}–{IMG_MAX_RATIO}). "
            "Recorte a imagem para algo mais proximo de 16:9 ou 9:16."
        )
    path = _temp_path(".png")
    pil.save(path, format="PNG")
    try:
        return _upload_path(path)
    finally:
        _cleanup(path)


def _upload_video(video) -> str:
    source = None
    try:
        source = video.get_stream_source()
    except Exception:
        source = None
    if isinstance(source, str) and os.path.isfile(source):
        return _upload_path(source)
    path = _temp_path(".mp4")
    try:
        video.save_to(path)
        return _upload_path(path)
    finally:
        _cleanup(path)


def _upload_audio(audio) -> str:
    waveform = audio["waveform"]
    sample_rate = int(audio["sample_rate"])
    if waveform.dim() == 3:
        waveform = waveform[0]
    samples = np.clip(waveform.cpu().numpy(), -1.0, 1.0)
    pcm = (samples * 32767.0).astype(np.int16).T
    path = _temp_path(".wav")
    try:
        with wave.open(path, "wb") as handle:
            handle.setnchannels(pcm.shape[1])
            handle.setsampwidth(2)
            handle.setframerate(sample_rate)
            handle.writeframes(pcm.tobytes())
        return _upload_path(path)
    finally:
        _cleanup(path)


# --------------------------------------------------------------------------- #
# Criar tarefa + polling                                                       #
# --------------------------------------------------------------------------- #

def _run(payload: dict) -> str:
    """Cria a tarefa, faz polling e devolve a URL do video. Respeita o Cancel."""
    import requests

    create_url = f"{_host()}/v2/video_generation"
    print(f"[MiniMax BYOK] POST {create_url}  model={payload.get('model')} "
          f"res={payload.get('resolution')} dur={payload.get('duration')}")
    response = requests.post(create_url, headers=_headers(), json=payload, timeout=300)
    if response.status_code != 200:
        raise RuntimeError(_explain_error(response))

    task_id = response.json().get("task_id")
    if not task_id:
        raise RuntimeError(f"resposta sem task_id: {response.text[:500]}")
    print(f"[MiniMax BYOK] task_id={task_id}")

    query_url = f"{_host()}/v2/query/video_generation/{task_id}"
    started = time.time()
    last_status = ""
    while True:
        if model_management is not None:
            model_management.throw_exception_if_processing_interrupted()

        poll = requests.get(query_url, headers=_headers(json_body=False), timeout=120)
        if poll.status_code != 200:
            raise RuntimeError(_explain_error(poll))
        task = poll.json().get("task") or {}
        status = task.get("status", "")

        if status != last_status:
            print(f"[MiniMax BYOK] {status}… {int(time.time() - started)}s")
            last_status = status

        if status == "succeeded":
            url = (task.get("content") or {}).get("url")
            if not url:
                raise RuntimeError(f"tarefa concluida sem URL: {json.dumps(task)[:500]}")
            usage = task.get("usage") or {}
            if usage:
                print(f"[MiniMax BYOK] uso: {json.dumps(usage)}")
            print(f"[MiniMax BYOK] pronto em {int(time.time() - started)}s")
            return url
        if status in ("failed", "cancelled"):
            err = task.get("error") or {}
            raise RuntimeError(
                f"tarefa {status}: {err.get('message') or json.dumps(task)[:500]}"
            )
        time.sleep(POLL_SECONDS)


def _explain_error(response) -> str:
    """Traduz os erros documentados para algo acionavel."""
    try:
        body = response.json()
        err = body.get("error") or {}
        kind = err.get("type", "")
        message = err.get("message", response.text[:300])
    except Exception:
        kind, message = "", response.text[:300]

    dicas = {
        "authorized_error": "chave ausente ou invalida — confira a MINIMAX_API_KEY",
        "insufficient_balance_error": "saldo insuficiente — adicione credito no console da MiniMax",
        "unprocessable_entity_error": "conteudo bloqueado pela moderacao",
        "rate_limit_error": "limite de requisicoes — espere e tente de novo",
        "bad_request_error": "payload invalido — confira prompt, resolucao, duracao e roles",
    }
    dica = dicas.get(kind, "")
    sufixo = f" ({dica})" if dica else ""
    return f"MiniMax HTTP {response.status_code} [{kind}]{sufixo}: {message}"


def _download_video(url: str):
    """Baixa o MP4 e devolve VIDEO nativo — o audio vem no container.

    A URL da MiniMax e temporaria; por isso baixamos na hora.
    """
    import requests

    response = requests.get(url, timeout=900)
    response.raise_for_status()
    return InputImpl.VideoFromFile(io.BytesIO(response.content))


# --------------------------------------------------------------------------- #
# Montagem do content[]                                                        #
# --------------------------------------------------------------------------- #

def _text_item(prompt: str) -> dict:
    if not prompt or not prompt.strip():
        raise ValueError("A API exige sempre um item de texto nao-vazio no content.")
    if len(prompt) > PROMPT_MAX_CHARS:
        raise ValueError(f"Prompt com {len(prompt)} caracteres; o maximo e {PROMPT_MAX_CHARS}.")
    return {"type": "text", "text": prompt}


def _collect(*values):
    return [v for v in values if v is not None]


# --------------------------------------------------------------------------- #
# Nos                                                                          #
# --------------------------------------------------------------------------- #

class MiniMaxH3BYOKReferenceToVideo:
    """Reference-to-video: cena NOVA guiada por imagens, videos e audio de referencia."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "The person in reference image 1 stands in the location shown in "
                            "reference image 2, looking around and smiling."
                        ),
                        "tooltip": "Cite as referencias em linguagem natural: 'reference image 1', "
                                   "'reference video 1'. A numeracao segue a ORDEM dos slots.",
                    },
                ),
                "resolution": (RESOLUTIONS, {"default": "768P"}),
                "duration": (DURATIONS, {"default": "6"}),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 2147483647,
                        "control_after_generate": True,
                        "tooltip": "NAO vai para a API (a v2 nao aceita seed). Forca re-execucao do no.",
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
                "callback_url": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "video_url")
    FUNCTION = "generate"
    CATEGORY = "MiniMax BYOK"
    DESCRIPTION = (
        "MiniMax H3 reference-to-video pela API v2 com a SUA MINIMAX_API_KEY. Gera uma cena "
        "nova guiada por referencias — nao edita o video de origem."
    )

    def generate(self, prompt, resolution, duration, seed,
                 image_1=None, image_2=None, image_3=None, image_4=None,
                 video_1=None, video_2=None, audio_1=None, callback_url=""):
        images = _collect(image_1, image_2, image_3, image_4)
        videos = _collect(video_1, video_2)
        audios = _collect(audio_1)

        if len(images) > MAX_REF_IMAGES:
            raise ValueError(f"Maximo {MAX_REF_IMAGES} imagens de referencia.")
        if len(videos) > MAX_REF_VIDEOS:
            raise ValueError(f"Maximo {MAX_REF_VIDEOS} videos de referencia.")
        if len(audios) > MAX_REF_AUDIOS:
            raise ValueError(f"Maximo {MAX_REF_AUDIOS} audios de referencia.")
        if audios and not (images or videos):
            raise ValueError("Audio de referencia nao pode aparecer sozinho.")
        if not (images or videos or audios):
            raise ValueError(
                "Reference-to-video sem nenhuma referencia. Ligue ao menos uma imagem ou "
                "video — ou use o no de Text to Video."
            )

        content = [_text_item(prompt)]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": _upload_image(img)},
                "role": "reference_image",
            })
        for vid in videos:
            content.append({
                "type": "video_url",
                "video_url": {"url": _upload_video(vid)},
                "role": "reference_video",
            })
        for aud in audios:
            content.append({
                "type": "audio_url",
                "audio_url": {"url": _upload_audio(aud)},
                "role": "reference_audio",
            })

        payload = {
            "model": MODEL_ID,
            "content": content,
            "resolution": resolution,
            "duration": int(duration),
        }
        if callback_url.strip():
            payload["callback_url"] = callback_url.strip()

        url = _run(payload)
        return (_download_video(url), url)


class MiniMaxH3BYOKImageToVideo:
    """Image-to-video: primeiro frame (e opcionalmente ultimo). O encadeador de clipes."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_frame": ("IMAGE",),
                "prompt": (
                    "STRING",
                    {"multiline": True, "default": "The camera slowly pushes in."},
                ),
                "resolution": (RESOLUTIONS, {"default": "768P"}),
                "duration": (DURATIONS, {"default": "6"}),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True},
                ),
            },
            "optional": {
                "last_frame": ("IMAGE", {"tooltip": "Opcional: fecha o clipe neste frame."}),
                "callback_url": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "video_url")
    FUNCTION = "generate"
    CATEGORY = "MiniMax BYOK"
    DESCRIPTION = (
        "MiniMax H3 image-to-video (primeiro/ultimo frame) pela API v2. O formato e sempre "
        "'adaptive' — herdado da imagem."
    )

    def generate(self, first_frame, prompt, resolution, duration, seed,
                 last_frame=None, callback_url=""):
        content = [_text_item(prompt), {
            "type": "image_url",
            "image_url": {"url": _upload_image(first_frame)},
            "role": "first_frame",
        }]
        if last_frame is not None:
            content.append({
                "type": "image_url",
                "image_url": {"url": _upload_image(last_frame)},
                "role": "last_frame",
            })

        payload = {
            "model": MODEL_ID,
            "content": content,
            "resolution": resolution,
            "duration": int(duration),
        }
        # 'ratio' nao e enviado: image-to-video forca 'adaptive' do lado da API.
        if callback_url.strip():
            payload["callback_url"] = callback_url.strip()

        url = _run(payload)
        return (_download_video(url), url)


class MiniMaxH3BYOKTextToVideo:
    """Text-to-video puro. Unico modo em que o `ratio` e obrigatorio e explicito."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {"multiline": True, "default": "A cinematic establishing shot of a quiet street at dawn."},
                ),
                "ratio": (
                    RATIOS_EXPLICIT,
                    {
                        "default": "16:9",
                        "tooltip": "Text-to-video EXIGE um formato explicito — 'adaptive' nao vale aqui.",
                    },
                ),
                "resolution": (RESOLUTIONS, {"default": "768P"}),
                "duration": (DURATIONS, {"default": "6"}),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": 2147483647, "control_after_generate": True},
                ),
            },
            "optional": {
                "callback_url": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "video_url")
    FUNCTION = "generate"
    CATEGORY = "MiniMax BYOK"
    DESCRIPTION = "MiniMax H3 text-to-video pela API v2 com a SUA MINIMAX_API_KEY."

    def generate(self, prompt, ratio, resolution, duration, seed, callback_url=""):
        payload = {
            "model": MODEL_ID,
            "content": [_text_item(prompt)],
            "resolution": resolution,
            "duration": int(duration),
            "ratio": ratio,
        }
        if callback_url.strip():
            payload["callback_url"] = callback_url.strip()
        url = _run(payload)
        return (_download_video(url), url)


class MiniMaxH3BYOKLastFrame:
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
    CATEGORY = "MiniMax BYOK"
    DESCRIPTION = "Extrai o ultimo frame de um VIDEO para alimentar o proximo clipe."

    def extract(self, video, offset_from_end):
        frames = video.get_components().images
        if frames is None or len(frames) == 0:
            raise ValueError("O video nao tem frames.")
        index = max(0, len(frames) - 1 - int(offset_from_end))
        return (frames[index : index + 1],)


class MiniMaxH3BYOKCheckKey:
    """Diagnostico barato: a chave existe e a API responde? Rode ANTES de gastar."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "check"
    CATEGORY = "MiniMax BYOK"
    OUTPUT_NODE = True
    DESCRIPTION = "Confere a MINIMAX_API_KEY e se a API v2 aceita a credencial."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def check(self):
        import requests

        lines = [f"Host: {_host()}"]
        try:
            key = _get_key()
            lines.append(f"MINIMAX_API_KEY: carregada (…{key[-4:]})")
        except RuntimeError as exc:
            return (f"MINIMAX_API_KEY: AUSENTE\n\n{exc}",)

        # Consulta um task_id inexistente: 401 = chave ruim; 4xx != 401 = chave aceita.
        try:
            probe = requests.get(
                f"{_host()}/v2/query/video_generation/0",
                headers=_headers(json_body=False),
                timeout=30,
            )
        except Exception as exc:  # pragma: no cover
            return ("\n".join(lines + [f"Rede: FALHOU ({exc})"]),)

        if probe.status_code == 401:
            lines.append("Autenticacao: RECUSADA (401) — a chave e invalida ou expirou.")
        else:
            lines.append(f"Autenticacao: aceita (a consulta devolveu HTTP {probe.status_code}, "
                         "que nao e 401).")
            lines.append("Endpoint de geracao: " + f"{_host()}/v2/video_generation")

        lines.append(
            "\nObs.: isto confirma credencial e alcance da API. Nao confirma saldo — "
            "sem credito a geracao falha com 'insufficient_balance_error'."
        )
        return ("\n".join(lines),)


NODE_CLASS_MAPPINGS = {
    "MiniMaxH3BYOKReferenceToVideo": MiniMaxH3BYOKReferenceToVideo,
    "MiniMaxH3BYOKImageToVideo": MiniMaxH3BYOKImageToVideo,
    "MiniMaxH3BYOKTextToVideo": MiniMaxH3BYOKTextToVideo,
    "MiniMaxH3BYOKLastFrame": MiniMaxH3BYOKLastFrame,
    "MiniMaxH3BYOKCheckKey": MiniMaxH3BYOKCheckKey,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MiniMaxH3BYOKReferenceToVideo": "MiniMax H3 BYOK · Reference to Video",
    "MiniMaxH3BYOKImageToVideo": "MiniMax H3 BYOK · Image to Video (first/last)",
    "MiniMaxH3BYOKTextToVideo": "MiniMax H3 BYOK · Text to Video",
    "MiniMaxH3BYOKLastFrame": "MiniMax H3 BYOK · Ultimo Frame",
    "MiniMaxH3BYOKCheckKey": "MiniMax H3 BYOK · Testar Chave",
}
