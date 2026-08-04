"""Pacote de nos do bundle video-minimax-h3-byok.

Instalacao: o `setup.sh` cria um symlink em ComfyUI/custom_nodes/ apontando para
esta pasta. Nada e copiado — editar aqui e reiniciar o servidor ja aplica.
"""

from .minimax_byok import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
