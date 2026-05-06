import json

files = ['covers.json', 'cpa_locks.json', 'housings.json', 'seals.json', 'terminals.json', 'tpa_locks.json']

for file in files:

    with open(file, 'r') as f:
        data = json.loads(f.read())

    for value in data.values():
        if 'image' in value and value['image'] is not None:
            if ', ' in value['image']:
                value['image'] = value['image'].split(', ')[0]

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=4))
