import math
from decimal import Decimal
import os
import json


def _d(val):
    return Decimal(str(val))


def mm2_to_awg(mm2: float) -> int:
    d_mm = _d(2.0) * _d(math.sqrt(_d(mm2) / _d(math.pi)))
    d_in = d_mm / _d(25.4)
    awg = _d(36) - _d(39) * _d(math.log(float(d_in / _d(0.005)), 92))
    return int(round(awg))


def mm2_to_d_mm(mm2: float) -> float:
    d_mm = _d(2.0) * _d(math.sqrt(_d(mm2) / _d(math.pi)))
    return float(round(d_mm, 4))


def d_mm_to_mm2(d_mm: float) -> float:
    mm2 = _d(d_mm) / _d(2.0)
    mm2 *= mm2
    mm2 *= _d(math.pi)
    return float(round(mm2, 4))


def mm2_to_in2(mm2: float) -> float:
    in2 = _d(mm2) / _d(25.4)
    return float(round(in2, 4))


def in2_to_mm2(in2: float) -> float:
    mm2 = _d(in2) * _d(25.4)
    return float(round(mm2, 4))


def mm2_to_d_in(mm2: float) -> float:
    d_mm = mm2_to_d_mm(mm2)
    d_in = _d(d_mm) / _d(25.4)
    return float(round(d_in, 4))


def awg_to_d_mm(awg: int) -> float:
    return mm2_to_d_mm(awg_to_mm2(awg))


def awg_to_mm2(awg: int) -> float:
    d_in = _d(0.005) * (_d(92) ** ((_d(36) - _d(awg)) / _d(39)))
    d_mm = d_in * _d(25.4)
    area_mm2 = (_d(math.pi) / _d(4)) * (d_mm ** _d(2))
    return float(round(area_mm2, 4))


def d_mm_to_awg(d_mm: float) -> int:
    area_mm2 = (_d(math.pi) / _d(4)) * (_d(d_mm) ** _d(2))
    return mm2_to_awg(area_mm2)


def awg_to_d_in(awg: int) -> float:
    d_in = _d(0.005) * (_d(92) ** ((_d(36) - _d(awg)) / _d(39)))
    return float(round(d_in, 4))


def d_in_to_d_mm(d_in: float) -> float:
    d_mm = _d(d_in) * _d(25.4)
    return float(round(d_mm, 4))


# terminals
'''
new names
wire_size_awg_min
wire_size_awg_max

wire_size_dia_min
wire_size_dia_max

wire_size_cross_min
wire_size_cross_max


current names 
wire_size_min_awg -> wire_size_awg_min
wire_size_max_awg -> wire_size_awg_max

min_dia -> wire_size_dia_min
max_dia -> wire_size_dia_max

min_size_mm2 -> wire_size_cross_min
max_size_mm2 -> wire_size_cross_max
'''


def read_terminals(file):
    with open(file, 'r') as f:
        data = json.loads(f.read())

    for row in data:
        wire_size_awg_min = row.get('wire_size_min_awg', None)
        wire_size_awg_max = row.get('wire_size_max_awg', None)
        wire_size_dia_min = row.get('min_dia', None)
        wire_size_dia_max = row.get('max_dia', None)
        wire_size_cross_min = row.get('min_size_mm2', None)
        wire_size_cross_max = row.get('max_size_mm2', None)

        wire_size_dia_min = row.get('wire_dia_min', wire_size_dia_min)
        wire_size_dia_max = row.get('wire_dia_max', wire_size_dia_max)
        wire_size_cross_min = row.get('min_wire_cross', wire_size_cross_min)
        wire_size_cross_max = row.get('max_wire_cross', wire_size_cross_max)

        if wire_size_cross_min not in (None, 0.0):
            wire_size_awg_min = mm2_to_awg(wire_size_cross_min)
            wire_size_dia_min = mm2_to_d_mm(wire_size_cross_min)
        elif wire_size_awg_min not in (None, -1):
            wire_size_dia_min = awg_to_d_mm(wire_size_awg_min)
            wire_size_cross_min = awg_to_mm2(wire_size_awg_min)
        elif wire_size_dia_min not in (None, 0.0):
            wire_size_awg_min = d_mm_to_awg(wire_size_dia_min)
            wire_size_cross_min = d_mm_to_mm2(wire_size_dia_min)

        else:
            wire_size_awg_min = None
            wire_size_dia_min = None
            wire_size_cross_min = None

        if wire_size_cross_max not in (None, 0.0):
            wire_size_awg_max = mm2_to_awg(wire_size_cross_max)
            wire_size_dia_max = mm2_to_d_mm(wire_size_cross_max)
        elif wire_size_awg_max not in (None, -1):
            wire_size_dia_max = awg_to_d_mm(wire_size_awg_max)
            wire_size_cross_max = awg_to_mm2(wire_size_awg_max)
        elif wire_size_dia_max not in (None, 0.0):
            wire_size_awg_max = d_mm_to_awg(wire_size_dia_max)
            wire_size_cross_max = d_mm_to_mm2(wire_size_dia_max)
        else:
            wire_size_awg_max = None
            wire_size_dia_max = None
            wire_size_cross_max = None

        row['wire_size_awg_min'] = wire_size_awg_min
        row['wire_size_awg_max'] = wire_size_awg_max
        row['wire_size_dia_min'] = wire_size_dia_min
        row['wire_size_dia_max'] = wire_size_dia_max
        row['wire_size_cross_min'] = wire_size_cross_min
        row['wire_size_cross_max'] = wire_size_cross_max

        for key in (
            'wire_size_min_awg',
            'wire_size_max_awg',
            'min_dia',
            'max_dia',
            'min_size_mm2',
            'max_size_mm2',
            'wire_dia_min',
            'wire_dia_max',
            'min_wire_cross',
            'max_wire_cross'
        ):
            try:
                del row[key]
            except KeyError:
                pass

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=4))


# seals
'''
new names
wire_size_awg_min
wire_size_awg_max

wire_size_dia_min
wire_size_dia_max

wire_size_cross_min
wire_size_cross_max


current names 
min_size_awg -> wire_size_awg_min
max_size_awg -> wire_size_awg_max

wire_dia_min -> wire_size_dia_min
wire_dia_max -> wire_size_dia_max

min_size_mm2 -> wire_size_cross_min
max_size_mm2 -> wire_size_cross_max
'''


def read_seals(file):
    with open(file, 'r') as f:
        data = json.loads(f.read())

    for row in data:
        wire_size_awg_min = row.get('min_size_awg', None)
        wire_size_awg_max = row.get('max_size_awg', None)
        wire_size_dia_min = row.get('wire_dia_min', None)
        wire_size_dia_max = row.get('wire_dia_max', None)
        wire_size_cross_min = row.get('min_size_mm2', None)
        wire_size_cross_max = row.get('max_size_mm2', None)

        if wire_size_awg_min not in (None, -1):
            wire_size_dia_min = awg_to_d_mm(wire_size_awg_min)
            wire_size_cross_min = awg_to_mm2(wire_size_awg_min)
        elif wire_size_dia_min not in (None, 0.0):
            wire_size_awg_min = d_mm_to_awg(wire_size_dia_min)
            wire_size_cross_min = d_mm_to_mm2(wire_size_dia_min)
        elif wire_size_cross_min not in (None, 0.0):
            wire_size_awg_min = mm2_to_awg(wire_size_cross_min)
            wire_size_dia_min = mm2_to_d_mm(wire_size_cross_min)
        else:
            wire_size_awg_min = None
            wire_size_dia_min = None
            wire_size_cross_min = None

        if wire_size_awg_max not in (None, -1):
            wire_size_dia_max = awg_to_d_mm(wire_size_awg_max)
            wire_size_cross_max = awg_to_mm2(wire_size_awg_max)
        elif wire_size_dia_max not in (None, 0.0):
            wire_size_awg_max = d_mm_to_awg(wire_size_dia_max)
            wire_size_cross_max = d_mm_to_mm2(wire_size_dia_max)
        elif wire_size_cross_max not in (None, 0.0):
            wire_size_awg_max = mm2_to_awg(wire_size_cross_max)
            wire_size_dia_max = mm2_to_d_mm(wire_size_cross_max)
        else:
            wire_size_awg_max = None
            wire_size_dia_max = None
            wire_size_cross_max = None

        row['wire_size_awg_min'] = wire_size_awg_min
        row['wire_size_awg_max'] = wire_size_awg_max
        row['wire_size_dia_min'] = wire_size_dia_min
        row['wire_size_dia_max'] = wire_size_dia_max
        row['wire_size_cross_min'] = wire_size_cross_min
        row['wire_size_cross_max'] = wire_size_cross_max

        for key in (
            'min_size_awg',
            'max_size_awg',
            'wire_dia_min',
            'wire_dia_max',
            'min_size_mm2',
            'max_size_mm2'
        ):
            try:
                del row[key]
            except KeyError:
                pass

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=4))


# wire markers
'''
new names
wire_size_awg_min
wire_size_awg_max

wire_size_dia_min
wire_size_dia_max

wire_size_cross_min
wire_size_cross_max


current names 
min_awg -> wire_size_awg_min
max_awg -> wire_size_awg_max

-> wire_size_dia_min
-> wire_size_dia_max

-> wire_size_cross_min
-> wire_size_cross_max
'''


def read_wire_markers(file):
    with open(file, 'r') as f:
        data = json.loads(f.read())

    for row in data:
        wire_size_awg_min = row.get('min_awg', None)
        wire_size_awg_max = row.get('max_awg', None)

        if wire_size_awg_min not in (None, -1):
            wire_size_dia_min = awg_to_d_mm(wire_size_awg_min)
            wire_size_cross_min = awg_to_mm2(wire_size_awg_min)
        else:
            wire_size_awg_min = None
            wire_size_dia_min = None
            wire_size_cross_min = None

        if wire_size_awg_max not in (None, -1):
            wire_size_dia_max = awg_to_d_mm(wire_size_awg_max)
            wire_size_cross_max = awg_to_mm2(wire_size_awg_max)
        else:
            wire_size_awg_max = None
            wire_size_dia_max = None
            wire_size_cross_max = None

        row['wire_size_awg_min'] = wire_size_awg_min
        row['wire_size_awg_max'] = wire_size_awg_max
        row['wire_size_dia_min'] = wire_size_dia_min
        row['wire_size_dia_max'] = wire_size_dia_max
        row['wire_size_cross_min'] = wire_size_cross_min
        row['wire_size_cross_max'] = wire_size_cross_max

        for key in (
            'min_awg',
            'max_awg'
        ):
            try:
                del row[key]
            except KeyError:
                pass

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=4))


# wire
'''
new names
wire_size_awg

wire_size_dia

wire_size_cross


current names 
size_awg -> wire_size_awg

conductor_dia_mm -> wire_size_dia

size_mm2 -> wire_size_cross
'''


def read_wire(file):
    with open(file, 'r') as f:
        data = json.loads(f.read())

    for row in data:
        wire_size_awg = row.get('size_awg', None)
        wire_size_dia = row.get('conductor_dia_mm', None)
        wire_size_cross = row.get('size_mm2', None)

        if wire_size_awg not in (None, -1):
            if wire_size_dia in (None, 0.0):
                wire_size_dia = awg_to_d_mm(wire_size_awg)
            if wire_size_cross in (None, 0.0):
                wire_size_cross = awg_to_mm2(wire_size_awg)
        elif wire_size_dia not in (None, 0.0):
            if wire_size_awg in (None, -1):
                wire_size_awg = d_mm_to_awg(wire_size_dia)
            if wire_size_cross in (None, 0.0):
                wire_size_cross = d_mm_to_mm2(wire_size_dia)
        elif wire_size_cross not in (None, 0.0):
            if wire_size_awg in (None, -1):
                wire_size_awg = mm2_to_awg(wire_size_cross)
            if wire_size_dia in (None, 0.0):
                wire_size_dia = mm2_to_d_mm(wire_size_cross)
        else:
            wire_size_awg = None
            wire_size_dia = None
            wire_size_cross = None

        row['wire_size_awg'] = wire_size_awg
        row['wire_size_dia'] = wire_size_dia
        row['wire_size_cross'] = wire_size_cross

        for key in (
            'size_awg',
            'conductor_dia_mm',
            'size_mm2'
        ):
            try:
                del row[key]
            except KeyError:
                pass

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=4))


# splices
'''
new names
wire_size_awg_min
wire_size_awg_max

wire_size_dia_min
wire_size_dia_max

wire_size_cross_min
wire_size_cross_max

num_wires
'''

base_path = os.path.dirname(__file__)


def iter_files(p):
    dirs = []

    for file in os.listdir(p):
        file = os.path.join(p, file)
        if file.endswith('terminals.json'):
            print(file)
            read_terminals(file)

        if file.endswith('seals.json'):
            print(file)
            read_seals(file)

        if file.endswith('wires.json'):
            print(file)
            read_wire(file)

        if file.endswith('wire_markers.json'):
            print(file)
            read_wire_markers(file)

        elif os.path.isdir(file):
            dirs.append(file)

    for file in dirs:
        iter_files(file)


iter_files(base_path)
