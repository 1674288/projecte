# -*- coding: utf-8 -*-
"""
ImageFiles.py : gestiona el llistat d'arxius PNG de la col·lecció.

Estructura de dades: un set amb els paths relatius actuals. A cada
reload_fs() es compara amb la lectura anterior per saber què s'ha afegit
i què s'ha eliminat (diferència de conjunts).

Els paths són relatius a cfg.get_root() (la mateixa base que fan servir
la resta de classes per tornar a trobar l'arxiu al disc).
"""

import os
import cfg


def _relative_path(full: str) -> str:
    """Path relatiu a ROOT_DIR amb '/' com a separador (ex.: sub/img.png)."""
    rel = os.path.relpath(os.path.realpath(full), cfg.get_root())
    return rel.replace(os.sep, "/")


class ImageFiles:

    def __init__(self):
        self._files = set()    # paths relatius presents a l'última lectura
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
                    found.add(_relative_path(os.path.join(dirpath, name)))

        self._added = sorted(found - self._files)
        self._removed = sorted(self._files - found)
        self._files = found

    def files_added(self) -> list:
        """Paths relatius afegits des de l'última crida a reload_fs()."""
        return list(self._added)

    def files_removed(self) -> list:
        """Paths relatius eliminats des de l'última crida a reload_fs()."""
        return list(self._removed)

    def get_files(self) -> list:
        """Tots els paths relatius coneguts (mètode auxiliar)."""
        return sorted(self._files)

    def __str__(self) -> str:
        return "ImageFiles({} arxius)".format(len(self._files))
