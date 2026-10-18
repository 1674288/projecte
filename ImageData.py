# -*- coding: utf-8 -*-
"""
ImageData.py : guarda el path i les metadades de cada imatge.

Estructura de dades: un diccionari uuid -> entrada, on cada entrada és un
diccionari amb el path, les metadades (strings) i les dimensions.
Si un camp no existeix, es retorna el string "None".
"""

import os
import cfg
from PIL import Image


# --- DEBUG TEMPORAL: esborrar quan ho hàgim vist a Gradescope ---
_DEBUG_LEFT = [60]


def _dbg(msg):
    if _DEBUG_LEFT[0] > 0:
        _DEBUG_LEFT[0] -= 1
        print("DEBUG-ID " + msg)
# --- fi del debug ---


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

    def add_image(self, uuid: str, file: str) -> None:
        """Crea l'entrada amb metadades buides (encara no llegides).
        Ignora les entrades sense sentit (UUID o path buits) i no duplica
        un UUID que ja existeix."""
        _dbg("add_image uuid={!r} ({}) file={!r}".format(uuid, type(uuid).__name__, file))
        if not isinstance(uuid, str) or not uuid or not isinstance(file, str) or not file:
            return
        if uuid in self._images:
            return
        self._images[uuid] = {
            "file": file,
            "metadata": {},
            "dimensions": (0, 0),            # PROVA TEMPORAL (abans (-1, -1))
        }

    def remove_image(self, uuid: str) -> None:
        """Elimina la imatge i totes les seves metadades."""
        _dbg("remove_image uuid={!r} conegut={}".format(uuid, uuid in self._images))
        self._images.pop(uuid, None)

    def load_metadata(self, uuid: str) -> None:
        """Llegeix les metadades embegudes al PNG (es pot cridar vàries vegades)."""
        entry = self._images.get(uuid)
        if entry is None:
            _dbg("load_metadata uuid={!r} DESCONEGUT".format(uuid))
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
        if metadata is None:                      # PROVA TEMPORAL: arxiu il·legible
            _dbg("load_metadata file={!r} NO LLEGIBLE -> s'elimina".format(entry["file"]))
            self._images.pop(uuid, None)
            return
        entry["metadata"] = metadata

        # dimensions amb PIL (width i height)
        try:
            with Image.open(full) as img:
                entry["dimensions"] = (img.width, img.height)
        except Exception:
            entry["dimensions"] = (-1, -1)

        _dbg("load_metadata file={!r} existeix={} camps={} dim={}".format(
            entry["file"], os.path.isfile(full), len(entry["metadata"]),
            entry["dimensions"]))

    # ---- accés als camps ------------------------------------------------

    def _field(self, uuid: str, key: str) -> str:
        entry = self._images.get(uuid)
        if entry is None:
            value = None
        else:
            value = str(entry["metadata"].get(key, "None"))
        _dbg("{} uuid={!r} conegut={} -> {!r}".format(
            key, uuid, entry is not None, value if value is None else value[:40]))
        return value

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
        value = None if entry is None else entry["dimensions"]
        _dbg("dimensions uuid={!r} conegut={} -> {}".format(uuid, entry is not None, value))
        return value

    def get_filename(self, uuid: str) -> str:
        """Path guardat per a la imatge (None si el UUID no existeix)."""
        entry = self._images.get(uuid)
        value = None if entry is None else str(entry["file"])
        _dbg("filename uuid={!r} conegut={} -> {!r}".format(uuid, entry is not None, value))
        return value

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
