# Ficha de Reprodução

Um workflow guarda nós/conexões/params, **não** os modelos/custom nodes/paths. Para reproduzir depois, registre:

## Campos obrigatórios
- **Fonte** do workflow (URL, autor, data).
- **Data** de criação/exportação.
- **Custom nodes** com versão.
- **Versão do ComfyUI** (nightly/stable, commit).
- **Modelos** com hash (sha256) e path.
- **Parâmetros**: seed, size, sampler, steps, cfg, scheduler.

## Nome do arquivo
`AAAAMMDD-proposito-vN.json`

## Metadados
PNG/mp4 com `save_metadata` permitem arrastar de volta ao ComfyUI, mas redes sociais removem. **Sempre salve o JSON separado.**

## Referências
- `docs/workflow-guide.md`
