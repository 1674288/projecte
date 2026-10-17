# -*- coding: utf-8 -*-
"""
ImageData.py : guarda el path i les metadades de cada imatge.

Estructura de dades: un diccionari uuid -> entrada, on cada entrada és un
diccionari amb el path, les metadades (strings) i les dimensions.
Si un camp no existeix, es retorna el string "None".
"""

import os
import cfg


class ImageData:

    def __init__(self):
        self._images = {}   # uuid -> {"file", "metadata", "dimensions"}

    def add_image(self, uuid: str, file: str) -> None:
        """Crea l'entrada amb metadades buides (encara no llegides)."""
        self._images[uuid] = {
            "file": file,
            "metadata": {},
            "dimensions": (-1, -1),
        }

    def remove_image(self, uuid: str) -> None:
        """Elimina la imatge i totes les seves metadades."""
        self._images.pop(uuid, None)

    def load_metadata(self, uuid: str) -> None:
        """Llegeix les metadades embegudes al PNG (es pot cridar vàries vegades)."""
        entry = self._images.get(uuid)
        if entry is None:
            print("ERROR: UUID desconegut: {}".format(uuid))
            return

        full = os.path.join(cfg.get_root(), entry["file"])

        metadata = cfg.read_png_metadata(full)
        entry["metadata"] = metadata if metadata else {}

        width, height = cfg.get_png_dimensions(full)
        if width is None or height is None:
            entry["dimensions"] = (-1, -1)
        else:
            entry["dimensions"] = (width, height)

    # ---- accés als camps ------------------------------------------------

    def _field(self, uuid: str, key: str) -> str:
        entry = self._images.get(uuid)
        if entry is None:
            return "None"
        return str(entry["metadata"].get(key, "None"))

    def get_prompt(self, uuid: str) -> str:
        return self._field(uuid, "Prompt")

    def get_model(self, uuid: str) -> str:
        return self._field(uuid, "Model")

    def get_seed(self, uuid: str) -> str:
        return self._field(uuid, "Seed")

    def get_cfg_scale(self, uuid: str) -> str:
        return self._field(uuid, "CFG_Scale")

    def get_steps(self, uuid: str) -> str:
        return self._field(uuid, "Steps")

    def get_sampler(self, uuid: str) -> str:
        return self._field(uuid, "Sampler")

    def get_generated(self, uuid: str) -> str:
        return self._field(uuid, "Generated")

    def get_created_date(self, uuid: str) -> str:
        return self._field(uuid, "Created_Date")

    def get_dimensions(self, uuid: str) -> tuple:
        entry = self._images.get(uuid)
        if entry is None:
            return (-1, -1)
        return entry["dimensions"]

    # ---- mètodes auxiliars per a les altres classes ---------------------

    def get_file(self, uuid: str) -> str:
        """Path relatiu de la imatge, o None si no existeix."""
        entry = self._images.get(uuid)
        return None if entry is None else entry["file"]

    def get_uuids(self) -> list:
        """Tots els UUID de la col·lecció (ordre d'inserció)."""
        return list(self._images.keys())

    def get_filename(self, uuid: str) -> str:
        """Path guardat per a la imatge, com a string ("None" si no existeix)."""
        entry = self._images.get(uuid)
        return "None" if entry is None else str(entry["file"])

    def __len__(self) -> int:
        return len(self._images)

    def __str__(self) -> str:
        return "ImageData({} imatges)".format(len(self._images))