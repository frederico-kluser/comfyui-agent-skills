#!/usr/bin/env bash
# setup.sh — video-minimax-h3-byok
#
# Bundle 100% ONLINE: nenhum modelo roda nesta maquina. Ele fala direto com a
# API v2 da MiniMax usando a variavel de ambiente MINIMAX_API_KEY.
#
# O que o script faz:
#   1. confere o servidor ComfyUI
#   2. instala os nos do bundle (symlink em custom_nodes/, nada e copiado)
#   3. confere a MINIMAX_API_KEY (sem NUNCA imprimir o valor) e testa o alcance da API
#   4. deixa os .json visiveis no painel Workflows
#
# Ele nao grava segredo em disco e nao instala nada via pip.
set -euo pipefail

COMFY_HOST="${COMFY_HOST:-127.0.0.1}"
COMFY_PORT="${COMFY_PORT:-8188}"
COMFY_URL="http://${COMFY_HOST}:${COMFY_PORT}"
COMFY_ROOT="${COMFY_ROOT:-$HOME/ComfyUI}"
CUSTOM_NODES="${COMFY_ROOT}/custom_nodes"
WF_DIR="${COMFY_ROOT}/user/default/workflows"
SECRETS="${COMFY_ROOT}/secrets.env"
API_HOST="${MINIMAX_API_HOST:-https://api.minimax.io}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$(basename "$HERE")"
NODE_LINK="${CUSTOM_NODES}/minimax-h3-byok"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$*"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$*"; }
die()  { printf '  \033[31mERRO\033[0m %s\n' "$*" >&2; exit 1; }

RESTART_NEEDED=0

# --------------------------------------------------------------------------- #
say "1/4 · servidor ComfyUI em ${COMFY_URL}"
command -v curl >/dev/null || die "curl nao encontrado."
if curl -fsS -m 5 "${COMFY_URL}/system_stats" -o /dev/null 2>/dev/null; then
  ok "servidor no ar"; SERVER_UP=1
else
  warn "ComfyUI nao respondeu. Nao e impeditivo: instale agora e suba o servidor depois."
  SERVER_UP=0
fi

# --------------------------------------------------------------------------- #
say "2/4 · instalar os nos do bundle"
[ -d "$CUSTOM_NODES" ] || die "nao achei ${CUSTOM_NODES}. Ajuste COMFY_ROOT."

if [ -L "$NODE_LINK" ]; then
  CURRENT="$(readlink -f "$NODE_LINK" || true)"
  if [ "$CURRENT" = "${HERE}/comfy_nodes" ]; then
    ok "symlink ja aponta para este bundle"
  else
    warn "symlink aponta para ${CURRENT} — refazendo"
    rm -f "$NODE_LINK"; ln -s "${HERE}/comfy_nodes" "$NODE_LINK"
    ok "symlink refeito"; RESTART_NEEDED=1
  fi
elif [ -e "$NODE_LINK" ]; then
  die "${NODE_LINK} existe e NAO e um symlink. Remova ou renomeie antes."
else
  ln -s "${HERE}/comfy_nodes" "$NODE_LINK"
  ok "symlink criado: ${NODE_LINK/#$HOME/\~}"
  RESTART_NEEDED=1
fi

# --------------------------------------------------------------------------- #
say "3/4 · MINIMAX_API_KEY"
KEY_VALUE=""
KEY_SRC=""
if [ -n "${MINIMAX_API_KEY:-}" ]; then
  KEY_VALUE="${MINIMAX_API_KEY}"; KEY_SRC="ambiente"
elif [ -f "$SECRETS" ] && grep -qE '^[[:space:]]*(export[[:space:]]+)?MINIMAX_API_KEY=.+' "$SECRETS"; then
  KEY_VALUE="$(grep -E '^[[:space:]]*(export[[:space:]]+)?MINIMAX_API_KEY=' "$SECRETS" \
    | tail -1 | sed -E 's/^[[:space:]]*(export[[:space:]]+)?MINIMAX_API_KEY=//' | tr -d "\"'" )"
  KEY_SRC="${SECRETS/#$HOME/\~}"
fi

if [ -n "$KEY_SRC" ]; then
  ok "MINIMAX_API_KEY presente (origem: ${KEY_SRC})"
  # Testa a credencial de verdade: consulta uma task inexistente.
  CODE="$(curl -s -o /dev/null -m 30 -w '%{http_code}' \
    "${API_HOST}/v2/query/video_generation/0" \
    -H "Authorization: Bearer ${KEY_VALUE}" || echo 000)"
  case "$CODE" in
    401) warn "a API respondeu 401 — a chave e invalida ou expirou." ;;
    000) warn "nao consegui falar com ${API_HOST} (rede/proxy?)." ;;
    *)   ok "credencial aceita pela API (consulta devolveu HTTP ${CODE}, nao 401)"
         warn "isto nao confirma SALDO. Sem credito a geracao falha com 'insufficient_balance_error'." ;;
  esac
else
  warn "MINIMAX_API_KEY NAO encontrada — toda geracao vai falhar."
  cat <<'EOF'
      Como pegar (5 min, tudo online):
        1. https://platform.minimax.io  -> Sign up (e-mail ou Google)
        2. Console (canto superior direito)
        3. Menu lateral: API Keys  ->  Create new API key  ->  copie AGORA
           (o valor aparece UMA vez so)
        4. Billing / Recharge -> adicione credito
      Como gravar (permissao 600, NUNCA commitar):
        printf 'MINIMAX_API_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
        chmod 600 ~/ComfyUI/secrets.env
      Depois REINICIE o ComfyUI (o run.sh ja da source no secrets.env).
EOF
fi

if [ -f "$SECRETS" ]; then
  PERM="$(stat -c '%a' "$SECRETS" 2>/dev/null || echo '?')"
  [ "$PERM" = "600" ] && ok "secrets.env com permissao 600" \
    || warn "secrets.env com permissao ${PERM} — recomendado: chmod 600 '${SECRETS}'"
fi

# --------------------------------------------------------------------------- #
say "4/4 · workflows visiveis no painel"
BUNDLES_DIR="$(dirname "$HERE")"
if [ ! -d "$WF_DIR" ]; then
  warn "nao achei ${WF_DIR} — abra os .json arrastando para a interface."
else
  FOUND="$(find -L "$WF_DIR" -path "*/${BUNDLE}/*.json" 2>/dev/null | head -1 || true)"
  if [ -n "$FOUND" ]; then
    ok "ja aparece em: ${FOUND/#$HOME/\~}"
  elif [ ! -e "${WF_DIR}/api" ]; then
    mkdir -p "$WF_DIR"; ln -s "$BUNDLES_DIR" "${WF_DIR}/api"
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
  say "conferindo os nos no /object_info"
  OBJ="$(mktemp)"; trap 'rm -f "$OBJ"' EXIT
  if curl -fsS -m 120 "${COMFY_URL}/object_info" -o "$OBJ"; then
    MISSING=()
    for n in MiniMaxH3BYOKReferenceToVideo MiniMaxH3BYOKImageToVideo \
             MiniMaxH3BYOKTextToVideo MiniMaxH3BYOKLastFrame MiniMaxH3BYOKCheckKey; do
      if grep -q "\"$n\"" "$OBJ"; then ok "$n"; else MISSING+=("$n"); fi
    done
    [ ${#MISSING[@]} -gt 0 ] && warn "nos ausentes: ${MISSING[*]} — reinicie o ComfyUI"
  else
    warn "nao consegui ler o /object_info"
  fi
fi

cat <<EOF

  Pronto. Como comecar:
    1. No painel Workflows abra "${BUNDLE}_so-texto.json" — e a chamada mais barata.
    2. Rode o no "Testar a chave" (custo zero).
    3. Run. Se sair video, a rota inteira funciona; ai va para os workflows com foto.

  Rascunhe em 768P com duration = 4. So depois suba para 2K.

  Leia o README.md — em especial "Como pegar a chave" e "Uso responsavel".

EOF
