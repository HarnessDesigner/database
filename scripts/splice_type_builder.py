import json


def _build_splice_types():

    data = ((0, "Unknown"), (1, "Butt"), (2, "Cable"), (3, "Closed End"),
     (4, "Parallel"), (5, "Pigtail"), (6, "Tap"),
     (7, "Thru"), (8, "Solder Sleeve"), (9, "Solder Sleeve w/Pigtail"))

    res = []
    for id, name in data:
        res.append(dict(id=id, name=name))

    return res


print(json.dumps(_build_splice_types(), indent=4))
