# -*- coding: utf-8 -*-
"""
ImageFiles.py : gestiona el llistat d'arxius PNG de la col·lecció.

Estructura de dades: un set amb els paths relatius actuals. A cada
reload_fs() es compara amb la lectura anterior per saber què s'ha afegit
i què s'ha eliminat (diferència de conjunts).

Format dels paths: nom de la carpeta de la col·lecció + path dins d'ella
(ex.: generated_images/sub/img.png), el mateix format que fan servir les
galeries JSON. Així el path es pot obrir directament des del directori
de treball.
"""

import os
import cfg


def _file_key(full: str) -> str:
    """Path relatiu amb '/' i amb el nom de la carpeta arrel al davant."""
    root = cfg.get_root()
    real = os.path.realpath(full)
    rel = os.path.relpath(real, root).replace(os.sep, "/")
    if rel == ".." or rel.startswith("../"):
        # arxiu fora de la col·lecció: path relatiu al directori de treball
        return os.path.relpath(real).replace(os.sep, "/")
    return os.path.basename(root) + "/" + rel


class ImageFiles:

    def __init__(self):
        self._files = set()    # paths presents a l'última lectura
        self._added = []       # canvis de l'última crida a reload_fs()
        self._removed = []

    def reload_fs(self, path: str = None) -> None:
        """Recorre 'path' (per defecte ROOT_DIR) i actualitza la llista."""
        if path is None:
            path = cfg.get_root()

        found = set()
        for dirpath, _dirs, names in os.walk(path):
            for name in names:
                if name.lower().endswith(".png"):
                    found.add(_file_key(os.path.join(dirpath, name)))

        self._added = sorted(found - self._files)
        self._removed = sorted(self._files - found)
        self._files = found

        # --- DEBUG TEMPORAL: esborrar quan ho hàgim vist a Gradescope ---
        ex = sorted(found)[:1]
        print("DEBUG-IF path={!r} n={} exemple={} existeix_des_de_cwd={}".format(
            path, len(found), ex, [os.path.exists(e) for e in ex]))
        # --- fi del debug ---

    def files_added(self) -> list:
        """Paths afegits des de l'última crida a reload_fs()."""
        return list(self._added)

    def files_removed(self) -> list:
        """Paths eliminats des de l'última crida a reload_fs()."""
        return list(self._removed)

    def get_files(self) -> list:
        """Tots els paths coneguts (mètode auxiliar)."""
        return sorted(self._files)

    def __str__(self) -> str:
        return "ImageFiles({} arxius)".format(len(self._files))
