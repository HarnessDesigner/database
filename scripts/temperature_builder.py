import json


def _build_temps():
    data = [dict(id=0, name='Unknown')]

    for i in range(-100, 305, 5):
        if i > 0:
            i = '+' + str(i)
        else:
            i = str(i)

        i += '°C'
        data.append(dict(id=len(data), name=i))

    return data


print(json.dumps(_build_temps(), indent=4))

