#!/usr/bin/env bash
# setup.sh — video-seedance25-byok
#
# Este bundle NAO usa login nem credito do comfy.org. Ele fala DIRETO com a fal.ai
# usando a variavel de ambiente FAL_KEY.
#
# O que o script faz:
#   1. confere o servidor ComfyUI
#   2. instala os nos do bundle (symlink em custom_nodes/, nada e copiado)
#   3. confere a dependencia fal_client no venv do ComfyUI
#   4. confere a FAL_KEY (sem NUNCA imprimir o valor)
#   5. deixa os .json visiveis no painel Workflows
#
# Ele nao grava segredo em disco e nao instala nada via pip sem avisar.
set -euo pipefail

COMFY_HOST="${COMFY_HOST:-127.0.0.1}"
COMFY_PORT="${COMFY_PORT:-8188}"
COMFY_URL="http://${COMFY_HOST}:${COMFY_PORT}"
COMFY_ROOT="${COMFY_ROOT:-$HOME/ComfyUI}"
CUSTOM_NODES="${COMFY_ROOT}/custom_nodes"
WF_DIR="${COMFY_ROOT}/user/default/workflows"
SECRETS="${COMFY_ROOT}/secrets.env"
VENV_PY="${COMFY_ROOT}/venv/bin/python"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$(basename "$HERE")"
NODE_LINK="${CUSTOM_NODES}/seedance-byok"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$*"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$*"; }
die()  { printf '  \033[31mERRO\033[0m %s\n' "$*" >&2; exit 1; }

RESTART_NEEDED=0

# --------------------------------------------------------------------------- #
say "1/5 · servidor ComfyUI em ${COMFY_URL}"
command -v curl >/dev/null || die "curl nao encontrado."
if curl -fsS -m 5 "${COMFY_URL}/system_stats" -o /dev/null 2>/dev/null; then
  ok "servidor no ar"
  SERVER_UP=1
else
  warn "ComfyUI nao respondeu em ${COMFY_URL}."
  warn "Nao e impeditivo: da para instalar tudo agora e subir o servidor depois."
  SERVER_UP=0
fi

# --------------------------------------------------------------------------- #
say "2/5 · instalar os nos do bundle"
[ -d "$CUSTOM_NODES" ] || die "nao achei ${CUSTOM_NODES}. Ajuste COMFY_ROOT."

if [ -L "$NODE_LINK" ]; then
  CURRENT="$(readlink -f "$NODE_LINK" || true)"
  if [ "$CURRENT" = "${HERE}/comfy_nodes" ]; then
    ok "symlink ja aponta para este bundle"
  else
    warn "symlink existe mas aponta para ${CURRENT} — refazendo"
    rm -f "$NODE_LINK"
    ln -s "${HERE}/comfy_nodes" "$NODE_LINK"
    ok "symlink refeito"
    RESTART_NEEDED=1
  fi
elif [ -e "$NODE_LINK" ]; then
  die "${NODE_LINK} existe e NAO e um symlink. Remova ou renomeie antes de continuar."
else
  ln -s "${HERE}/comfy_nodes" "$NODE_LINK"
  ok "symlink criado: ${NODE_LINK/#$HOME/\~} -> ${HERE/#$HOME/\~}/comfy_nodes"
  RESTART_NEEDED=1
fi

# --------------------------------------------------------------------------- #
say "3/5 · dependencia fal_client"
if [ -x "$VENV_PY" ]; then
  PY="$VENV_PY"
  ok "usando o venv do ComfyUI"
else
  PY="$(command -v python3 || true)"
  [ -n "$PY" ] || die "python3 nao encontrado."
  warn "nao achei ${VENV_PY} — checando com o python3 do sistema (pode nao refletir o ComfyUI)"
fi

if "$PY" -c 'import fal_client' 2>/dev/null; then
  FAL_VER="$("$PY" -c 'import importlib.metadata as m; print(m.version("fal_client"))' 2>/dev/null || echo '?')"
  ok "fal_client presente (versao ${FAL_VER})"
else
  warn "fal_client AUSENTE — os nos deste bundle vao falhar ao rodar."
  cat <<EOF
      Instale no venv do ComfyUI:
        ${VENV_PY} -m pip install fal-client
      (ele ja vem junto se voce usa o custom node ComfyUI-fal-API)
EOF
fi

# --------------------------------------------------------------------------- #
say "4/5 · FAL_KEY"
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
  warn "FAL_KEY NAO encontrada — toda geracao vai falhar."
  cat <<'EOF'
      Como pegar (5 min):
        1. https://fal.ai            -> crie a conta
        2. https://fal.ai/dashboard/keys    -> Add key (o valor aparece UMA vez so)
        3. https://fal.ai/dashboard/billing -> adicione credito
      Como gravar (permissao 600, NUNCA commitar):
        printf 'FAL_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
        chmod 600 ~/ComfyUI/secrets.env
      Depois REINICIE o ComfyUI (o run.sh ja da source no secrets.env).
EOF
fi

if [ -f "$SECRETS" ]; then
  PERM="$(stat -c '%a' "$SECRETS" 2>/dev/null || echo '?')"
  if [ "$PERM" = "600" ]; then
    ok "secrets.env com permissao 600"
  else
    warn "secrets.env com permissao ${PERM} — recomendado: chmod 600 '${SECRETS}'"
  fi
fi

# --------------------------------------------------------------------------- #
say "5/5 · workflows visiveis no painel"
BUNDLES_DIR="$(dirname "$HERE")"
if [ ! -d "$WF_DIR" ]; then
  warn "nao achei ${WF_DIR} — abra os .json arrastando para a interface."
else
  FOUND="$(find -L "$WF_DIR" -path "*/${BUNDLE}/*.json" 2>/dev/null | head -1 || true)"
  if [ -n "$FOUND" ]; then
    ok "ja aparece em: ${FOUND/#$HOME/\~}"
  elif [ ! -e "${WF_DIR}/api" ]; then
    mkdir -p "$WF_DIR"
    ln -s "$BUNDLES_DIR" "${WF_DIR}/api"
    ok "symlink criado: ${WF_DIR/#$HOME/\~}/api -> ${BUNDLES_DIR/#$HOME/\~}"
  else
    warn "${WF_DIR}/api existe mas nao contem ${BUNDLE}/."
    printf '        rm -rf "%s/api" && ln -s "%s" "%s/api"\n' "$WF_DIR" "$BUNDLES_DIR" "$WF_DIR"
  fi
fi

# --------------------------------------------------------------------------- #
if [ "$RESTART_NEEDED" = "1" ] || [ "$SERVER_UP" = "0" ]; then
  say "REINICIE O COMFYUI"
  echo "  Os nos novos so aparecem depois de reiniciar o servidor."
  echo "    bash ~/ComfyUI/run.sh"
else
  # Servidor no ar e symlink ja existia: da para conferir de verdade.
  say "conferindo os nos no /object_info"
  OBJ="$(mktemp)"; trap 'rm -f "$OBJ"' EXIT
  if curl -fsS -m 120 "${COMFY_URL}/object_info" -o "$OBJ"; then
    MISSING=()
    for n in SeedanceBYOKReferenceToVideo SeedanceBYOKImageToVideo WanAnimateBYOK \
             VideoUpscaleBYOK SeedanceBYOKLastFrame SeedanceBYOKCheckKey; do
      if grep -q "\"$n\"" "$OBJ"; then ok "$n"; else MISSING+=("$n"); fi
    done
    if [ ${#MISSING[@]} -gt 0 ]; then
      warn "nos ausentes: ${MISSING[*]} — reinicie o ComfyUI (bash ~/ComfyUI/run.sh)"
    fi
  else
    warn "nao consegui ler o /object_info"
  fi
fi

cat <<EOF

  Pronto. Como comecar:
    1. No painel Workflows abra "${BUNDLE}_eu-foto__lugar-foto.json".
    2. Rode o no "Testar a chave" (custo zero) — ele diz se a FAL_KEY carregou
       e quais endpoints Seedance estao roteaveis agora.
    3. Suba a sua foto e a foto do lugar, ajuste o prompt, Run.

  Rascunhe barato: model = "Seedance 2.0 Mini", resolution = 480p, duration = 4.
  So depois suba para Seedance 2.0 + 1080p.

  Leia o README.md — em especial a secao "Uso responsavel" antes de usar o rosto
  de qualquer pessoa, inclusive o seu.

EOF
