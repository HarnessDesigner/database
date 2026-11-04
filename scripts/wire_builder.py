import argparse
import itertools
import json
import math
import os


# ---------------------------------------------------------------------------
# Unit conversion constant
# ---------------------------------------------------------------------------

MM2_PER_IN2 = 645.16


# ---------------------------------------------------------------------------
# Stranding tables
# ---------------------------------------------------------------------------

# Generic strand counts by AWG used when strands=0 (stranded but count unknown)
_AWG_STRAND_COUNT = {
    -4: 2109,
    -3: 1665,
    -2: 1330,
    0: 1045,
    1: 817,
    2: 665,
    4: 133,
    6: 133,
    8: 133,
    10: 37,
    12: 19,
    14: 19,
    16: 19,
    18: 19,
    20: 19,
    22: 19,
    24: 19,
    26: 19,
    28: 7,
    30: 7,
}

# Packing factors by strand count
_PACKING_FACTOR = {
    1: 1.000,
    7: 0.750,
    19: 0.780,
    37: 0.800,
    133: 0.830,
    665: 0.850,
    817: 0.850,
    1045: 0.850,
    1330: 0.850,
    1665: 0.850,
    2109: 0.850,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_strand_count(awg: int, strands: int) -> int:
    strands = int(strands)
    if strands == 1:
        return 1
    if strands == 0:
        return _AWG_STRAND_COUNT.get(int(awg), 19)
    return strands


def _get_packing_factor(strand_count: int) -> float:
    if strand_count in _PACKING_FACTOR:
        return _PACKING_FACTOR[strand_count]
    known = sorted(_PACKING_FACTOR.keys())
    for i, k in enumerate(known):
        if strand_count < k:
            if i == 0:
                return _PACKING_FACTOR[k]
            lo, hi = known[i - 1], k
            t = (strand_count - lo) / (hi - lo)
            return _PACKING_FACTOR[lo] + t * (_PACKING_FACTOR[hi] - _PACKING_FACTOR[lo])
    return _PACKING_FACTOR[known[-1]]


def _solid_to_bundle(solid_d_mm: float, strand_count: int) -> float:
    if strand_count == 1:
        return solid_d_mm
    return solid_d_mm / math.sqrt(_get_packing_factor(strand_count))


def _bundle_to_solid(bundle_d_mm: float, strand_count: int) -> float:
    if strand_count == 1:
        return bundle_d_mm
    return bundle_d_mm * math.sqrt(_get_packing_factor(strand_count))


# ---------------------------------------------------------------------------
# Public conversion functions
# ---------------------------------------------------------------------------

def mm2_to_awg(mm2: float, strands: int = 1) -> int:
    d_in = mm2_to_d_in(mm2, strands)
    awg = 36 - 39 * math.log(float(d_in / 0.005), 92)
    return int(round(awg))


def awg_to_mm2(awg: int, strands: int = 1) -> float:  # NOQA
    # mm² is always the electrical equivalent cross-section — stranding doesn't change it
    d_in = float(round(0.005 * 92 ** ((36 - int(awg)) / 39), 6))
    d_mm = d_in * 25.4
    return float(round(math.pi / 4 * d_mm ** 2, 4))


def awg_to_d_in(awg: int, strands: int = 1) -> float:
    d_in = float(round(0.005 * 92 ** ((36 - int(awg)) / 39), 6))
    strand_count = _get_strand_count(awg, strands)
    d_mm = _solid_to_bundle(d_in * 25.4, strand_count)
    return float(round(d_mm / 25.4, 4))


def awg_to_d_mm(awg: int, strands: int = 1) -> float:
    d_in = float(round(0.005 * 92 ** ((36 - int(awg)) / 39), 6))
    strand_count = _get_strand_count(awg, strands)
    return float(round(_solid_to_bundle(d_in * 25.4, strand_count), 4))


def d_in_to_d_mm(d_in: float, strands: int = 1) -> float:  # NOQA
    return float(round(float(d_in) * 25.4, 4))


def d_mm_to_mm2(d_mm: float, strands: int = 1) -> float:  # NOQA
    return float(round(math.pi / 4 * float(d_mm) ** 2, 4))


def mm2_to_d_mm(mm2: float, strands: int = 1) -> float:
    solid_d_mm = 2 * math.sqrt(float(mm2 / math.pi))
    strand_count = _get_strand_count(mm2_to_awg(mm2, strands=1), strands)
    return float(round(_solid_to_bundle(solid_d_mm, strand_count), 4))


def mm2_to_d_in(mm2: float, strands: int = 1) -> float:
    return float(round(mm2_to_d_mm(mm2, strands) / 25.4, 4))


def d_mm_to_awg(d_mm: float, strands: int = 1) -> int:
    # Convert bundle diameter back to solid equivalent, then derive AWG
    approx_awg = mm2_to_awg(d_mm_to_mm2(float(d_mm), strands), strands=1)
    strand_count = _get_strand_count(approx_awg, strands)
    solid_d_mm = _bundle_to_solid(float(d_mm), strand_count)
    return mm2_to_awg(d_mm_to_mm2(solid_d_mm, strands), strands=1)


def mm2_to_in2(mm2: float, strands: int = 1) -> float:  # NOQA
    return float(round(mm2 / MM2_PER_IN2, 4))


def in2_to_mm2(in2: float, strands: int = 1) -> float:  # NOQA
    return float(round(in2 * MM2_PER_IN2, 4))


# ---------------------------------------------------------------------------
# Milspec wire data
# ---------------------------------------------------------------------------

def _build_wires():
    # All dimensions in mm. dia = conductor bundle diameter, od = max insulation diameter.
    # Weights in kg/km, resistance in Ω/km @20°C.
    # strands = number of strands in the conductor (first number of stranding e.g. 133/29 -> 133)
    # Source: MIL-DTL-22759 / SAE AS22759 spec (Amphenol CIT / Thermax datasheet).
    mapping = {
        'M22759/5': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with abrasion-resistant mineral fillers',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                8:  {'dia': 4.11, 'od': 6.48, 'weight': 115.00, 'resistance': 2.16, 'strands': 133},
                10: {'dia': 2.74, 'od': 4.73, 'weight': 63.30, 'resistance': 3.90, 'strands': 37},
                12: {'dia': 2.18, 'od': 4.24, 'weight': 46.00, 'resistance': 5.94, 'strands': 19},
                14: {'dia': 1.70, 'od': 3.81, 'weight': 33.50, 'resistance': 9.45, 'strands': 19},
                16: {'dia': 1.35, 'od': 3.30, 'weight': 24.70, 'resistance': 14.80, 'strands': 19},
                18: {'dia': 1.19, 'od': 2.92, 'weight': 19.20, 'resistance': 19.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 2.54, 'weight': 13.60, 'resistance': 30.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 2.29, 'weight': 10.10, 'resistance': 49.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 2.03, 'weight': 7.60, 'resistance': 79.70, 'strands': 19},
            }
        },
        'M22759/6': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with abrasion-resistant mineral fillers',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8:  {'dia': 4.14, 'od': 6.48, 'weight': 118.00, 'resistance': 2.28, 'strands': 133},
                10: {'dia': 2.77, 'od': 4.73, 'weight': 64.80, 'resistance': 4.07, 'strands': 37},
                12: {'dia': 2.18, 'od': 4.24, 'weight': 47.50, 'resistance': 6.20, 'strands': 19},
                14: {'dia': 1.70, 'od': 3.81, 'weight': 34.70, 'resistance': 9.84, 'strands': 19},
                16: {'dia': 1.35, 'od': 3.30, 'weight': 25.20, 'resistance': 15.60, 'strands': 19},
                18: {'dia': 1.19, 'od': 2.92, 'weight': 19.50, 'resistance': 20.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 2.54, 'weight': 13.90, 'resistance': 32.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 2.29, 'weight': 10.40, 'resistance': 52.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 2.03, 'weight': 7.70, 'resistance': 85.00, 'strands': 19},
            }
        },
        'M22759/7': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with abrasion-resistant mineral fillers (reduced weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                8:  {'dia': 4.11, 'od': 5.72, 'weight': 101.00, 'resistance': 2.16, 'strands': 133},
                10: {'dia': 2.74, 'od': 4.11, 'weight': 55.70, 'resistance': 3.90, 'strands': 37},
                12: {'dia': 2.18, 'od': 3.48, 'weight': 38.30, 'resistance': 5.94, 'strands': 19},
                14: {'dia': 1.70, 'od': 3.00, 'weight': 25.80, 'resistance': 9.45, 'strands': 19},
                16: {'dia': 1.35, 'od': 2.67, 'weight': 18.90, 'resistance': 14.80, 'strands': 19},
                18: {'dia': 1.19, 'od': 2.39, 'weight': 15.20, 'resistance': 19.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 2.13, 'weight': 10.90, 'resistance': 30.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.91, 'weight': 7.44, 'resistance': 49.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.63, 'weight': 5.51, 'resistance': 79.70, 'strands': 19},
            }
        },
        'M22759/8': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with abrasion-resistant mineral fillers (reduced weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8:  {'dia': 4.14, 'od': 5.72, 'weight': 104.00, 'resistance': 2.28, 'strands': 133},
                10: {'dia': 2.77, 'od': 4.11, 'weight': 57.20, 'resistance': 4.07, 'strands': 37},
                12: {'dia': 2.18, 'od': 3.48, 'weight': 42.80, 'resistance': 6.20, 'strands': 19},
                14: {'dia': 1.70, 'od': 3.00, 'weight': 27.00, 'resistance': 9.84, 'strands': 19},
                16: {'dia': 1.35, 'od': 2.67, 'weight': 19.40, 'resistance': 15.60, 'strands': 19},
                18: {'dia': 1.19, 'od': 2.39, 'weight': 15.50, 'resistance': 20.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 2.13, 'weight': 11.20, 'resistance': 32.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.91, 'weight': 7.66, 'resistance': 52.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.63, 'weight': 5.66, 'resistance': 85.00, 'strands': 19},
            }
        },
        'M22759/9': {
            'start': 8,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE',
            'volts': 1000,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                8:  {'dia': 4.11, 'od': 5.38, 'weight': 97.30, 'resistance': 2.16, 'strands': 133},
                10: {'dia': 2.74, 'od': 3.68, 'weight': 52.50, 'resistance': 3.90, 'strands': 37},
                12: {'dia': 2.18, 'od': 3.15, 'weight': 34.70, 'resistance': 5.94, 'strands': 19},
                14: {'dia': 1.70, 'od': 2.62, 'weight': 24.00, 'resistance': 9.45, 'strands': 19},
                16: {'dia': 1.35, 'od': 2.21, 'weight': 15.80, 'resistance': 14.80, 'strands': 19},
                18: {'dia': 1.19, 'od': 2.03, 'weight': 12.90, 'resistance': 19.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 30.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 49.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 79.70, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 126.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 209.00, 'strands': 7},
            }
        },
        'M22759/10': {
            'start': 8,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE',
            'volts': 1000,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8:  {'dia': 4.14, 'od': 5.38, 'weight': 98.80, 'resistance': 2.28, 'strands': 133},
                10: {'dia': 2.77, 'od': 3.68, 'weight': 53.40, 'resistance': 4.07, 'strands': 37},
                12: {'dia': 2.18, 'od': 3.15, 'weight': 34.80, 'resistance': 6.20, 'strands': 19},
                14: {'dia': 1.70, 'od': 2.62, 'weight': 24.10, 'resistance': 9.84, 'strands': 19},
                16: {'dia': 1.35, 'od': 2.21, 'weight': 16.10, 'resistance': 15.60, 'strands': 19},
                18: {'dia': 1.19, 'od': 2.03, 'weight': 12.90, 'resistance': 20.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 32.00, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 52.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 85.00, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 138.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 223.00, 'strands': 7},
            }
        },
        'M22759/11': {
            'start': 8,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Thin-wall extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                8:  {'dia': 4.11, 'od': 5.23, 'weight': 86.10, 'resistance': 2.16, 'strands': 133},
                10: {'dia': 2.74, 'od': 3.63, 'weight': 52.00, 'resistance': 3.90, 'strands': 37},
                12: {'dia': 2.18, 'od': 2.90, 'weight': 35.00, 'resistance': 5.94, 'strands': 19},
                14: {'dia': 1.70, 'od': 2.34, 'weight': 21.90, 'resistance': 9.45, 'strands': 19},
                16: {'dia': 1.35, 'od': 1.96, 'weight': 14.30, 'resistance': 14.80, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.78, 'weight': 11.30, 'resistance': 19.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.66, 'resistance': 30.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.12, 'resistance': 49.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.59, 'resistance': 79.70, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.59, 'resistance': 126.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.82, 'resistance': 209.00, 'strands': 7},
            }
        },
        'M22759/12': {
            'start': 8,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Thin-wall extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8:  {'dia': 4.14, 'od': 5.28, 'weight': 87.50, 'resistance': 2.28, 'strands': 133},
                10: {'dia': 2.77, 'od': 3.63, 'weight': 52.80, 'resistance': 4.07, 'strands': 37},
                12: {'dia': 2.18, 'od': 2.90, 'weight': 35.70, 'resistance': 6.20, 'strands': 19},
                14: {'dia': 1.70, 'od': 2.34, 'weight': 22.00, 'resistance': 9.84, 'strands': 19},
                16: {'dia': 1.35, 'od': 1.96, 'weight': 14.50, 'resistance': 15.60, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.78, 'weight': 11.40, 'resistance': 20.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.72, 'resistance': 32.00, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.15, 'resistance': 52.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.60, 'resistance': 85.00, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.60, 'resistance': 138.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.83, 'resistance': 223.00, 'strands': 7},
            }
        },
        'M22759/16': {
            'start': -2,
            'stop': 25,
            'step': 1,
            'con_plate': 'Sn/Cu',
            'material': 'Extruded ETFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                -2: {'dia': 11.70, 'od': 14.00, 'weight': 722.00, 'resistance': 0.30, 'strands': 1330},
                -1: {'dia': 10.50, 'od': 12.30, 'weight': 566.00, 'resistance': 0.38, 'strands': 1045},
                1: {'dia':  9.40, 'od': 11.10, 'weight': 437.00, 'resistance': 0.49, 'strands': 817},
                2: {'dia':  8.38, 'od':  9.96, 'weight': 344.00, 'resistance': 0.60, 'strands': 665},
                4: {'dia':  6.60, 'od':  8.03, 'weight': 227.00, 'resistance': 0.92, 'strands': 133},
                6: {'dia':  5.13, 'od':  6.43, 'weight': 144.00, 'resistance': 1.46, 'strands': 133},
                8: {'dia':  4.11, 'od':  5.13, 'weight': 91.50, 'resistance': 2.30, 'strands': 133},
                10: {'dia':  2.79, 'od':  3.61, 'weight': 50.60, 'resistance': 4.13, 'strands': 37},
                12: {'dia':  2.18, 'od':  2.97, 'weight': 32.40, 'resistance': 6.63, 'strands': 37},
                14: {'dia':  1.70, 'od':  2.41, 'weight': 21.60, 'resistance': 10.00, 'strands': 19},
                16: {'dia':  1.35, 'od':  2.06, 'weight': 14.40, 'resistance': 15.80, 'strands': 19},
                18: {'dia':  1.22, 'od':  1.85, 'weight': 11.40, 'resistance': 20.40, 'strands': 19},
                20: {'dia':  0.97, 'od':  1.57, 'weight': 7.71, 'resistance': 32.40, 'strands': 19},
                22: {'dia':  0.76, 'od':  1.37, 'weight': 5.24, 'resistance': 53.10, 'strands': 19},
                24: {'dia':  0.61, 'od':  1.19, 'weight': 3.65, 'resistance': 85.90, 'strands': 19},
            }
        },
        'M22759/17': {
            'start': 20,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded ETFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                20: {'dia': 0.97, 'od': 1.57, 'weight': 7.38, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.37, 'weight': 5.06, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.19, 'weight': 3.45, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.07, 'weight': 2.49, 'resistance': 147.00, 'strands': 19},
            }
        },
        'M22759/18': {
            'start': 10,
            'stop': 27,
            'step': 2,
            'con_plate': 'Sn/Cu',
            'material': 'Thin-wall extruded ETFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                10: {'dia': 2.79, 'od': 3.48, 'weight': 49.30, 'resistance': 4.13, 'strands': 37},
                12: {'dia': 2.18, 'od': 2.80, 'weight': 31.30, 'resistance': 6.63, 'strands': 37},
                14: {'dia': 1.70, 'od': 2.21, 'weight': 20.40, 'resistance': 10.00, 'strands': 19},
                16: {'dia': 1.35, 'od': 1.83, 'weight': 13.30, 'resistance': 15.80, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.60, 'weight': 10.30, 'resistance': 20.40, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.35, 'weight': 6.85, 'resistance': 32.40, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.14, 'weight': 4.52, 'resistance': 53.10, 'strands': 19},
                24: {'dia': 0.61, 'od': 0.97, 'weight': 3.01, 'resistance': 85.90, 'strands': 19},
                26: {'dia': 0.48, 'od': 0.86, 'weight': 2.26, 'resistance': 135.00, 'strands': 19},
            }
        },
        'M22759/19': {
            'start': 20,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Thin-wall extruded ETFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                20: {'dia': 0.97, 'od': 1.35, 'weight': 6.62, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.14, 'weight': 4.27, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.61, 'od': 0.97, 'weight': 2.86, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.48, 'od': 0.86, 'weight': 2.02, 'resistance': 147.00, 'strands': 19},
            }
        },
        'M22759/20': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE',
            'volts': 1000,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 147.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 244.00, 'strands': 7},
            }
        },
        'M22759/21': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE',
            'volts': 1000,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 37.40, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 61.00, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 98.70, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 162.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 259.00, 'strands': 7},
            }
        },
        'M22759/22': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Thin-wall extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.72, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.28, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.74, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.74, 'resistance': 147.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.89, 'resistance': 244.00, 'strands': 7},
            }
        },
        'M22759/23': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Thin-wall extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.84, 'resistance': 37.40, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.39, 'resistance': 61.00, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.79, 'resistance': 98.70, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.77, 'resistance': 162.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.92, 'resistance': 259.00, 'strands': 7},
            }
        },
        'M22759/28': {
            'start': 14,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with polyimide hard coat',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                14: {'dia': 1.70, 'od': 2.39, 'weight': 22.00, 'resistance': 9.45, 'strands': 19},
                16: {'dia': 1.35, 'od': 2.01, 'weight': 14.50, 'resistance': 14.80, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.80, 'weight': 11.40, 'resistance': 19.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.80, 'resistance': 30.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.22, 'resistance': 49.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.68, 'resistance': 79.70, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.68, 'resistance': 126.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.89, 'resistance': 209.00, 'strands': 7},
            }
        },
        'M22759/29': {
            'start': 14,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with polyimide hard coat',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                14: {'dia': 1.70, 'od': 2.39, 'weight': 22.00, 'resistance': 9.84, 'strands': 19},
                16: {'dia': 1.35, 'od': 2.01, 'weight': 14.50, 'resistance': 15.60, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.80, 'weight': 11.40, 'resistance': 20.00, 'strands': 19},
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.80, 'resistance': 32.00, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.22, 'resistance': 52.50, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.68, 'resistance': 85.00, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.68, 'resistance': 138.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.89, 'resistance': 223.00, 'strands': 7},
            }
        },
        'M22759/30': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with polyimide hard coat',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.80, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.22, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.68, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.68, 'resistance': 147.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.89, 'resistance': 244.00, 'strands': 7},
            }
        },
        'M22759/31': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with polyimide hard coat',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.86, 'resistance': 37.40, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.24, 'resistance': 61.00, 'strands': 19},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.69, 'resistance': 98.70, 'strands': 19},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.69, 'resistance': 162.00, 'strands': 19},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.90, 'resistance': 259.00, 'strands': 7},
            }
        },
        'M22759/32': {
            'start': 12,
            'stop': 31,
            'step': 2,
            'con_plate': 'Sn/Cu',
            'material': 'Extruded XL-ETFE (cross-linked modified ETFE), single wall',
            'volts': 600,
            'min_temp': -65,
            'max_temp': 150,
            'data': {
                30: {'dia': 0.28, 'od': 0.66, 'weight': 0.98, 'resistance': 355.643, 'strands': 7},
                28: {'dia': 0.36, 'od': 0.74, 'weight': 1.35, 'resistance': 225.066, 'strands': 7},
                26: {'dia': 0.46, 'od': 0.86, 'weight': 2.08, 'resistance': 135.499, 'strands': 19},
                24: {'dia': 0.58, 'od': 0.99, 'weight': 2.98, 'resistance': 85.958, 'strands': 19},
                22: {'dia': 0.74, 'od': 1.14, 'weight': 4.17, 'resistance': 53.15, 'strands': 19},
                20: {'dia': 0.94, 'od': 1.32, 'weight': 6.40, 'resistance': 32.415, 'strands': 19},
                18: {'dia': 1.17, 'od': 1.57, 'weight': 9.67, 'resistance': 20.44, 'strands': 19},
                16: {'dia': 1.32, 'od': 1.78, 'weight': 12.35, 'resistance': 15.781, 'strands': 19},
                14: {'dia': 1.65, 'od': 2.31, 'weight': 19.35, 'resistance': 10.039, 'strands': 19},
                12: {'dia': 2.13, 'od': 2.77, 'weight': 29.32, 'resistance': 6.627, 'strands': 37},
            }
        },
        'M22759/33': {
            'start': 20,
            'stop': 31,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded XL-ETFE (cross-linked modified ETFE), single wall, high-strength copper alloy conductor',
            'volts': 600,
            'min_temp': -65,
            'max_temp': 200,
            'data': {
                30: {'dia': 0.29, 'od': 0.66, 'weight': 0.98, 'resistance': 385.171, 'strands': 7},
                28: {'dia': 0.38, 'od': 0.74, 'weight': 1.35, 'resistance': 244.094, 'strands': 7},
                26: {'dia': 0.48, 'od': 0.86, 'weight': 2.08, 'resistance': 146.982, 'strands': 19},
                24: {'dia': 0.61, 'od': 0.99, 'weight': 2.98, 'resistance': 93.176, 'strands': 19},
                22: {'dia': 0.76, 'od': 1.14, 'weight': 4.32, 'resistance': 57.415, 'strands': 19},
                20: {'dia': 0.96, 'od': 1.32, 'weight': 6.55, 'resistance': 35.105, 'strands': 19},
            }
        },
        'M22759/43': {
            'start': 8,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded XL-ETFE (cross-linked modified ETFE), dual wall',
            'volts': 600,
            'min_temp': -65,
            'max_temp': 200,
            'data': {
                26: {'dia': 0.47, 'od': 1.07, 'weight': 2.53, 'resistance': 125.984, 'strands': 19},
                24: {'dia': 0.60, 'od': 1.19, 'weight': 3.42, 'resistance': 79.724, 'strands': 19},
                22: {'dia': 0.75, 'od': 1.32, 'weight': 4.91, 'resistance': 49.541, 'strands': 19},
                20: {'dia': 0.95, 'od': 1.52, 'weight': 6.99, 'resistance': 30.151, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.85, 'weight': 10.71, 'resistance': 18.996, 'strands': 19},
                16: {'dia': 1.34, 'od': 2.03, 'weight': 13.39, 'resistance': 14.829, 'strands': 19},
                14: {'dia': 1.69, 'od': 2.46, 'weight': 20.54, 'resistance': 9.449, 'strands': 19},
                12: {'dia': 2.17, 'od': 2.90, 'weight': 30.51, 'resistance': 6.234, 'strands': 37},
                10: {'dia': 2.77, 'od': 3.51, 'weight': 48.22, 'resistance': 3.904, 'strands': 37},
                8: {'dia': 4.15, 'od': 5.16, 'weight': 96.73, 'resistance': 2.159, 'strands': 133},
            }
        },
        'M22759/44': {
            'start': 12,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded XL-ETFE (cross-linked modified ETFE), lightweight single wall',
            'volts': 600,
            'min_temp': -65,
            'max_temp': 200,
            'data': {
                28: {'dia': 0.37, 'od': 0.74, 'weight': 1.35, 'resistance': 209.318, 'strands': 7},
                26: {'dia': 0.47, 'od': 0.86, 'weight': 2.08, 'resistance': 125.984, 'strands': 19},
                24: {'dia': 0.61, 'od': 0.99, 'weight': 2.98, 'resistance': 79.724, 'strands': 19},
                22: {'dia': 0.75, 'od': 1.14, 'weight': 4.17, 'resistance': 49.541, 'strands': 19},
                20: {'dia': 0.96, 'od': 1.32, 'weight': 6.40, 'resistance': 30.151, 'strands': 19},
                18: {'dia': 1.19, 'od': 1.57, 'weight': 9.67, 'resistance': 18.996, 'strands': 19},
                16: {'dia': 1.34, 'od': 1.78, 'weight': 12.35, 'resistance': 14.829, 'strands': 19},
                14: {'dia': 1.69, 'od': 2.24, 'weight': 19.35, 'resistance': 9.449, 'strands': 19},
                12: {'dia': 2.17, 'od': 2.69, 'weight': 29.32, 'resistance': 6.234, 'strands': 37},
            }
        },
        'M22759/80': {
            'start': 10,
            'stop': 27,
            'step': 2,
            'con_plate': 'Sn/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape (light weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                10: {'dia': 2.84, 'od': 3.12, 'weight': 45.20, 'resistance': 4.13, 'strands': 37},
                12: {'dia': 2.27, 'od': 2.54, 'weight': 28.90, 'resistance': 6.63, 'strands': 37},
                14: {'dia': 1.76, 'od': 2.03, 'weight': 18.40, 'resistance': 10.00, 'strands': 19},
                16: {'dia': 1.41, 'od': 1.70, 'weight': 11.90, 'resistance': 15.80, 'strands': 19},
                18: {'dia': 1.25, 'od': 1.52, 'weight': 9.50, 'resistance': 20.40, 'strands': 19},
                20: {'dia': 1.00, 'od': 1.30, 'weight': 6.40, 'resistance': 32.40, 'strands': 19},
                22: {'dia': 0.80, 'od': 1.09, 'weight': 4.10, 'resistance': 53.10, 'strands': 19},
                24: {'dia': 0.62, 'od': 0.97, 'weight': 2.80, 'resistance': 85.90, 'strands': 19},
                26: {'dia': 0.52, 'od': 0.86, 'weight': 1.90, 'resistance': 135.00, 'strands': 19},
            }
        },
        'M22759/81': {
            'start': 20,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape (light weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                20: {'dia': 1.00, 'od': 1.30, 'weight': 6.50, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.80, 'od': 1.09, 'weight': 4.20, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.62, 'od': 0.97, 'weight': 2.80, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.52, 'od': 0.86, 'weight': 2.10, 'resistance': 185.00, 'strands': 19},
            }
        },
        'M22759/82': {
            'start': 20,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape (light weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                20: {'dia': 1.03, 'od': 1.30, 'weight': 6.40, 'resistance': 37.40, 'strands': 19},
                22: {'dia': 0.80, 'od': 1.09, 'weight': 4.20, 'resistance': 61.00, 'strands': 19},
                24: {'dia': 0.65, 'od': 0.97, 'weight': 2.80, 'resistance': 98.30, 'strands': 19},
                26: {'dia': 0.52, 'od': 0.86, 'weight': 2.10, 'resistance': 191.00, 'strands': 19},
            }
        },
        'M22759/83': {
            'start': -4,
            'stop': 3,
            'step': 1,
            'con_plate': 'Ag/Cu',
            'material': 'PTFE tape and PTFE/polyimide/PTFE tape with polyamide braid',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                -4: {'dia': 15.37, 'od': 16.64, 'weight': 984.0, 'resistance': 0.177, 'strands': 2109},
                -3: {'dia': 13.72, 'od': 14.83, 'weight': 774.1, 'resistance': 0.223, 'strands': 1665},
                -2: {'dia': 12.07, 'od': 13.41, 'weight': 617.0, 'resistance': 0.279, 'strands': 1330},
                0: {'dia': 10.80, 'od': 11.73, 'weight': 501.4, 'resistance': 0.354, 'strands': 1045},
                1: {'dia':  9.65, 'od': 10.67, 'weight': 419.6, 'resistance': 0.456, 'strands': 817},
                2: {'dia':  8.64, 'od':  9.65, 'weight': 324.2, 'resistance': 0.558, 'strands': 665},
            }
        },
        'M22759/84': {
            'start': -4,
            'stop': 3,
            'step': 1,
            'con_plate': 'Ni/Cu',
            'material': 'PTFE tape and PTFE/polyimide/PTFE tape with polyamide braid',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                -4: {'dia': 15.37, 'od': 16.64, 'weight': 984.0, 'resistance': 0.184, 'strands': 2109},
                -3: {'dia': 13.72, 'od': 14.83, 'weight': 774.1, 'resistance': 0.233, 'strands': 1665},
                -2: {'dia': 12.07, 'od': 13.41, 'weight': 617.0, 'resistance': 0.292, 'strands': 1330},
                0: {'dia': 10.80, 'od': 11.73, 'weight': 501.4, 'resistance': 0.371, 'strands': 1045},
                1: {'dia':  9.65, 'od': 10.67, 'weight': 419.6, 'resistance': 0.472, 'strands': 817},
                2: {'dia':  8.64, 'od':  9.65, 'weight': 324.2, 'resistance': 0.581, 'strands': 665},
            }
        },
        'M22759/85': {
            'start': -4,
            'stop': 3,
            'step': 1,
            'con_plate': 'Sn/Cu',
            'material': 'PTFE tape and PTFE/polyimide/PTFE tape with polyamide braid',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                -4: {'dia': 15.37, 'od': 16.64, 'weight': 984.0, 'resistance': 0.184, 'strands': 2109},
                -3: {'dia': 13.72, 'od': 14.83, 'weight': 774.1, 'resistance': 0.233, 'strands': 1665},
                -2: {'dia': 12.07, 'od': 13.41, 'weight': 617.0, 'resistance': 0.298, 'strands': 1330},
                0: {'dia': 10.80, 'od': 11.73, 'weight': 501.4, 'resistance': 0.380, 'strands': 1045},
                1: {'dia':  9.65, 'od': 10.67, 'weight': 408.4, 'resistance': 0.489, 'strands': 817},
                2: {'dia':  8.64, 'od':  9.65, 'weight': 324.2, 'resistance': 0.600, 'strands': 665},
            }
        },
        'M22759/86': {
            'start': -4,
            'stop': 27,
            'step': 1,
            'con_plate': 'Ag/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                -4: {'dia': 15.37, 'od': 16.00, 'weight': 1012.9, 'resistance': 0.177, 'strands': 2109},
                -3: {'dia': 13.72, 'od': 14.22, 'weight': 806.1, 'resistance': 0.223, 'strands': 1665},
                -2: {'dia': 12.07, 'od': 12.83, 'weight': 642.1, 'resistance': 0.279, 'strands': 1330},
                0: {'dia': 10.80, 'od': 11.43, 'weight': 511.5, 'resistance': 0.354, 'strands': 1045},
                1: {'dia':  9.65, 'od': 10.36, 'weight': 405.4, 'resistance': 0.456, 'strands': 817},
                2: {'dia':  8.64, 'od':  9.25, 'weight': 331.5, 'resistance': 0.558, 'strands': 665},
                4: {'dia':  6.68, 'od':  7.32, 'weight': 209.9, 'resistance': 0.866, 'strands': 133},
                6: {'dia':  5.28, 'od':  5.82, 'weight': 131.1, 'resistance': 1.37, 'strands': 133},
                8: {'dia':  4.22, 'od':  4.78, 'weight': 85.50, 'resistance': 2.16, 'strands': 133},
                10: {'dia':  2.79, 'od':  3.23, 'weight': 46.40, 'resistance': 3.90, 'strands': 37},
                12: {'dia':  2.22, 'od':  2.67, 'weight': 29.20, 'resistance': 6.23, 'strands': 37},
                14: {'dia':  1.74, 'od':  2.18, 'weight': 18.60, 'resistance': 9.45, 'strands': 19},
                16: {'dia':  1.38, 'od':  1.85, 'weight': 12.70, 'resistance': 14.80, 'strands': 19},
                18: {'dia':  1.23, 'od':  1.65, 'weight': 9.90, 'resistance': 19.00, 'strands': 19},
                20: {'dia':  0.98, 'od':  1.40, 'weight': 6.70, 'resistance': 30.10, 'strands': 19},
                22: {'dia':  0.77, 'od':  1.19, 'weight': 4.40, 'resistance': 49.50, 'strands': 19},
                24: {'dia':  0.62, 'od':  1.07, 'weight': 3.00, 'resistance': 79.70, 'strands': 19},
                26: {'dia':  0.49, 'od':  0.94, 'weight': 2.10, 'resistance': 126.00, 'strands': 19},
            }
        },
        'M22759/87': {
            'start': -4,
            'stop': 27,
            'step': 1,
            'con_plate': 'Ni/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                -4: {'dia': 15.37, 'od': 16.00, 'weight': 1012.9, 'resistance': 0.177, 'strands': 2109},
                -3: {'dia': 13.72, 'od': 14.22, 'weight': 806.1, 'resistance': 0.233, 'strands': 1665},
                -2: {'dia': 12.09, 'od': 12.83, 'weight': 642.1, 'resistance': 0.292, 'strands': 1330},
                0: {'dia': 10.80, 'od': 11.43, 'weight': 511.5, 'resistance': 0.371, 'strands': 1045},
                1: {'dia':  9.65, 'od': 10.36, 'weight': 405.4, 'resistance': 0.472, 'strands': 817},
                2: {'dia':  8.64, 'od':  9.25, 'weight': 331.5, 'resistance': 0.581, 'strands': 665},
                4: {'dia':  6.81, 'od':  7.32, 'weight': 209.9, 'resistance': 0.902, 'strands': 133},
                6: {'dia':  5.38, 'od':  5.82, 'weight': 131.1, 'resistance': 1.43, 'strands': 133},
                8: {'dia':  4.29, 'od':  4.78, 'weight': 85.50, 'resistance': 2.28, 'strands': 133},
                10: {'dia':  2.84, 'od':  3.23, 'weight': 46.60, 'resistance': 4.07, 'strands': 37},
                12: {'dia':  2.27, 'od':  2.67, 'weight': 29.80, 'resistance': 6.49, 'strands': 37},
                14: {'dia':  1.76, 'od':  2.18, 'weight': 18.60, 'resistance': 9.84, 'strands': 19},
                16: {'dia':  1.41, 'od':  1.85, 'weight': 12.70, 'resistance': 15.60, 'strands': 19},
                18: {'dia':  1.25, 'od':  1.65, 'weight': 9.90, 'resistance': 20.00, 'strands': 19},
                20: {'dia':  1.00, 'od':  1.40, 'weight': 6.80, 'resistance': 32.00, 'strands': 19},
                22: {'dia':  0.80, 'od':  1.19, 'weight': 4.40, 'resistance': 52.50, 'strands': 19},
                24: {'dia':  0.62, 'od':  1.07, 'weight': 3.00, 'resistance': 85.00, 'strands': 19},
                26: {'dia':  0.52, 'od':  0.94, 'weight': 2.20, 'resistance': 138.00, 'strands': 19},
            }
        },
        'M22759/88': {
            'start': -4,
            'stop': 27,
            'step': 1,
            'con_plate': 'Sn/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                -4: {'dia': 15.37, 'od': 16.00, 'weight': 1012.9, 'resistance': 0.184, 'strands': 2109},
                -3: {'dia': 13.72, 'od': 14.22, 'weight': 806.1, 'resistance': 0.233, 'strands': 1665},
                -2: {'dia': 12.07, 'od': 12.83, 'weight': 642.1, 'resistance': 0.298, 'strands': 1330},
                0: {'dia': 10.80, 'od': 11.43, 'weight': 511.5, 'resistance': 0.380, 'strands': 1045},
                1: {'dia':  9.65, 'od': 10.36, 'weight': 408.4, 'resistance': 0.489, 'strands': 817},
                2: {'dia':  8.64, 'od':  9.25, 'weight': 331.5, 'resistance': 0.600, 'strands': 665},
                4: {'dia':  6.81, 'od':  7.32, 'weight': 209.9, 'resistance': 0.918, 'strands': 133},
                6: {'dia':  5.38, 'od':  5.82, 'weight': 131.1, 'resistance': 1.46, 'strands': 133},
                8: {'dia':  4.29, 'od':  4.78, 'weight': 85.50, 'resistance': 2.30, 'strands': 133},
                10: {'dia':  2.84, 'od':  3.23, 'weight': 46.60, 'resistance': 4.13, 'strands': 37},
                12: {'dia':  2.27, 'od':  2.67, 'weight': 29.80, 'resistance': 6.63, 'strands': 37},
                14: {'dia':  1.76, 'od':  2.18, 'weight': 19.20, 'resistance': 10.00, 'strands': 19},
                16: {'dia':  1.41, 'od':  1.85, 'weight': 12.60, 'resistance': 15.80, 'strands': 19},
                18: {'dia':  1.25, 'od':  1.65, 'weight': 9.90, 'resistance': 20.40, 'strands': 19},
                20: {'dia':  1.00, 'od':  1.40, 'weight': 6.70, 'resistance': 32.40, 'strands': 19},
                22: {'dia':  0.80, 'od':  1.19, 'weight': 4.40, 'resistance': 53.10, 'strands': 19},
                24: {'dia':  0.62, 'od':  1.07, 'weight': 3.00, 'resistance': 85.90, 'strands': 19},
                26: {'dia':  0.52, 'od':  0.94, 'weight': 2.10, 'resistance': 135.00, 'strands': 19},
            }
        },
        'M22759/89': {
            'start': 20,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                20: {'dia': 1.00, 'od': 1.40, 'weight': 6.80, 'resistance': 35.10, 'strands': 19},
                22: {'dia': 0.80, 'od': 1.19, 'weight': 4.40, 'resistance': 57.40, 'strands': 19},
                24: {'dia': 0.62, 'od': 1.07, 'weight': 3.00, 'resistance': 93.20, 'strands': 19},
                26: {'dia': 0.52, 'od': 0.94, 'weight': 2.30, 'resistance': 185.00, 'strands': 19},
            }
        },
        'M22759/90': {
            'start': 20,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                20: {'dia': 1.03, 'od': 1.40, 'weight': 6.80, 'resistance': 37.40, 'strands': 19},
                22: {'dia': 0.80, 'od': 1.19, 'weight': 4.40, 'resistance': 61.00, 'strands': 19},
                24: {'dia': 0.65, 'od': 1.07, 'weight': 3.00, 'resistance': 98.70, 'strands': 19},
                26: {'dia': 0.52, 'od': 0.94, 'weight': 2.30, 'resistance': 191.00, 'strands': 19},
            }
        },
        'M22759/91': {
            'start': 10,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape (light weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                10: {'dia': 2.79, 'od': 3.12, 'weight': 45.40, 'resistance': 3.90, 'strands': 37},
                12: {'dia': 2.22, 'od': 2.54, 'weight': 29.00, 'resistance': 6.23, 'strands': 37},
                14: {'dia': 1.74, 'od': 2.03, 'weight': 18.70, 'resistance': 9.45, 'strands': 19},
                16: {'dia': 1.38, 'od': 1.70, 'weight': 12.20, 'resistance': 14.80, 'strands': 19},
                18: {'dia': 1.23, 'od': 1.52, 'weight': 9.80, 'resistance': 19.00, 'strands': 19},
                20: {'dia': 0.98, 'od': 1.30, 'weight': 6.50, 'resistance': 30.10, 'strands': 19},
                22: {'dia': 0.77, 'od': 1.09, 'weight': 4.20, 'resistance': 49.50, 'strands': 19},
                24: {'dia': 0.62, 'od': 0.97, 'weight': 2.80, 'resistance': 79.70, 'strands': 19},
                26: {'dia': 0.49, 'od': 0.86, 'weight': 2.00, 'resistance': 126.00, 'strands': 19},
            }
        },
        'M22759/92': {
            'start': 10,
            'stop': 27,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'PTFE/polyimide/PTFE tape and PTFE tape (light weight)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                10: {'dia': 2.84, 'od': 3.12, 'weight': 45.40, 'resistance': 4.07, 'strands': 37},
                12: {'dia': 2.27, 'od': 2.54, 'weight': 29.00, 'resistance': 6.49, 'strands': 37},
                14: {'dia': 1.76, 'od': 2.03, 'weight': 18.70, 'resistance': 9.84, 'strands': 19},
                16: {'dia': 1.41, 'od': 1.70, 'weight': 12.20, 'resistance': 15.60, 'strands': 19},
                18: {'dia': 1.25, 'od': 1.52, 'weight': 9.80, 'resistance': 20.00, 'strands': 19},
                20: {'dia': 1.00, 'od': 1.30, 'weight': 6.50, 'resistance': 32.00, 'strands': 19},
                22: {'dia': 0.80, 'od': 1.09, 'weight': 4.20, 'resistance': 52.50, 'strands': 19},
                24: {'dia': 0.62, 'od': 0.97, 'weight': 2.80, 'resistance': 85.00, 'strands': 19},
                26: {'dia': 0.52, 'od': 0.86, 'weight': 2.00, 'resistance': 138.00, 'strands': 19},
            }
        },
    }

    color_mapping = {
        0: 'Black',
        1: 'Brown',
        2: 'Red',
        3: 'Orange',
        4: 'Yellow',
        5: 'Green',
        6: 'Blue',
        7: 'Violet',
        8: 'Gray',
        9: 'White',
    }

    pn_template = '{series}-{awg}-{primary}{secondary}'
    colors = list(color_mapping.values())
    values = []

    for family, wire_data in mapping.items():
        plating = wire_data['con_plate']
        min_temp = wire_data['min_temp']
        max_temp = wire_data['max_temp']
        volts = wire_data['volts']
        material = wire_data['material']

        for awg in range(wire_data['start'], wire_data['stop'], wire_data['step']):
            if awg not in wire_data['data']:
                continue

            entry = wire_data['data'][awg]
            dia = entry['dia']
            od_mm = entry['od']
            weight = entry['weight'] * 1000.0
            resistance = entry['resistance']
            strands = entry['strands']
            mm_2 = awg_to_mm2(awg, strands)

            for p_id, color in enumerate(colors):
                part_number = pn_template.format(series=family, awg=awg, primary=p_id, secondary='')
                description = (
                    f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]} '
                    f'milspec single conductor wire'
                )

                values.append(dict(
                    part_number=part_number,
                    description=description,
                    mfg='TE Connectivity',
                    family='Milspec',
                    series=family,
                    color=color,
                    image=None,
                    datasheet=None,
                    cad=None,
                    min_temp=min_temp,
                    max_temp=max_temp,
                    material=material,
                    stripe_color=None,
                    core_material=plating,
                    num_conductors=1,
                    shielded=0,
                    tpi=0.0,
                    wire_size_dia=dia,
                    wire_size_cross=mm_2,
                    wire_size_awg=awg,
                    od_mm=od_mm,
                    weight_1km=weight,
                    resistance_1km=resistance,
                    strands=strands,
                    volts=volts,
                ))

                for s_id, stripe_color in enumerate(colors):
                    if stripe_color == color:
                        continue

                    values.append(dict(
                        part_number=part_number + str(s_id),
                        description=(
                            f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]}/{color_mapping[s_id]} '
                            f'milspec single conductor wire'
                        ),
                        mfg='TE Connectivity',
                        family='Milspec',
                        series=family,
                        color=color,
                        image=None,
                        datasheet=None,
                        cad=None,
                        min_temp=min_temp,
                        max_temp=max_temp,
                        material=material,
                        stripe_color=stripe_color,
                        core_material=plating,
                        num_conductors=1,
                        shielded=0,
                        tpi=0.0,
                        wire_size_dia=dia,
                        wire_size_cross=mm_2,
                        wire_size_awg=awg,
                        od_mm=od_mm,
                        weight_1km=weight,
                        resistance_1km=resistance,
                        strands=strands,
                        volts=volts,
                    ))

    return values


# ---------------------------------------------------------------------------
# M27500 cable generator
# ---------------------------------------------------------------------------

# Circumscribed circle multipliers per conductor count (MIL-DTL-27500)
_CONDUCTOR_MULTIPLIER = {1: 1.000, 2: 2.000, 3: 2.155, 4: 2.414,
                         5: 2.701, 6: 3.000, 7: 3.000, 8: 3.613}

# MIL-STD-681 colour codes, in code order (the same table _build_wires uses for the single wires)
_MIL_COLORS = {0: 'Black', 1: 'Brown', 2: 'Red', 3: 'Orange', 4: 'Yellow',
               5: 'Green', 6: 'Blue', 7: 'Violet', 8: 'Gray', 9: 'White'}

# Twists per inch of a multi-conductor M27500 cable: 1. A seller's listing for M27500-20SB2U00 reads "1 twist per inch
# as per MIL standards" (the spec itself was not available). This replaces a table of per-AWG values that was a guess.
_M27500_TPI = 1.0

# Shield braid wall thickness added to bundle diameter (mm)
# Back-calculated from spec tabulated 1-conductor data
_SHIELD_WALL_MM = 0.635

# Jacket wall thicknesses added to diameter (mm)
_JACKET_WALL_MM = {'06': 0.508,  # PTFE tape, white
                   '14': 0.635,  # ETFE extruded, white
                   '05': 0.635}  # FEP extruded, clear


# Jacket material densities (g/cm³)
_JACKET_DENSITY = {'06': 2.20,    # PTFE
                   '14': 1.75,    # ETFE
                   '05': 2.15}    # FEP


# Jacket descriptions
_JACKET_DESC = {'06': 'PTFE tape white 260°C',
                '14': 'ETFE extruded white 150°C',
                '05': 'FEP extruded clear 200°C'}

# Jacket colour, by jacket code (matches _JACKET_DESC; the FEP jacket is clear, the closest colour row is "Natural").
# A cable with no jacket has the colour "None": a "None" colour means no outer jacket (TWISTED_WIRE_DESIGN.md).
_JACKET_COLOR = {'06': 'White', '14': 'White', '05': 'Natural'}
_NO_JACKET_COLOR = 'None'

# The colour of each conductor of an M27500 cable is set by the colour-code character after "M27500" (source: the
# Wiremasters M27500 guide, a secondary source; the standard itself was not available). Conductor 1 comes first.
#  "-"  (the default, no letter), the PREFERRED method, NEMA WC 27500 Table A-1: every conductor is WHITE, and
#       conductors 2 and up carry a stripe in this order; conductor 1 has no stripe.
#  "A", Optional Method A, Table A-1: the same sequence, but as SOLID insulation colours (conductor 1 white).
# Only the first 8 positions are used (the cable generator stops at 8 conductors).
_CABLE_STRIPE_COLORS = ['Blue', 'Orange', 'Green', 'Red', 'Black', 'Yellow', 'Violet']
_CABLE_SOLID_COLORS = ['White'] + _CABLE_STRIPE_COLORS

# Jacket max temp limits (°C)
_JACKET_MAX_TEMP = {'06': 260, '14': 150, '05': 200}

# Shield materials: code -> (description, plating, max_temp_c)
_SHIELD_MATERIALS = {'T': ('Tin-plated copper braid',    'Sn/Cu', 150),
                     'S': ('Silver-plated copper braid', 'Ag/Cu', 200),
                     'N': ('Nickel-plated copper braid', 'Ni/Cu', 260)}

# Copper braid density (g/cm³)
_COPPER_DENSITY = 8.96

# Shield braid coverage fraction
_SHIELD_COVERAGE = 0.85

# M27500 component wire type codes (from spec)
_WIRE_TYPE_CODE = {'M22759/5':  'VA', 'M22759/6':  'WA', 'M22759/7':  'SA',
                   'M22759/8':  'TA', 'M22759/9':  'LE', 'M22759/10': 'LH',
                   'M22759/11': 'RC', 'M22759/12': 'RE', 'M22759/16': 'TE',
                   'M22759/17': 'TF', 'M22759/18': 'TG', 'M22759/19': 'TH',
                   'M22759/20': 'TK', 'M22759/21': 'TL', 'M22759/22': 'TM',
                   'M22759/23': 'TN', 'M22759/28': 'JB', 'M22759/29': 'JC',
                   'M22759/30': 'JD', 'M22759/31': 'JE', 'M22759/32': 'SB',
                   'M22759/33': 'SC', 'M22759/43': 'SP', 'M22759/44': 'SR', 'M22759/80': 'WB',
                   'M22759/81': 'WC', 'M22759/82': 'WE', 'M22759/83': 'WF',
                   'M22759/84': 'WG', 'M22759/85': 'WH', 'M22759/86': 'WJ',
                   'M22759/87': 'WK', 'M22759/88': 'WL', 'M22759/89': 'WM',
                   'M22759/90': 'WN', 'M22759/91': 'WP', 'M22759/92': 'WR'}


def _shield_weight_1km(bundle_od_mm: float, shield_code: str) -> float:  # NOQA
    """
    Estimate shield braid weight in kg/km.

    Models the braid as a thin cylindrical shell of copper at the given
    coverage fraction and wall thickness.

    volume_per_km = π × bundle_od_mm × shield_wall_mm × coverage × 1e6 mm³/km
                    converted to cm³: ÷ 1000
    weight = volume_cm³ × density_g_cm3 ÷ 1000  → kg
    """
    od_cm = bundle_od_mm / 10.0
    wall_cm = _SHIELD_WALL_MM / 10.0
    volume_cm3_per_km = math.pi * od_cm * wall_cm * _SHIELD_COVERAGE * 1e5
    return volume_cm3_per_km * _COPPER_DENSITY / 1000.0


def _jacket_weight_1km(shield_od_mm: float, jacket_code: str) -> float:
    """
    Estimate jacket weight in kg/km.

    Models the jacket as a cylindrical shell.

    volume_per_km = π × shield_od_mm × jacket_wall_mm × 1e6 mm³/km ÷ 1000 → cm³
    weight = volume_cm³ × density ÷ 1000 → kg
    """
    od_cm = shield_od_mm / 10.0
    wall_cm = _JACKET_WALL_MM[jacket_code] / 10.0
    volume_cm3_per_km = math.pi * od_cm * wall_cm * 1e5
    return volume_cm3_per_km * _JACKET_DENSITY[jacket_code] / 1000.0


def _twist_length_factor(component_od_mm: float, tpi: float) -> float:
    """
    Calculate the conductor length factor due to twisting.

    The conductor follows a helix of diameter = component_od_mm and
    pitch = 1/TPI inches = 25.4/TPI mm.

    For one full turn:
        helix_circumference = π × component_od_mm
        pitch               = 25.4 / tpi  (mm per turn)
        length_per_turn     = sqrt(pitch² + helix_circumference²)
        straight_per_turn   = pitch

    factor = length_per_turn / pitch
           = sqrt(1 + (π × component_od_mm × tpi / 25.4)²)
    """
    if tpi == 0.0:
        return 1.0
    helix_turns_per_mm = tpi / 25.4
    return math.sqrt(1.0 + (math.pi * component_od_mm * helix_turns_per_mm) ** 2)


def _bundle_od_mm(component_od_mm: float, num_conductors: int) -> float:
    """Circumscribed bundle OD from component wire OD and conductor count."""
    return component_od_mm * _CONDUCTOR_MULTIPLIER[num_conductors]


def _assembly_od_mm(component_od_mm: float, num_conductors: int,
                    shielded: bool, jacket_code: str | None) -> float:

    """Full assembly OD in mm."""
    od = _bundle_od_mm(component_od_mm, num_conductors)
    if shielded:
        od += _SHIELD_WALL_MM
    if jacket_code:
        od += _JACKET_WALL_MM[jacket_code]
    return round(od, 4)


def _assembly_weight_1km(component_od_mm: float, component_weight_1km: float,
                         num_conductors: int, twist_factor: float, shielded: bool,
                         jacket_code: str | None) -> float:

    """Total cable assembly weight in kg/km."""
    conductor_weight = component_weight_1km * num_conductors * twist_factor
    bundle_od = _bundle_od_mm(component_od_mm, num_conductors)

    shield_weight = 0.0
    shield_od = bundle_od
    if shielded:
        # same geometry for all shield types
        shield_weight = _shield_weight_1km(bundle_od, 'S')
        shield_od = bundle_od + _SHIELD_WALL_MM

    jacket_weight = 0.0
    if jacket_code:
        jacket_weight = _jacket_weight_1km(shield_od, jacket_code)

    return round(conductor_weight + shield_weight + jacket_weight, 4)


def _assembly_resistance_1km(component_resistance_1km: float,
                             twist_factor: float) -> float:

    """Single conductor resistance in Ω/km accounting for twist length."""
    return round(component_resistance_1km * twist_factor, 4)


def _max_temp(component_max_temp: int, shield_code: str | None,
              jacket_code: str | None) -> int:

    """Assembly max temp is the minimum of all constituent material limits."""
    temps = [component_max_temp]
    if shield_code:
        temps.append(_SHIELD_MATERIALS[shield_code][2])
    if jacket_code:
        temps.append(_JACKET_MAX_TEMP[jacket_code])
    return min(temps)


def _conductor_entry(cable: dict, wire: dict, solid: bool = False) -> dict:
    """The conductors of a multi-conductor cable, for ``wire_conductors.json``.

    One entry per CABLE, not per conductor, because every conductor of an M27500 cable is the same component
    wire and only the colour differs: the fields they share are in ``common`` and ``conductors`` lists one item per
    conductor in order (its position is its ``idx``), holding what is specific to it. An item may also name any
    field of ``common`` to override it. ``builder/create_database/wire_conductors.py`` expands it into one
    ``wire_conductors`` row per conductor. ``wire`` is the cable's part number; ``wire`` here is the component
    wire (an M22759 entry) the cable is built from.
    """
    return dict(
        wire=cable['part_number'],
        common=dict(
            core_material=wire['core_material'], material=wire['material'],
            wire_size_dia=wire['wire_size_dia'], wire_size_cross=wire['wire_size_cross'],
            wire_size_awg=wire['wire_size_awg'], strands=wire['strands'], od_mm=wire['od_mm'],
            resistance_1km=cable['resistance_1km']),
        conductors=_cable_conductor_looks(cable['num_conductors'], solid))


def _cable_conductor_looks(num_conductors: int, solid: bool) -> list[dict]:
    """The colour and stripe of each conductor of an M27500 cable: colour code "-" (white, with a stripe from the
    second conductor on) or, when ``solid``, colour code "A" (solid colours)."""
    if solid:
        return [dict(color=_CABLE_SOLID_COLORS[idx], stripe_color=None) for idx in range(num_conductors)]

    return [dict(color='White', stripe_color=None if idx == 0 else _CABLE_STRIPE_COLORS[idx - 1])
            for idx in range(num_conductors)]


def _build_cables(wire_data: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Generate M27500 shielded/twisted cable variants from M22759 component wire data.

    For each component wire AWG entry this generates:
      - Untwisted unshielded unjacketed          (1 variant)
      - Untwisted shielded+jacketed              (3 shields × 3 jackets = 9 variants)
      - Twisted   unshielded unjacketed          (1 variant)
      - Twisted   shielded+jacketed              (9 variants)

    Per conductor count 1–8.  Twisted variants only apply to num_conductors >= 2.

    Parameters
    ----------
    wire_data : list of dicts as returned by _build_wires(), one entry per
                unique (family, awg) combination (colour/stripe duplicates
                are ignored — pass de-duped data or the function de-dupes
                internally).
    """

    shield_jacket_combos = [(shield_code, jacket_code)
                            for shield_code in _SHIELD_MATERIALS
                            for jacket_code in _JACKET_WALL_MM]

    # De-duplicate on (family, awg) — we only need one row per wire size
    seen = set()

    unique_wires = []
    for w in wire_data:
        key = (w['series'], w['wire_size_awg'])

        if key not in seen:
            seen.add(key)
            unique_wires.append(w)

    values = []
    conductors = []

    for wire in unique_wires:
        series = wire['series']
        awg = wire['wire_size_awg']
        wire_code = _WIRE_TYPE_CODE.get(series, series)
        component_od = wire['od_mm']  # insulated wire OD from M22759 data
        comp_weight = wire['weight_1km']  # kg/km for one conductor
        comp_res = wire['resistance_1km']  # Ω/km for one conductor
        comp_strands = wire['strands']
        comp_mm2 = wire['wire_size_cross']
        comp_dia = wire['wire_size_dia']
        comp_min_t = wire['min_temp']
        comp_max_t = wire['max_temp']
        comp_volts = wire['volts']
        comp_mat = wire['material']
        comp_plate = wire['core_material']
        tpi = _M27500_TPI

        # Twist factor uses the component wire OD as the helix diameter
        twist_factor = _twist_length_factor(component_od, tpi)

        for num_conductors in range(1, 9):
            # Every cable of 2 or more conductors is twisted (cabled); a single conductor has nothing to twist. The part
            # number says nothing about it: M27500 has no twist code, so there is one cable per number, not a twisted
            # and an untwisted one.
            twist_options = [num_conductors > 1]
            first_cable = len(values)
            first_conductors = len(conductors)

            for twisted in twist_options:
                if twisted:
                    tf = twist_factor
                    effective_tpi = tpi
                else:
                    tf = 1.0
                    effective_tpi = 0.0

                # --- Unshielded, unjacketed ---
                # One conductor with no shield and no jacket is not a cable, it is the plain wire again (already
                # generated from its M22759 sheet), so M27500 has the unshielded, unjacketed form from 2 conductors up.
                if num_conductors > 1:
                    od = _assembly_od_mm(
                        component_od, num_conductors, False, None)

                    weight = _assembly_weight_1km(
                        component_od, comp_weight, num_conductors, tf, False, None)

                    resistance = _assembly_resistance_1km(comp_res, tf)
                    max_t = _max_temp(comp_max_t, None, None)

                    pn = f'M27500-{awg}{wire_code}{num_conductors}U00'

                    desc = (f'{awg}AWG {num_conductors}-conductor '
                            f'{"twisted " if twisted else ""}'
                            f'unshielded unjacketed {series} milspec cable')

                    values.append(dict(
                        part_number=pn, description=desc, mfg='TE Connectivity', family='M27500',
                        series=series, image=None, datasheet=None, color=_NO_JACKET_COLOR,
                        cad=None, min_temp=comp_min_t, max_temp=max_t, material=comp_mat,
                        core_material=comp_plate, num_conductors=num_conductors,
                        shielded=0, tpi=effective_tpi, wire_size_dia=comp_dia,
                        wire_size_cross=comp_mm2, wire_size_awg=awg, od_mm=od,
                        weight_1km=weight, resistance_1km=resistance, strands=comp_strands,
                        volts=comp_volts))
                    conductors.append(_conductor_entry(values[-1], wire))

                # --- Shielded + jacketed combos ---
                for shield_code, jacket_code in shield_jacket_combos:
                    shield_desc, shield_plate, _ = _SHIELD_MATERIALS[shield_code]
                    od = _assembly_od_mm(component_od, num_conductors, True, jacket_code)
                    weight = _assembly_weight_1km(
                        component_od, comp_weight, num_conductors, tf, True, jacket_code
                    )
                    resistance = _assembly_resistance_1km(comp_res, tf)
                    max_t = _max_temp(comp_max_t, shield_code, jacket_code)

                    pn = f'M27500-{awg}{wire_code}{num_conductors}{shield_code}{jacket_code}'
                    desc = (f'{awg}AWG {num_conductors}-conductor '
                            f'{"twisted " if twisted else ""}'
                            f'shielded ({shield_desc}) '
                            f'{_JACKET_DESC[jacket_code]} jacketed '
                            f'{series} milspec cable')

                    values.append(dict(
                        part_number=pn, description=desc, mfg='TE Connectivity', family='M27500',
                        series=series, image=None, datasheet=None, color=_JACKET_COLOR[jacket_code],
                        cad=None, min_temp=comp_min_t, max_temp=max_t, material=comp_mat,
                        core_material=comp_plate, num_conductors=num_conductors,
                        shielded=1, tpi=effective_tpi, wire_size_dia=comp_dia,
                        wire_size_cross=comp_mm2, wire_size_awg=awg, od_mm=od,
                        weight_1km=weight, resistance_1km=resistance, strands=comp_strands,
                        volts=comp_volts))
                    if num_conductors > 1:
                        conductors.append(_conductor_entry(values[-1], wire))

            # Colour code "A": the same cables with solid-colour conductors, "M27500A..." instead of "M27500-...".
            # Only from 2 conductors up; with one conductor both codes mean the same white wire.
            if num_conductors > 1:
                for cable, entry in zip(values[first_cable:], conductors[first_conductors:]):
                    solid_pn = 'M27500A' + cable['part_number'][len('M27500-'):]

                    values.append(dict(cable, part_number=solid_pn,
                                       description=cable['description'] + ', solid colour conductors (colour code A)'))
                    conductors.append(dict(entry, wire=solid_pn,
                                           conductors=_cable_conductor_looks(num_conductors, True)))

    return values, conductors


# ---------------------------------------------------------------------------
# Automotive twisted pairs
# ---------------------------------------------------------------------------

# Two conductors of M22759/32 (XL-ETFE) or M22759/18 (thin-wall ETFE), both tin-plated copper, 150 C, twisted together
# with no shield and NO JACKET (colour "None"), so both coloured conductors show. Every combination of two different
# conductor looks is made, where a look is a solid colour or a colour with a stripe.
_PAIR_SERIES = ('M22759/32', 'M22759/18')
_PAIR_AWGS = (20, 22, 24, 26, 28)  # a sheet that lacks a size (/18 stops at 26) just has no pair of it

# Twists per inch. There is no standard for the automotive pair: ISO 11898 does not say, the supplier listings found
# (Interstate Electronics' 20 AWG GXL and TXL pairs) give a lay of 1.0 inch, and a seller's M27500-20SB2U00 listing says
# "1 twist per inch as per MIL standards". Some sellers list 2 TPI for 18 AWG; that is not generated.
_PAIR_TPI = 1.0


def _build_twisted_pairs(wire_data: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Generate unshielded, unjacketed twisted pairs made of M22759/32 and M22759/18 wire, 20 to 28 AWG.

    There is no MIL part number for an arbitrary colour pair (M27500 only has its fixed colour codes), so the numbers
    follow the way sellers number them, with the MIL-STD-681 colour digits (``9`` white, ``6`` blue):

    * both conductors solid:  ``M22759/32-24-5/4-1TPI``  (green and yellow, 1 twist per inch)
    * any conductor striped:  ``M22759/32-18-9-9/6``     (white, and white with a blue stripe: ``base/stripe``)

    The first conductor of a pair is the one with the higher colour digit (white before blue); with the same digit a
    solid one comes before a striped one. Returns the cables and their ``wire_conductors`` entries.
    """

    colors = list(_MIL_COLORS.values())

    # a look is (colour code, stripe code or None). Highest colour first, solid before striped, so the first of a
    # pair is the one a seller would list first: 9 (white), then 9/0 ... 9/8, then 8 (gray) ...
    looks = []
    for p_id in range(len(colors) - 1, -1, -1):
        looks.append((p_id, None))
        looks.extend((p_id, s_id) for s_id in range(len(colors)) if s_id != p_id)

    def look_code(look):
        if look[1] is None:
            return str(look[0])
        return f'{look[0]}/{look[1]}'

    def look_name(look):
        if look[1] is None:
            return colors[look[0]]
        return f'{colors[look[0]]}/{colors[look[1]]}'

    values = []
    conductors = []

    for series in _PAIR_SERIES:
        components = {}
        for wire in wire_data:
            if wire['series'] == series and wire['wire_size_awg'] in _PAIR_AWGS:
                components.setdefault(wire['wire_size_awg'], wire)

        for awg in _PAIR_AWGS:
            if awg not in components:
                continue

            wire = components[awg]
            component_od = wire['od_mm']
            twist_factor = _twist_length_factor(component_od, _PAIR_TPI)
            od = _assembly_od_mm(component_od, 2, False, None)
            weight = _assembly_weight_1km(component_od, wire['weight_1km'], 2, twist_factor, False, None)
            resistance = _assembly_resistance_1km(wire['resistance_1km'], twist_factor)

            for look_1, look_2 in itertools.combinations(looks, 2):
                if look_1[1] is None and look_2[1] is None:
                    pn = f'{series}-{awg}-{look_1[0]}/{look_2[0]}-{_PAIR_TPI:g}TPI'
                else:
                    pn = f'{series}-{awg}-{look_code(look_1)}-{look_code(look_2)}'

                values.append(dict(
                    part_number=pn,
                    description=(f'{awg}AWG unshielded unjacketed twisted pair of {series} wire, '
                                 f'{look_name(look_1)} + {look_name(look_2)}, {_PAIR_TPI:g} twist per inch'),
                    mfg='TE Connectivity', family='Twisted Pair', series=series, image=None, datasheet=None,
                    color=_NO_JACKET_COLOR, cad=None, min_temp=wire['min_temp'], max_temp=wire['max_temp'],
                    material=wire['material'], core_material=wire['core_material'], num_conductors=2, shielded=0,
                    tpi=_PAIR_TPI, wire_size_dia=wire['wire_size_dia'], wire_size_cross=wire['wire_size_cross'],
                    wire_size_awg=awg, od_mm=od, weight_1km=weight, resistance_1km=resistance,
                    strands=wire['strands'], volts=wire['volts']))

                conductors.append(dict(
                    wire=pn,
                    common=dict(
                        core_material=wire['core_material'], material=wire['material'],
                        wire_size_dia=wire['wire_size_dia'], wire_size_cross=wire['wire_size_cross'],
                        wire_size_awg=awg, strands=wire['strands'], od_mm=component_od,
                        resistance_1km=resistance),
                    conductors=[dict(color=colors[look[0]],
                                     stripe_color=None if look[1] is None else colors[look[1]])
                                for look in (look_1, look_2)]))

    return values, conductors


def check_for_dupes(all_wires):
    """Remove from te/wires.json (relative to the working directory) any part the generator now makes itself."""
    pns = set(part['part_number'] for part in all_wires)

    with open('te/wires.json', 'r') as file:
        data = json.loads(file.read())

    output = []
    for prt in data:
        part_num = prt['part_number']
        if part_num in pns:
            continue
        pns.add(part_num)
        output.append(prt)

    with open('te/wires.json', 'w') as file:
        file.write(json.dumps(output, indent=4))


def _model_file_name(wire: dict) -> str:
    """The file a wire is written to: one file per wire MODEL, so no file gets huge.

    A single wire goes in its slash sheet's file (``M22759-32``), the M27500 cables built from that wire in
    ``M27500-M22759-32``, and the twisted pairs in one file per size (``TP-M22759-32-22AWG``).
    """
    series = wire['series'].replace('/', '-')

    if wire['family'] == 'M27500':
        return f'M27500-{series}'

    if wire['family'] == 'Twisted Pair':
        return f"TP-{series}-{wire['wire_size_awg']}AWG"

    return series


def write_split(all_wires: list[dict], all_conductors: list[dict], out_dir: str) -> None:
    """Write ``<out_dir>/wires/<model>.json`` and ``<out_dir>/wire_conductors/<model>.json``.

    The conductors of a cable go in the file with the same name as the cable's, so the two folders mirror each other.
    The two folders are replaced, so a model that is no longer generated does not linger.
    """
    wires_dir = os.path.join(out_dir, 'wires')
    conductors_dir = os.path.join(out_dir, 'wire_conductors')

    file_of = {wire['part_number']: _model_file_name(wire) for wire in all_wires}

    for folder in (wires_dir, conductors_dir):
        os.makedirs(folder, exist_ok=True)

        for file_name in os.listdir(folder):
            if file_name.endswith('.json'):
                os.remove(os.path.join(folder, file_name))

    by_file = {}
    for wire in all_wires:
        by_file.setdefault(file_of[wire['part_number']], []).append(wire)

    for name, wires in by_file.items():
        with open(os.path.join(wires_dir, f'{name}.json'), 'w') as f:
            f.write(json.dumps(wires, indent=4))

    conductors_by_file = {}
    for entry in all_conductors:
        conductors_by_file.setdefault(file_of[entry['wire']], []).append(entry)

    for name, entries in conductors_by_file.items():
        with open(os.path.join(conductors_dir, f'{name}.json'), 'w') as f:
            f.write(json.dumps(entries, separators=(',', ':')))

    print(f'{len(all_wires)} wires in {len(by_file)} files, {len(all_conductors)} cables with conductors '
          f'in {len(conductors_by_file)} files, under {out_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the milspec wires, cables and twisted pairs.')
    parser.add_argument(
        '--out', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Universal'),
        help='Folder that gets the wires/ and wire_conductors/ folders (default: the Universal folder of this repo).')
    args = parser.parse_args()

    wires = _build_wires()
    cables, cable_conductors = _build_cables(wires)
    pairs, pair_conductors = _build_twisted_pairs(wires)

    all_wires = wires + cables + pairs

    check_for_dupes(all_wires)
    write_split(all_wires, cable_conductors + pair_conductors, args.out)
