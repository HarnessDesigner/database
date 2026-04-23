

import json


def _build_platings():

    data = (
        (0, 'Unknown', 'Unknown'),
        (1, 'Sn', 'Tin'),
        (2, 'Cu', 'Copper'),
        (3, 'Al', 'Aluminum'),
        (4, 'Ti', 'Titanium'),
        (5, 'Zn', 'Zinc'),
        (6, 'Au', 'Gold'),
        (7, 'Ag', 'Silver'),
        (8, 'Ni', 'Nickel'),
        (9, 'Ag/Cu', 'Silver-plated Copper'),
        (10, 'Sn/Cu', 'Tin-plated Copper'),
        (11, 'Au/Cu', 'Gold-plated Copper'),
        (12, 'Ni/Cu', 'Nickel-plated Copper'),
        (13, 'Ag/Al', 'Silver-plated Aluminum'),
        (14, 'Sn/Al', 'Tin-plated Aluminum'),
        (15, 'Au/Al', 'Gold-plated Aluminum')
    )

    res = []
    for id, symbol, description in data:
        res.append(dict(id=id, symbol=symbol, description=description))

    return res


print(json.dumps(_build_platings(), indent=4))
