import os

base_path = os.path.dirname(__file__)


def iter_files(p):
    for file in os.listdir(p):
        file = os.path.join(p, file)
        if os.path.isdir(file):
            iter_files(file)
        elif file.endswith('.json'):
            with open(file, 'r') as f:
                data = f.read()

            data = data.replace('\u00a0', '')
            with open(file, 'w') as f:
                f.write(data)


iter_files(base_path)
