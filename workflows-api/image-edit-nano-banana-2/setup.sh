#!/usr/bin/env bash
# setup.sh — image-edit-nano-banana-2
#
# Bundle 100% de nos CORE (partner nodes do comfy.org). Nao ha custom node para
# instalar e nao ha chave de API para gravar: a autenticacao e o LOGIN em
# platform.comfy.org, feito pela propria interface do ComfyUI.
#
# Este script so VERIFICA as pre-condicoes e deixa o .json visivel no painel.
set -euo pipefail

COMFY_HOST="${COMFY_HOST:-127.0.0.1}"
COMFY_PORT="${COMFY_PORT:-8188}"
COMFY_URL="http://${COMFY_HOST}:${COMFY_PORT}"
COMFY_ROOT="${COMFY_ROOT:-$HOME/ComfyUI}"
WF_DIR="${COMFY_ROOT}/user/default/workflows"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$(basename "$HERE")"
REQUIRED_NODES=(GeminiNanoBanana2 BatchImagesNode LoadImage SaveImage)

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mok\033[0m   %s\n' "$*"; }
warn() { printf '  \033[33mAVISO\033[0m %s\n' "$*"; }
die()  { printf '  \033[31mERRO\033[0m %s\n' "$*" >&2; exit 1; }

say "1/3 · servidor ComfyUI em ${COMFY_URL}"
command -v curl >/dev/null || die "curl nao encontrado."
if ! curl -fsS -m 5 "${COMFY_URL}/system_stats" -o /dev/null; then
  die "ComfyUI nao respondeu em ${COMFY_URL}. Suba o servidor e rode de novo (ou ajuste COMFY_HOST/COMFY_PORT)."
fi
ok "servidor no ar"

say "2/3 · os nos deste workflow existem?"
OBJ="$(mktemp)"; trap 'rm -f "$OBJ"' EXIT
curl -fsS -m 120 "${COMFY_URL}/object_info" -o "$OBJ" || die "falha ao ler /object_info"
MISSING=()
for n in "${REQUIRED_NODES[@]}"; do
  if command -v jq >/dev/null; then
    # python_module nao-nulo = o no esta REALMENTE carregado (o /object_info devolve
    # 200 com corpo vazio para nos que o Manager conhece mas nao estao instalados)
    if [ "$(jq -r --arg n "$n" '(.[$n].python_module // "null")' "$OBJ")" = "null" ]; then
      MISSING+=("$n"); else ok "$n"; fi
  else
    grep -q "\"$n\"" "$OBJ" && ok "$n (sem jq: checagem simples)" || MISSING+=("$n")
  fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
  die "nos ausentes: ${MISSING[*]}
  Esses nos sao CORE (comfy_api_nodes). Se faltam, o ComfyUI esta desatualizado:
    cd '${COMFY_ROOT}' && git pull && pip install -r requirements.txt   # e reinicie"
fi

say "3/3 · workflow visivel no painel"
BUNDLES_DIR="$(dirname "$HERE")"           # .../workflows-api
if [ ! -d "$WF_DIR" ]; then
  warn "nao achei ${WF_DIR} — abra o .json arrastando para a interface."
else
  # -L: seguir symlinks. Sem isso o find NAO entra em workflows/api quando ele
  # e um symlink para o repo — e o script acabaria copiando o .json para dentro
  # do proprio repo (poluindo workflows-api/ com um json solto na raiz).
  FOUND="$(find -L "$WF_DIR" -path "*/${BUNDLE}/*.json" 2>/dev/null | head -1 || true)"
  if [ -n "$FOUND" ]; then
    ok "ja aparece em: ${FOUND/#$HOME/\~}"
  elif [ ! -e "${WF_DIR}/api" ]; then
    ln -s "$BUNDLES_DIR" "${WF_DIR}/api"
    ok "symlink criado: ${WF_DIR/#$HOME/\~}/api -> ${BUNDLES_DIR/#$HOME/\~}"
    ok "todos os bundles de workflows-api/ passam a aparecer no painel"
  else
    warn "${WF_DIR}/api existe mas nao contem ${BUNDLE}/."
    warn "aponte-o para o repo (assim editar aqui reflete la na hora):"
    printf '        rm -rf "%s/api" && ln -s "%s" "%s/api"\n' "$WF_DIR" "$BUNDLES_DIR" "$WF_DIR"
  fi
fi

cat <<EOF

  Pronto. Falta so o que este script nao pode fazer por voce:

    1. Logar em platform.comfy.org pela interface do ComfyUI (menu do usuario).
       Os nos partner cobram em CREDITOS COMFY.ORG e NAO usam chave de API.
    2. Conferir o saldo de creditos.
    3. Abrir qualquer um dos 6 .json de "${BUNDLE}" no painel Workflows e ler o no "LEIA PRIMEIRO".

  Nenhum custom node foi instalado — este bundle nao precisa de nenhum.
  Nenhum segredo foi gravado em disco.

EOF
