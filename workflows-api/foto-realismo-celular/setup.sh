#!/usr/bin/env bash
# setup.sh — foto-realismo-celular
#
# Bundle 100% LOCAL: nenhuma chamada de API, nenhuma chave, nenhum credito.
# Depende de dois custom nodes (WAS Node Suite e KJNodes). O script so VERIFICA
# as pre-condicoes e deixa o .json visivel no painel.
set -euo pipefail

COMFY_HOST="${COMFY_HOST:-127.0.0.1}"
COMFY_PORT="${COMFY_PORT:-8188}"
COMFY_URL="http://${COMFY_HOST}:${COMFY_PORT}"
COMFY_ROOT="${COMFY_ROOT:-$HOME/ComfyUI}"
WF_DIR="${COMFY_ROOT}/user/default/workflows"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$(basename "$HERE")"
REQUIRED_NODES=(
  ColorMatchV2
  ImageScaleToMaxDimension
  "Image Filter Adjustments"
  "Image Chromatic Aberration"
  ImageSharpen
  "Image Film Grain"
  ImageAddNoise
  "Image Save"
  LoadImage
)

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$*"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$*"; }
die()  { printf '  \033[31mERRO\033[0m %s\n' "$*" >&2; exit 1; }

say "1/3 · servidor ComfyUI em ${COMFY_URL}"
command -v curl >/dev/null || die "curl nao encontrado."
curl -fsS -m 5 "${COMFY_URL}/system_stats" -o /dev/null \
  || die "ComfyUI nao respondeu em ${COMFY_URL}. Suba o servidor e rode de novo."
ok "servidor no ar"

say "2/3 · os nos deste workflow existem?"
OBJ="$(mktemp)"; trap 'rm -f "$OBJ"' EXIT
curl -fsS -m 120 "${COMFY_URL}/object_info" -o "$OBJ" || die "falha ao ler /object_info"
MISSING=()
for n in "${REQUIRED_NODES[@]}"; do
  if command -v jq >/dev/null; then
    if [ "$(jq -r --arg n "$n" '(.[$n].python_module // "null")' "$OBJ")" = "null" ]; then
      MISSING+=("$n"); else ok "$n"; fi
  else
    grep -q "\"$n\"" "$OBJ" && ok "$n (sem jq: checagem simples)" || MISSING+=("$n")
  fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
  die "nos ausentes: ${MISSING[*]}
  Instale pelo ComfyUI Manager (e reinicie o servidor):
    - was-node-suite-comfyui   (Image Film Grain / Chromatic Aberration / Save)
    - ComfyUI-KJNodes          (ColorMatchV2)
  Os demais sao core: se faltarem, o ComfyUI esta desatualizado."
fi

say "3/3 · workflows visiveis no painel"
BUNDLES_DIR="$(dirname "$HERE")"
if [ ! -d "$WF_DIR" ]; then
  warn "nao achei ${WF_DIR} — abra o .json arrastando para a interface."
else
  FOUND="$(find -L "$WF_DIR" -path "*/${BUNDLE}/*.json" 2>/dev/null | head -1 || true)"
  if [ -n "$FOUND" ]; then
    ok "ja aparece em: ${FOUND/#$HOME/\~}"
  elif [ ! -e "${WF_DIR}/api" ]; then
    ln -s "$BUNDLES_DIR" "${WF_DIR}/api"
    ok "symlink criado: ${WF_DIR/#$HOME/\~}/api -> ${BUNDLES_DIR/#$HOME/\~}"
  else
    warn "${WF_DIR}/api existe mas nao contem ${BUNDLE}/."
    printf '        rm -rf "%s/api" && ln -s "%s" "%s/api"\n' "$WF_DIR" "$BUNDLES_DIR" "$WF_DIR"
  fi
fi

cat <<EOF

  Pronto. Para usar:
    1. Abra "${BUNDLE}_tratar-foto.json" no painel Workflows.
    2. Suba a imagem a tratar em FOTO (e, se quiser, uma foto sua de celular
       em REF DE COR -- senao ligue a mesma imagem nos dois slots).
    3. Run. Sai em output/celular/foto_*.jpg

  Custo ZERO: roda tudo na CPU local, nao chama modelo nenhum.
  Preset padrao ja aplicado. A tabela dos 4 presets esta na nota verde do grafo.

EOF
