#!/usr/bin/env bash
# setup.sh — image-edit-pro-byok
#
# Bundle 100% por API. Nenhum modelo roda nesta maquina — nem no setup, nem no uso.
# Credencial unica: FAL_KEY.
#
#   1. confere o servidor ComfyUI
#   2. instala os nos do bundle (symlink em custom_nodes/, nada e copiado)
#   3. confere a dependencia fal_client
#   4. confere a FAL_KEY (sem NUNCA imprimir o valor)
#   5. deixa os .json visiveis no painel Workflows
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
NODE_LINK="${CUSTOM_NODES}/pro-image-edit-byok"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$*"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$*"; }
die()  { printf '  \033[31mERRO\033[0m %s\n' "$*" >&2; exit 1; }

RESTART_NEEDED=0

say "1/5 · servidor ComfyUI em ${COMFY_URL}"
command -v curl >/dev/null || die "curl nao encontrado."
if curl -fsS -m 5 "${COMFY_URL}/system_stats" -o /dev/null 2>/dev/null; then
  ok "servidor no ar"; SERVER_UP=1
else
  warn "ComfyUI nao respondeu. Da para instalar agora e subir depois."; SERVER_UP=0
fi

say "2/5 · instalar os nos do bundle"
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
  ok "symlink criado: ${NODE_LINK/#$HOME/\~}"; RESTART_NEEDED=1
fi

say "3/5 · dependencia fal_client"
if [ -x "$VENV_PY" ]; then PY="$VENV_PY"; ok "usando o venv do ComfyUI"
else PY="$(command -v python3 || true)"; [ -n "$PY" ] || die "python3 nao encontrado."
     warn "nao achei ${VENV_PY} — checando com o python3 do sistema"; fi
if "$PY" -c 'import fal_client' 2>/dev/null; then
  ok "fal_client presente"
else
  warn "fal_client AUSENTE — os nos vao falhar ao rodar."
  echo "      ${VENV_PY} -m pip install fal-client"
fi

say "4/5 · FAL_KEY"
KEY_SRC=""
if [ -n "${FAL_KEY:-}" ]; then KEY_SRC="ambiente"
elif [ -f "$SECRETS" ] && grep -qE '^[[:space:]]*(export[[:space:]]+)?FAL_KEY=.+' "$SECRETS"; then
  KEY_SRC="${SECRETS/#$HOME/\~}"; fi
if [ -n "$KEY_SRC" ]; then
  ok "FAL_KEY presente (origem: ${KEY_SRC})"
  warn "presenca != saldo. Sem credito na fal a geracao falha."
else
  warn "FAL_KEY NAO encontrada — toda geracao vai falhar."
  cat <<'EOF'
      Como pegar (5 min, tudo online):
        1. https://fal.ai                   -> crie a conta
        2. https://fal.ai/dashboard/keys    -> Add key (o valor aparece UMA vez so)
        3. https://fal.ai/dashboard/billing -> adicione credito
      Como gravar (permissao 600, NUNCA commitar):
        printf 'FAL_KEY=%s\n' "SUA_CHAVE" >> ~/ComfyUI/secrets.env
        chmod 600 ~/ComfyUI/secrets.env
      Depois REINICIE o ComfyUI.
EOF
fi
if [ -f "$SECRETS" ]; then
  PERM="$(stat -c '%a' "$SECRETS" 2>/dev/null || echo '?')"
  [ "$PERM" = "600" ] && ok "secrets.env com permissao 600" \
    || warn "secrets.env com permissao ${PERM} — recomendado: chmod 600 '${SECRETS}'"
fi

say "5/5 · workflows visiveis no painel"
BUNDLES_DIR="$(dirname "$HERE")"
if [ ! -d "$WF_DIR" ]; then
  warn "nao achei ${WF_DIR} — abra os .json arrastando para a interface."
else
  FOUND="$(find -L "$WF_DIR" -path "*/${BUNDLE}/*.json" 2>/dev/null | head -1 || true)"
  if [ -n "$FOUND" ]; then ok "ja aparece em: ${FOUND/#$HOME/\~}"
  elif [ ! -e "${WF_DIR}/api" ]; then
    mkdir -p "$WF_DIR"; ln -s "$BUNDLES_DIR" "${WF_DIR}/api"
    ok "symlink criado: ${WF_DIR/#$HOME/\~}/api"
  else
    warn "${WF_DIR}/api existe mas nao contem ${BUNDLE}/."
    printf '        rm -rf "%s/api" && ln -s "%s" "%s/api"\n' "$WF_DIR" "$BUNDLES_DIR" "$WF_DIR"
  fi
fi

if [ "$RESTART_NEEDED" = "1" ] || [ "$SERVER_UP" = "0" ]; then
  say "REINICIE O COMFYUI"
  echo "  Os nos novos so aparecem depois de reiniciar."
  echo "    bash ~/ComfyUI/run.sh"
else
  say "conferindo os nos no /object_info"
  OBJ="$(mktemp)"; trap 'rm -f "$OBJ"' EXIT
  if curl -fsS -m 120 "${COMFY_URL}/object_info" -o "$OBJ"; then
    for n in ProImageEditBYOK ProFaceRestoreBYOK ProImageEditCheckKey; do
      grep -q "\"$n\"" "$OBJ" && ok "$n" || warn "$n ausente — reinicie o ComfyUI"
    done
  else
    warn "nao consegui ler o /object_info"
  fi
fi

cat <<EOF

  Pronto. A ORDEM IMPORTA:

    1. Abra "${BUNDLE}_00_teste-de-identidade.json"
    2. Rode o no "Testar a chave" (custo zero)
    3. Suba a foto BASE + DUAS fotos suas (angulos diferentes, ROSTO GRANDE no quadro)
    4. Run -> saem 3 arquivos em output/edit/, um por motor
    5. Compare SO O ROSTO e adote o vencedor no dropdown 'model' dos outros workflows

  Sem esse teste voce fica adivinhando qual modelo erra menos o SEU rosto.

  Leia o README.md — a secao "Por que as fotos anteriores erravam o rosto" explica
  o que mudou e por que.

EOF
