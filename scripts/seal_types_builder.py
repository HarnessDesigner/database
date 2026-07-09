

import json


def _build_seal_types():

    data = (
        (0, 'None'),
        (1, 'Unknown Seal'),
        (2, 'Axial Seal'),
        (3, 'Radial Seal'),
        (4, 'Rubber Cap Over Wires'),
        (5, 'Single Wire Seal'),
        (6, 'SWS'),
        (7, 'Mat Seal'),
        (8, 'Dummy Terminal'),
        (9, 'Plug')
    )

    res = []
    for id, name in data:
        res.append(dict(id=id, name=name))

    return res


print(json.dumps(_build_seal_types(), indent=4))
