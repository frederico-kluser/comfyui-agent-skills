# Templates Oficiais — Base Known-Good

Vêm instalados com o ComfyUI (não precisa baixar):
`…/site-packages/comfyui_workflow_templates_media_{api,image,video,other,core}/templates/*.json`.

## Como achar o exemplo de um nó
```bash
grep -rl "<NodeType>" …/comfyui_workflow_templates*/templates/
```

## Templates úteis para API
- `api_google_nano_banana2_image_edit`
- `api_bytedance_seedream_5_0_lite_image_edit`
- `template_eric_seedance_5_subject_and_outfit_combine`
- `api_seedance2_0_r2v_real_human`
- `template_seedance2_0_viral_videos_character_swap`

## Por que usar templates
- Ordem correta dos `widgets_values` (schema V3).
- Fiação known-good dos slots AUTOGROW.
- Exemplos de asset verification (Seedance 2.0).

## Referências
- Schemas V3 → [schemas-v3](schemas-v3.md)
- Seedance real human → [seedance-real-human](seedance-real-human.md)
