"""Pacote de nos do bundle image-edit-pro-byok.

Instalacao: o `setup.sh` cria um symlink em ComfyUI/custom_nodes/ apontando para
esta pasta. Nada e copiado — editar aqui e reiniciar o servidor ja aplica.
"""

from .pro_image_edit import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
