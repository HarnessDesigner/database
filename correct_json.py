

color_map = {
    'Blue - Transluscent': 'Blue',
    'Red - Green': 'Red',
    'Blue - Green': 'Blue Green',
    'Yellow - Green': 'Yellow Green',
    'Brown - Green': 'Brown',
    'Violet - Green': 'Violet',
    'Black - Orange': 'Black',
    'Gray  - Orange': 'Gray',
    'Clear': 'Light Gray',
    'Yellow - Translucent': 'Yellow',
    'Rust Red': 'Rust',
    'Red-Orange': 'Red Orange',
    'Green & Yellow': 'Green Yellow',
    'Black Matte': 'Black Shadows',
    'Beige White': 'Beige',
    'Emerald Green': 'Emerald',
    'Ivory': 'Vanilla',
    'Cream Yellow': 'Arylide Yellow',
    'Metalized Silver': 'Silver',
    'Gray & Dark Gray': 'Gray'
}


import os
import json


used_part_numbers = {}


model_count = 0


def read_file(in_file):
    global model_count

    if '.old.' not in in_file:
        return

    filename = os.path.split(in_file)[-1]
    filename = os.path.splitext(os.path.splitext(filename)[0])[0]
    if filename not in used_part_numbers:
        used_part_numbers[filename] = []

    with open(in_file, 'r') as f:
        data = f.read()

    for key, value in color_map.items():
        data = data.replace(key, value)

    output = []

    data = json.loads(data)

    if isinstance(data, list):
        for row in data:
            if 'part_number' in row:
                pn = row['part_number']
                if pn not in used_part_numbers[filename]:
                    used_part_numbers[filename].append(pn)
                    output.append(row)
                else:
                    print('duplicate:', pn)

                if row.get('model3d', None) is not None:
                    model_count += 1

            else:
                output.append(row)

    else:
        for row in data.values():
            if 'part_number' in row:
                pn = row['part_number']
                if pn not in used_part_numbers[filename]:
                    used_part_numbers[filename].append(pn)
                    output.append(row)
                else:
                    print('duplicate:', pn)

                if row.get('model3d', None) is not None:
                    model_count += 1
            else:
                output.append(row)

    print(in_file, ':', len(data), ':', len(output))

    with open(os.path.join(os.path.split(in_file)[0], filename + '.new.json'), 'w') as f:
        f.write(json.dumps(output, indent=4))


base_path = os.path.dirname(__file__)


def iter_files(p):
    dirs = []

    for file in os.listdir(p):
        file = os.path.join(p, file)
        if file.endswith('.json') and '.bak.' not in file:
            print(file)
            read_file(file)
        elif os.path.isdir(file):
            dirs.append(file)

    for file in dirs:
        iter_files(file)


iter_files(base_path)

print()
print(model_count)
