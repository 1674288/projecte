# -*- coding: utf-8 -*-
"""
p1_main.py : ** OPTIONAL ** Si heu fet un main vostre, poseu aquí el codi.
                            Aquest arxiu no s'avalua automàticament.

Aquí podeu posar el vostre codi de proves per testejar les funcionalitats
implementades.

Exemples d'ús:
    - Carregar la col·lecció d'imatges
    - Generar UUID per a totes les imatges
    - Llegir metadades d'algunes imatges
    - Visualitzar imatges
    - Carregar i mostrar galeries
    - Fer cerques i crear galeries a partir dels resultats
"""

# -*- coding: utf-8 -*-
"""
p1_main.py : codi de proves de la primera entrega (no s'avalua).
Recorre les 7 funcionalitats: llistat, UUID, metadades, visualització,
galeries JSON, cerques i galeries dinàmiques.
"""

import json
import os
import tempfile

import cfg
from ImageFiles import ImageFiles
from ImageID import ImageID
from ImageData import ImageData
from ImageViewer import ImageViewer
from Gallery import Gallery
from SearchMetadata import SearchMetadata


def main():
    cfg.DISPLAY_MODE = 0   # a les proves només imprimim metadades (no obre cap finestra)

    # Func1: llistat d'imatges
    files = ImageFiles()
    files.reload_fs(cfg.ROOT_DIR)
    added = files.files_added()
    print("Imatges trobades: {}".format(len(added)))
    files.reload_fs(cfg.ROOT_DIR)
    print("Segona lectura -> afegides: {}, eliminades: {}\n".format(
        len(files.files_added()), len(files.files_removed())))

    # Func2 i Func3: UUID i metadades
    ids = ImageID()
    data = ImageData()
    for f in added:
        uuid = ids.generate_uuid(f)
        if uuid is None:
            continue
        data.add_image(uuid, f)
        data.load_metadata(uuid)

    # Func4: visualització (mode 0 = només metadades)
    viewer = ImageViewer(data)
    for uuid in data.get_uuids()[:2]:
        viewer.show_image(uuid, 0)
        print()

    # Func6: cerques
    search = SearchMetadata(data)
    cats = search.prompt("cat")
    sd = search.model("SD")
    print("prompt 'cat': {}  |  model 'SD': {}".format(len(cats), len(sd)))
    print("AND: {}  |  OR: {}\n".format(
        len(search.and_operator(cats, sd)), len(search.or_operator(cats, sd))))

    # Func5: galeria llegida d'un JSON (creat aquí amb les 3 primeres imatges)
    gallery_json = {
        "gallery_name": "Prova",
        "description": "Galeria de proves",
        "created_date": "2026-10-07",
        "images": added[:3] + ["no_existeix/fals.png"],
    }
    path = os.path.join(tempfile.gettempdir(), "gallery_prova.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gallery_json, f)

    gallery = Gallery(ids, viewer)
    gallery.load_file(path)
    print("Galeria '{}' amb {} imatges (la inexistent s'ha ignorat)".format(
        gallery.name, len(gallery)))
    gallery.show()

    # Func7: galeria dinàmica a partir d'una cerca
    result = Gallery(ids, viewer)
    result.load_uuids(cats)
    print("\nGaleria de la cerca: {} imatges".format(len(result)))
    if data.get_uuids():
        result.add_image_at_end(data.get_uuids()[0])
    result.remove_first_image()
    result.remove_last_image()
    print("Després d'afegir al final i treure primera i última: {} imatges".format(
        len(result)))

    print("\nFinal!")


if __name__ == "__main__":
    main()