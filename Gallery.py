# -*- coding: utf-8 -*-
"""
Gallery.py : gestiona una galeria d'imatges definida en un JSON.

Estructura de dades: un deque (collections) amb els UUID de les imatges en
ordre. Afegir al final i treure del principi o del final són O(1), sense
haver de recórrer ni desplaçar elements com passaria amb una llista.
"""

import json
import os
from collections import deque

import cfg


# --- DEBUG TEMPORAL: esborrar quan ho hàgim vist a Gradescope ---
_DEBUG_LEFT = [40]


def _dbg(msg):
    if _DEBUG_LEFT[0] > 0:
        _DEBUG_LEFT[0] -= 1
        print("DEBUG-GA " + msg)
# --- fi del debug ---


class Gallery:

    def __init__(self, image_id, image_viewer):
        self._image_id = image_id        # per passar de path a UUID
        self._viewer = image_viewer      # per visualitzar les imatges
        self.name = ""
        self.description = ""
        self.created_date = ""
        self._uuids = deque()

    def _find_uuid(self, path: str):
        """UUID de la imatge d'un path del JSON, o None si no és a la col·lecció.
        El path pot ser relatiu a ROOT_DIR (sub/img.png) o al seu directori
        pare, amb el nom de la carpeta al davant (generated_images/sub/img.png)."""
        path = path.replace("\\", "/")
        root = cfg.get_root()

        candidates = [os.path.normpath(path).replace(os.sep, "/")]
        full = os.path.join(os.path.dirname(root), path)
        candidates.append(
            os.path.relpath(os.path.realpath(full), root).replace(os.sep, "/"))

        for candidate in candidates:
            uuid = self._image_id.get_uuid(candidate)
            if uuid is not None:
                return uuid
        return None

    def load_file(self, file: str) -> None:
        """Llegeix el JSON de la galeria; ignora les imatges que no existeixen.
        Carregar substitueix sempre el contingut anterior, també si l'arxiu
        no es pot llegir (llavors la galeria queda buida)."""
        _dbg("load_file {!r} (abans: {} imatges)".format(file, len(self._uuids)))
        self.name = ""
        self.description = ""
        self.created_date = ""
        self._uuids = deque()

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            print("ERROR: no es pot llegir la galeria {}: {}".format(file, e))
            return

        if not isinstance(data, dict):
            print("ERROR: format de galeria incorrecte: {}".format(file))
            return

        self.name = data.get("gallery_name", "")
        self.description = data.get("description", "")
        self.created_date = data.get("created_date", "")

        images = data.get("images", [])
        if not isinstance(images, list):
            images = []

        for path in images:
            uuid = self._find_uuid(path) if isinstance(path, str) else None
            if uuid is None:
                print("AVÍS: imatge inexistent a la col·lecció, s'ignora: {}".format(path))
                continue
            self._uuids.append(uuid)
        _dbg("load_file -> {} imatges".format(len(self._uuids)))

    def show(self) -> None:
        """Visualitza totes les imatges de la galeria, en ordre."""
        for uuid in self._uuids:
            self._viewer.show_image(uuid, cfg.DISPLAY_MODE)

    def add_image_at_end(self, uuid: str) -> None:
        """Afegeix una imatge al final (s'accepten repeticions).
        Ignora UUID buits o que no són strings."""
        _dbg("add_image_at_end {!r} (abans: {})".format(uuid, len(self._uuids)))
        if not isinstance(uuid, str) or not uuid:
            return
        self._uuids.append(uuid)

    def remove_first_image(self) -> None:
        _dbg("remove_first_image (abans: {})".format(len(self._uuids)))
        if self._uuids:
            self._uuids.popleft()

    def remove_last_image(self) -> None:
        _dbg("remove_last_image (abans: {})".format(len(self._uuids)))
        if self._uuids:
            self._uuids.pop()

    # ---- mètodes auxiliars ----------------------------------------------

    def load_uuids(self, uuids: list) -> None:
        """Omple la galeria amb una llista d'UUID (p.ex. el resultat d'una cerca)."""
        self._uuids = deque(uuids)

    def get_uuids(self) -> list:
        return list(self._uuids)

    def __len__(self) -> int:
        return len(self._uuids)

    def __str__(self) -> str:
        return "Gallery('{}', {} imatges)".format(self.name, len(self._uuids))
