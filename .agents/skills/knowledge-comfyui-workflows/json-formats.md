# Dois Formatos JSON (UI vs API)

Distinção crítica — usar o formato errado é o erro mais comum ao automatizar.

## UI/LiteGraph (salvo/carregado na tela)
- Tem `nodes[]`, `links[]`, `groups[]`, posições.
- **Não roda** direto no `/prompt`.

## API/prompt (Dev mode → "Save (API Format)")
- Dict plano `{id: {class_type, inputs}}`.
- Conexões = `[node_id, output_index]`.
- É o que vai no `POST /prompt`.

## Metadados em PNG/mp4
`VHS_VideoCombine save_metadata` permite arrastar o arquivo de volta ao ComfyUI —
mas redes sociais **removem** metadados. **Sempre salve o JSON** (export), com nome datado.

## Referências
- `docs/workflow-guide.md`
- Automação → [api-automation](api-automation.md)
