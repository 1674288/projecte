# -*- coding: utf-8 -*-
"""
ImageData.py : guarda el path i les metadades de cada imatge.

Estructura de dades: un diccionari uuid -> entrada, on cada entrada és un
diccionari amb el path, les metadades (strings) i les dimensions.
Si un camp de metadades no existeix, es retorna el string "None".
Si el UUID no existeix, els getters retornen None.
"""

import os
import cfg
from PIL import Image


class ImageData:

    def __init__(self):
        self._images = {}   # uuid -> {"file", "metadata", "dimensions"}

    def _resolve(self, file) -> str:
        """Path real de l'arxiu al disc. El path guardat pot ser absolut,
        relatiu al directori de treball (generated_images/x.png) o relatiu
        a ROOT_DIR (x.png)."""
        file = str(file)
        root = cfg.get_root()
        candidates = [file,
                      os.path.join(root, file),
                      os.path.join(os.path.dirname(root), file)]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        return candidates[1]

    def _read_dimensions(self, file) -> tuple:
        """(width, height) de la imatge, o (-1, -1) si no es pot llegir."""
        try:
            with Image.open(self._resolve(file)) as img:
                return (img.width, img.height)
        except Exception:
            return (-1, -1)

    def add_image(self, uuid: str, file: str) -> None:
        """Crea l'entrada amb metadades buides (encara no llegides).
        Ignora les entrades sense sentit (UUID o path buits) i no duplica
        un UUID que ja existeix."""
        if not isinstance(uuid, str) or not uuid or not isinstance(file, str) or not file:
            return
        if uuid in self._images:
            return
        self._images[uuid] = {
            "file": file,
            "metadata": {},
            "dimensions": None,      # es llegeixen quan es demanen
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

        full = self._resolve(entry["file"])

        # metadades (text chunks) amb la funció de cfg; si no hi és, amb PIL
        try:
            metadata = cfg.read_png_metadata(full)
        except AttributeError:
            try:
                with Image.open(full) as img:
                    metadata = dict(getattr(img, "text", {}))
            except Exception:
                metadata = None
        entry["metadata"] = metadata if metadata else {}

        entry["dimensions"] = self._read_dimensions(entry["file"])

    # ---- accés als camps ------------------------------------------------

    def _field(self, uuid: str, key: str) -> str:
        entry = self._images.get(uuid)
        if entry is None:
            return None
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
        """(width, height) de la imatge; None si el UUID no existeix."""
        entry = self._images.get(uuid)
        if entry is None:
            return None
        if entry["dimensions"] is None:
            entry["dimensions"] = self._read_dimensions(entry["file"])
        return entry["dimensions"]

    def get_filename(self, uuid: str) -> str:
        """Path guardat per a la imatge (None si el UUID no existeix)."""
        entry = self._images.get(uuid)
        return None if entry is None else str(entry["file"])

    # ---- mètodes auxiliars per a les altres classes ---------------------

    def get_file(self, uuid: str) -> str:
        """Path guardat de la imatge, o None si no existeix."""
        entry = self._images.get(uuid)
        return None if entry is None else entry["file"]

    def get_uuids(self) -> list:
        """Tots els UUID de la col·lecció (ordre d'inserció)."""
        return list(self._images.keys())

    def __len__(self) -> int:
        return len(self._images)

    def __str__(self) -> str:
        return "ImageData({} imatges)".format(len(self._images))
