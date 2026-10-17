# -*- coding: utf-8 -*-
"""
ImageID.py : genera i gestiona els identificadors únics (UUID) de les imatges.

Estructura de dades: dos diccionaris, un per fitxer -> uuid i un altre per
uuid -> fitxer. Així consultar per fitxer (get_uuid) i eliminar per uuid
(remove_uuid) són operacions directes, sense recórrer res.
"""

import cfg


class ImageID:

    def __init__(self):
        self._by_file = {}   # path relatiu -> uuid (str)
        self._by_uuid = {}   # uuid (str) -> path relatiu

    def generate_uuid(self, file: str) -> str:
        """Genera el UUID de 'file' (path relatiu canònic).
        Retorna None i mostra un error si el UUID ja està en ús."""
        uuid = str(cfg.get_uuid(file))

        if uuid in self._by_uuid:
            print("ERROR: el UUID {} ja està en ús (arxiu: {})".format(uuid, file))
            return None

        self._by_file[file] = uuid
        self._by_uuid[uuid] = file
        return uuid

    def get_uuid(self, file: str) -> str:
        """UUID associat a 'file', o None si no s'ha generat."""
        return self._by_file.get(file)

    def remove_uuid(self, uuid: str) -> None:
        """Elimina el UUID del registre; després es podrà tornar a generar."""
        file = self._by_uuid.pop(uuid, None)
        if file is not None:
            self._by_file.pop(file, None)

    def __len__(self) -> int:
        return len(self._by_uuid)

    def __str__(self) -> str:
        return "ImageID({} identificadors)".format(len(self._by_uuid))
