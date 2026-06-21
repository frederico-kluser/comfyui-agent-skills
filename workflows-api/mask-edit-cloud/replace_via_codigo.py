#!/usr/bin/env python3
"""Replace 'via código' (PIL): cola a região editada de volta na imagem original usando a máscara.
Uso: python3 replace_via_codigo.py original.png editada.png mascara.png saida.png [blur]
- original: imagem base (fica intacta fora da máscara)
- editada : imagem com a região nova (mesmo tamanho do original)
- mascara : tons de cinza; BRANCO = usa a editada, PRETO = mantém o original
- blur    : (opcional) suaviza a borda da máscara em N px (default 4)
"""
import sys
from PIL import Image, ImageFilter

def main():
    if len(sys.argv) < 5:
        print(__doc__); sys.exit(1)
    orig = Image.open(sys.argv[1]).convert("RGB")
    edit = Image.open(sys.argv[2]).convert("RGB").resize(orig.size)
    mask = Image.open(sys.argv[3]).convert("L").resize(orig.size)
    out_path = sys.argv[4]
    blur = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))  # costura sem emenda
    result = orig.copy()
    result.paste(edit, (0, 0), mask)   # cola 'edit' onde a máscara é branca
    result.save(out_path)
    print("salvo:", out_path)

if __name__ == "__main__":
    main()
