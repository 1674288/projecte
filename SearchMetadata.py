# -*- coding: utf-8 -*-
"""
SearchMetadata.py : cerca imatges per subcadena en les metadades.

Recorre els UUID d'ImageData i comprova cada camp amb str.find()
(case-sensitive). Retorna llistes simples d'UUID, no objectes Gallery.
"""

import cfg


class SearchMetadata:

    def __init__(self, image_data):
        self._data = image_data

    def _search(self, getter, sub) -> list:
        if sub is None:
            return []
        sub = str(sub)          # tolera valors no string (p.ex. un seed numèric)
        return [uuid for uuid in self._data.get_uuids()
                if getter(uuid).find(sub) != -1]

    def prompt(self, sub: str) -> list:
        return self._search(self._data.get_prompt, sub)

    def model(self, sub: str) -> list:
        return self._search(self._data.get_model, sub)

    def seed(self, sub: str) -> list:
        return self._search(self._data.get_seed, sub)

    def cfg_scale(self, sub: str) -> list:
        return self._search(self._data.get_cfg_scale, sub)

    def steps(self, sub: str) -> list:
        return self._search(self._data.get_steps, sub)

    def sampler(self, sub: str) -> list:
        return self._search(self._data.get_sampler, sub)

    def date(self, sub: str) -> list:
        return self._search(self._data.get_created_date, sub)

    def and_operator(self, list1: list, list2: list) -> list:
        """Intersecció: UUID presents a les dues llistes (no modifica les originals)."""
        list1 = list1 or []
        in_second = set(list2 or [])
        result = []
        seen = set()
        for uuid in list1:
            if uuid in in_second and uuid not in seen:
                seen.add(uuid)
                result.append(uuid)
        return result

    def or_operator(self, list1: list, list2: list) -> list:
        """Unió sense duplicats (no modifica les originals)."""
        result = []
        seen = set()
        for uuid in list(list1 or []) + list(list2 or []):
            if uuid not in seen:
                seen.add(uuid)
                result.append(uuid)
        return result

    def __str__(self) -> str:
        return "SearchMetadata({} imatges)".format(len(self._data))
