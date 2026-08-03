# Organização do Grafo

Manter workflows grandes navegáveis e manteníveis.

## Groups (`Ctrl+G`)
Titule "01-Modelos", "02-Prompt", "03-Sampling"... — leitura rápida do fluxo.

## Reroute (rgthree)
Nós de desvio para evitar fios cruzados.

## Get/Set (KJNodes)
Variáveis globais — evita fios cruzando o grafo inteiro.
Útil para compartilhar seed, size, prompt entre ramos distantes.

## Bypass vs Mute
- **Bypass** (`Ctrl+B`): pula o nó, dados passam direto.
- **Mute** (`Ctrl+M`): mata o ramo inteiro.

## Primitives
Compartilhar seed/size/steps como nós constantes.

## Subgraphs (2026)
Encapsular uma seção como super-nó, aninhável, publicável (≥0.3.63 "Subgraph Blueprints").
Nós internos "Inputs"/"Outputs" expõem slots.
⚠️ Ainda há bugs (previews ao vivo, Power Lora Loader dentro de subgraph).

## Referências
- `docs/workflow-guide.md`
