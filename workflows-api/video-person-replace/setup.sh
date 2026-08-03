#!/usr/bin/env bash
# setup.sh — video-person-replace
#
# Este bundle NAO roda por credito comfy.org: ele usa a fal.ai, que exige a
# variavel de ambiente FAL_KEY. O script VERIFICA as pre-condicoes e deixa os
# .json visiveis no painel. Ele NAO grava segredo em disco e NAO imprime a chave.
set -euo pipefail

COMFY_HOST="${COMFY_HOST:-127.0.0.1}"
COMFY_PORT="${COMFY_PORT:-8188}"
COMFY_URL="http://${COMFY_HOST}:${COMFY_PORT}"
COMFY_ROOT="${COMFY_ROOT:-$HOME/ComfyUI}"
WF_DIR="${COMFY_ROOT}/user/default/workflows"
SECRETS="${COMFY_ROOT}/secrets.env"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$(basename "$HERE")"
REQUIRED_NODES=(
  Wan2214b_animate_replace_character_fal
  PixverseSwapNode_fal
  LoadVideoURL
  VHS_VideoInfoLoaded
  GetVideoComponents
  CreateVideo
  SaveVideo
  LoadImage
  LoadVideo
)

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$*"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$*"; }
die()  { printf '  \033[31mERRO\033[0m %s\n' "$*" >&2; exit 1; }

say "1/4 · servidor ComfyUI em ${COMFY_URL}"
command -v curl >/dev/null || die "curl nao encontrado."
curl -fsS -m 5 "${COMFY_URL}/system_stats" -o /dev/null \
  || die "ComfyUI nao respondeu em ${COMFY_URL}. Suba o servidor e rode de novo."
ok "servidor no ar"

say "2/4 · os nos deste workflow existem?"
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
    - ComfyUI-fal-API            (nos *_fal e o Load Video (URL))
    - ComfyUI-VideoHelperSuite   (VHS_VideoInfoLoaded)
  Os demais sao core: se faltarem, o ComfyUI esta desatualizado."
fi

say "3/4 · FAL_KEY"
# Le do ambiente OU do secrets.env, sem nunca imprimir o valor.
KEY_SRC=""
if [ -n "${FAL_KEY:-}" ]; then
  KEY_SRC="ambiente"
elif [ -f "$SECRETS" ] && grep -qE '^[[:space:]]*(export[[:space:]]+)?FAL_KEY=.+' "$SECRETS"; then
  KEY_SRC="${SECRETS/#$HOME/\~}"
fi
if [ -n "$KEY_SRC" ]; then
  ok "FAL_KEY presente (origem: ${KEY_SRC})"
  warn "presenca != validade. Se der 401, a chave expirou ou acabou o credito."
else
  warn "FAL_KEY NAO encontrada — os nos *_fal vao falhar com 401."
  cat <<'EOF'
      Como pegar (5 min):
        1. https://fal.ai  -> crie a conta
        2. https://fal.ai/dashboard/keys -> Add key (o valor so aparece UMA vez)
        3. https://fal.ai/dashboard/billing -> adicione credito
      Como gravar (permissao 600, NUNCA commitar):
        printf 'FAL_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
        chmod 600 ~/ComfyUI/secrets.env
      Depois REINICIE o ComfyUI (o run.sh ja da source no secrets.env).
EOF
fi
if [ -f "$SECRETS" ]; then
  PERM="$(stat -c '%a' "$SECRETS" 2>/dev/null || echo '?')"
  [ "$PERM" = "600" ] && ok "secrets.env com permissao 600" \
    || warn "secrets.env com permissao ${PERM} — recomendado: chmod 600 '${SECRETS}'"
fi

say "4/4 · workflows visiveis no painel"
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

  Pronto. Para gerar:
    1. Abra "${BUNDLE}_wan-animate.json" no painel Workflows.
    2. Suba a SUA FOTO (corpo inteiro) e o VIDEO ORIGINAL (comece com 3-6 s).
    3. Run. Sai em output/video/replace_*.mp4 com audio e fps originais.

  Resolucao ja vem em 480p (o minimo do modelo) de proposito: mais barato
  e ja parece video de celular. Suba para 720p so na versao final.

EOF
