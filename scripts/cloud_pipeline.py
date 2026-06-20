#!/usr/bin/env python3
"""
Cloud Pipeline — TryOff + SCAIL-2 via Replicate + fal.ai
=========================================================
Substitui execução local dos workflows ComfyUI por APIs cloud.

Requer:
  export REPLICATE_API_TOKEN="r8_..."
  export FAL_KEY="fal-..."

Uso:
  python scripts/cloud_pipeline.py \
    --reference reference.jpg \
    --driving driving.mp4 \
    --prompt "a person dancing samba at carnival" \
    --output final_animation.mp4

Fluxo:
  Step 1a — Upload reference + generate mask (Segformer offline ou via Replicate)
  Step 1b — mmezhov/catvton-flux (try_off=false) → garment + tryoff outputs
  Step 1c — Composição Pillow: paste tryoff_output onto original via blurred mask
  Step 2  — fal-ai/scail-2 com a imagem composta + vídeo condutor → vídeo final
"""

import argparse
import os
import sys
import time
import json
import base64
import tempfile
import urllib.request
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image, ImageFilter


# ── Config ──────────────────────────────────────────────────────────

REPLICATE_MODEL = "mmezhov/catvton-flux:cc41d1b963023987ed2ddf26e9264efcc96ee076640115c303f95b0010f6a958"
FAL_SCAIL_MODEL = "fal-ai/scail-2"
REPLICATE_API = "https://api.replicate.com/v1"
FAL_API = "https://fal.run"


# ── Helpers ─────────────────────────────────────────────────────────

def upload_to_tmp_public(filepath: str) -> str:
    """
    Upload a file to a publicly accessible URL.
    Uses transfer.sh (free, no auth) for temporary hosting.
    For production, use S3/GCS/R2 presigned URLs.
    """
    fname = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        resp = requests.put(f"https://transfer.sh/{fname}", data=f)
    resp.raise_for_status()
    url = resp.text.strip()
    print(f"  ↳ uploaded: {url}")
    return url


def image_to_data_uri(filepath: str) -> str:
    """Convert image file to data URI (for Replicate <1MB inputs)."""
    with open(filepath, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = Path(filepath).suffix.lower().replace("jpg", "jpeg").lstrip(".")
    return f"data:image/{ext};base64,{data}"


def download_file(url: str, outpath: str):
    """Download a file from URL to local path."""
    print(f"  ↳ downloading: {url[:80]}...")
    urllib.request.urlretrieve(url, outpath)
    print(f"  ↳ saved: {outpath}")


# ── Step 1a: Generate clothing mask ─────────────────────────────────

def generate_mask_replicate(image_path: str) -> str:
    """
    Generate Segformer clothing mask via Replicate.
    
    Uses a dedicated segformer model on Replicate if available,
    OR falls back to generating mask locally via Pillow (simple threshold).
    
    For production: use a hosted Segformer endpoint or pre-generate masks.
    """
    # TODO: Find a Replicate model for Segformer B2 clothes segmentation.
    # Currently falls back to a simple luminance-based mask.
    # Replace with actual Segformer API when available.
    
    print("[Step 1a] Generating clothing mask...")
    
    # For now, provide a way to use pre-generated masks or skip
    mask_path = image_path.replace(".jpg", "_mask.png").replace(".jpeg", "_mask.png").replace(".png", "_mask.png")
    
    if os.path.exists(mask_path):
        print(f"  ↳ using pre-existing mask: {mask_path}")
        return mask_path
    
    print("  ⚠️  No pre-existing mask found and no Segformer API configured.")
    print("  Using simple luminance-based fallback mask.")
    print("  For production, generate masks via ComfyUI SegformerB2ClothesUltra or")
    print("  via Replicate model (search: 'segformer-b2-clothes' on replicate.com).")
    
    img = Image.open(image_path).convert("RGB")
    gray = img.convert("L")
    # Simple threshold-based mask (replace with real Segformer output)
    mask = gray.point(lambda p: 255 if 40 < p < 200 else 0)
    mask.save(mask_path)
    return mask_path


# ── Step 1b: Run TryOff via Replicate ───────────────────────────────

def run_tryoff_replicate(image_url: str, mask_url: str, hf_token: str,
                         num_steps: int = 20, guidance_scale: float = 12.0,
                         width: int = 768, height: int = 1024,
                         seed: int = 42) -> dict:
    """
    Execute catvton-flux try-off on Replicate.
    
    Returns: {"garment": local_path, "tryoff": local_path}
    
    mmezhov/catvton-flux outputs an array of 2 image URLs:
      output[0] = garment visualization
      output[1] = try-off result (masked person)
    """
    print(f"[Step 1b] Running TryOff on Replicate...")
    print(f"  model: {REPLICATE_MODEL}")
    print(f"  params: steps={num_steps}, guidance={guidance_scale}, seed={seed}")
    
    headers = {"Authorization": f"Bearer {os.environ['REPLICATE_API_TOKEN']}"}
    
    payload = {
        "version": REPLICATE_MODEL.split(":")[1],
        "input": {
            "hf_token": hf_token,
            "image": image_url,
            "mask": mask_url,
            "try_on": False,
            "num_steps": num_steps,
            "guidance_scale": guidance_scale,
            "width": width,
            "height": height,
            "seed": seed,
        }
    }
    
    # Create prediction
    resp = requests.post(
        f"{REPLICATE_API}/models/mmezhov/catvton-flux/predictions",
        headers=headers,
        json=payload
    )
    
    if resp.status_code != 201:
        print(f"  ❌ Replicate error: {resp.status_code}")
        print(f"  {resp.text[:500]}")
        sys.exit(1)
    
    prediction = resp.json()
    pred_id = prediction["id"]
    print(f"  prediction_id: {pred_id}")
    
    # Poll until complete
    while prediction["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(2)
        resp = requests.get(
            f"{REPLICATE_API}/predictions/{pred_id}",
            headers=headers
        )
        prediction = resp.json()
        status = prediction["status"]
        if status == "processing":
            print(f"  ⌛ processing...", end="\r")
    
    if prediction["status"] != "succeeded":
        print(f"\n  ❌ Prediction failed: {prediction.get('error', 'unknown')}")
        sys.exit(1)
    
    print(f"\n  ✅ completed in {prediction['metrics'].get('predict_time', '?')}s")
    
    output_urls = prediction["output"]
    # output[0] = garment, output[1] = tryoff
    garment_path = "output/tryoff_garment.png"
    tryoff_path = "output/tryoff_result.png"
    
    os.makedirs("output", exist_ok=True)
    download_file(output_urls[0], garment_path)
    download_file(output_urls[1], tryoff_path)
    
    return {"garment": garment_path, "tryoff": tryoff_path}


# ── Step 1c: Composite back onto original ───────────────────────────

def composite_clothing(original_path: str, tryoff_path: str, 
                       mask_path: str, blur_sigma: float = 3.0) -> str:
    """
    Composite tryoff result back onto original photo using blurred mask.
    
    Uses Pillow: Image.composite(source, destination, mask)
    This is equivalent to ComfyUI's ImageCompositeMasked.
    
    The mask from Segformer has:
      - white (255) = clothing region → use tryoff pixels
      - black (0)   = rest → use original pixels
    
    Formula: result = mask * tryoff + (1 - mask) * original
    """
    print(f"[Step 1c] Compositing clothing onto original...")
    
    original = Image.open(original_path).convert("RGB")
    tryoff = Image.open(tryoff_path).convert("RGB")
    mask = Image.open(mask_path).convert("L")
    
    # Resize everything to match
    w, h = original.size
    tryoff = tryoff.resize((w, h), Image.LANCZOS)
    mask = mask.resize((w, h), Image.LANCZOS)
    
    # Apply Gaussian blur to feather the mask edges
    mask_blurred = mask.filter(ImageFilter.GaussianBlur(blur_sigma))
    
    # Composite: where mask is white → use tryoff, where black → use original
    result = Image.composite(tryoff, original, mask_blurred)
    
    output_path = "output/reference_processed.png"
    result.save(output_path)
    print(f"  ↳ saved: {output_path}")
    return output_path


# ── Step 2: Run SCAIL-2 via fal.ai ──────────────────────────────────

def run_scail2_fal(reference_url: str, driving_video_url: str,
                   prompt: str, seed: int = 42,
                   replacement_mode: bool = True,
                   num_frames: int = 81) -> str:
    """
    Execute SCAIL-2 animation on fal.ai.
    
    Returns: local path to downloaded MP4 video.
    """
    print(f"[Step 2] Running SCAIL-2 on fal.ai...")
    print(f"  prompt: {prompt[:80]}...")
    print(f"  replacement_mode: {replacement_mode}")
    
    headers = {
        "Authorization": f"Key {os.environ['FAL_KEY']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "image_url": reference_url,
        "video_url": driving_video_url,
        "prompt": prompt,
        "seed": seed,
        "replacement_mode": replacement_mode,
        "num_frames": num_frames,
    }
    
    # Submit (async by default on fal)
    resp = requests.post(
        f"{FAL_API}/{FAL_SCAIL_MODEL}",
        headers=headers,
        json=payload
    )
    
    if resp.status_code == 200:
        # fal.ai pode responder sync ou com um request_id para polling
        result = resp.json()
        
        if "video" in result and "url" in result["video"]:
            video_url = result["video"]["url"]
        elif "video_url" in result:
            video_url = result["video_url"]
        else:
            # Try polling pattern
            request_id = result.get("request_id")
            if request_id:
                print(f"  request_id: {request_id}, polling...")
                video_url = _poll_fal_request(request_id, headers)
            else:
                print(f"  ❌ Unexpected fal response: {json.dumps(result, indent=2)[:500]}")
                sys.exit(1)
    elif resp.status_code == 202:
        # Async — poll for result
        request_id = resp.json().get("request_id")
        print(f"  request_id: {request_id}, polling...")
        video_url = _poll_fal_request(request_id, headers)
    else:
        print(f"  ❌ fal.ai error: {resp.status_code}")
        print(f"  {resp.text[:500]}")
        sys.exit(1)
    
    # Download video
    output_path = "output/scail2_animation.mp4"
    download_file(video_url, output_path)
    print(f"  ✅ SCAIL-2 complete → {output_path}")
    return output_path


def _poll_fal_request(request_id: str, headers: dict, 
                      timeout: int = 600, interval: int = 5) -> str:
    """Poll fal.ai request status until complete."""
    status_url = f"{FAL_API}/{FAL_SCAIL_MODEL}/requests/{request_id}/status"
    
    for _ in range(timeout // interval):
        time.sleep(interval)
        resp = requests.get(status_url, headers=headers)
        data = resp.json()
        status = data.get("status", "")
        
        if status == "COMPLETED":
            video_url = data.get("video_url") or data.get("video", {}).get("url")
            if video_url:
                return video_url
        elif status in ("FAILED", "CANCELLED"):
            print(f"  ❌ fal request {status}: {data}")
            sys.exit(1)
        else:
            print(f"  ⌛ {status}...", end="\r")
    
    print(f"  ❌ Timeout after {timeout}s")
    sys.exit(1)


# ── Main Pipeline ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cloud Pipeline: TryOff + SCAIL-2 via Replicate + fal.ai"
    )
    parser.add_argument("--reference", required=True, help="Reference photo (person)")
    parser.add_argument("--driving", required=True, help="Driving video (mp4)")
    parser.add_argument("--prompt", required=True, help="Animation prompt for SCAIL-2")
    parser.add_argument("--mask", help="Pre-generated clothing mask (optional)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--guidance", type=float, default=12.0)
    parser.add_argument("--output", default="output/scail2_animation.mp4")
    parser.add_argument("--skip-tryoff", action="store_true",
                        help="Skip TryOff step (use pre-processed reference)")
    parser.add_argument("--skip-composite", action="store_true",
                        help="Skip composition (use raw tryoff output)")
    
    args = parser.parse_args()
    
    # Check env vars
    if not args.skip_tryoff:
        if "REPLICATE_API_TOKEN" not in os.environ:
            print("❌ REPLICATE_API_TOKEN not set")
            sys.exit(1)
    if "FAL_KEY" not in os.environ:
        print("❌ FAL_KEY not set")
        sys.exit(1)
    
    os.makedirs("output", exist_ok=True)
    
    print("=" * 60)
    print("CLOUD PIPELINE: TryOff + SCAIL-2")
    print("=" * 60)
    
    # ── Step 1: TryOff + Composition ──
    if not args.skip_tryoff:
        # 1a — Upload files
        print("\n── Uploading inputs ──")
        ref_url = upload_to_tmp_public(args.reference)
        
        # 1b — Generate mask
        mask_path = args.mask or generate_mask_replicate(args.reference)
        mask_url = upload_to_tmp_public(mask_path)
        
        # 1c — Run TryOff on Replicate
        hf_token = os.environ.get("HF_TOKEN", "")
        if not hf_token:
            print("⚠️  HF_TOKEN not set. Replicate catvton-flux requires HF token for FLUX.1-dev license.")
            print("   Set HF_TOKEN env var or pass --skip-tryoff to use pre-processed reference.")
            sys.exit(1)
        
        result = run_tryoff_replicate(
            image_url=ref_url,
            mask_url=mask_url,
            hf_token=hf_token,
            num_steps=args.steps,
            guidance_scale=args.guidance,
            seed=args.seed,
        )
        
        # 1d — Composite
        if not args.skip_composite:
            reference_processed = composite_clothing(
                args.reference, result["tryoff"], mask_path
            )
        else:
            reference_processed = result["tryoff"]
        
        # Upload composite for SCAIL-2
        reference_url = upload_to_tmp_public(reference_processed)
    else:
        reference_url = upload_to_tmp_public(args.reference)
    
    # ── Step 2: SCAIL-2 Animation ──
    print("\n── Uploading driving video ──")
    driving_url = upload_to_tmp_public(args.driving)
    
    output_path = run_scail2_fal(
        reference_url=reference_url,
        driving_video_url=driving_url,
        prompt=args.prompt,
        seed=args.seed,
        replacement_mode=True,
    )
    
    print(f"\n{'=' * 60}")
    print(f"✅ Pipeline complete!")
    print(f"   Output: {output_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
