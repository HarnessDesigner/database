import json
import math


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
                    mfg='TE',
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
                        mfg='TE',
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

# Typical twists per inch by AWG for twisted variants
_AWG_TPI = {8:  0.8, 10: 1.0, 12: 1.2, 14: 1.4, 16: 1.6,
            18: 1.8, 20: 2.0, 22: 2.5, 24: 3.0, 26: 3.5, 28: 4.0}

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
                   'M22759/30': 'JD', 'M22759/31': 'JE', 'M22759/80': 'WB',
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


def _build_cables(wire_data: list[dict]) -> list[dict]:
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
        tpi = _AWG_TPI.get(awg, 2.0)

        # Twist factor uses the component wire OD as the helix diameter
        twist_factor = _twist_length_factor(component_od, tpi)

        for num_conductors in range(1, 9):
            # Twisted only makes sense for 2+ conductors
            if num_conductors == 1:
                twist_options = [False]
            else:
                twist_options = [False, True]

            for twisted in twist_options:
                if twisted:
                    tf = twist_factor
                    effective_tpi = tpi
                else:
                    tf = 1.0
                    effective_tpi = 0.0

                # --- Unshielded, unjacketed ---
                od = _assembly_od_mm(
                    component_od, num_conductors, False, None)

                weight = _assembly_weight_1km(
                    component_od, comp_weight, num_conductors, tf, False, None)

                resistance = _assembly_resistance_1km(comp_res, tf)
                max_t = _max_temp(comp_max_t, None, None)

                pn = (f'M27500-{awg}{wire_code}{num_conductors}'
                      f'U00{"T" if twisted else ""}')

                desc = (f'{awg}AWG {num_conductors}-conductor '
                        f'{"twisted " if twisted else ""}'
                        f'unshielded unjacketed {series} milspec cable')

                values.append(dict(
                    part_number=pn, description=desc, mfg='TE', family='M27500',
                    series=series, image=None, datasheet=None, color='Vanilla',
                    cad=None, min_temp=comp_min_t, max_temp=max_t, material=comp_mat,
                    core_material=comp_plate, num_conductors=num_conductors,
                    shielded=0, tpi=effective_tpi, wire_size_dia=comp_dia,
                    wire_size_cross=comp_mm2, wire_size_awg=awg, od_mm=od,
                    weight_1km=weight, resistance_1km=resistance, strands=comp_strands,
                    volts=comp_volts))

                # --- Shielded + jacketed combos ---
                for shield_code, jacket_code in shield_jacket_combos:
                    shield_desc, shield_plate, _ = _SHIELD_MATERIALS[shield_code]
                    od = _assembly_od_mm(component_od, num_conductors, True, jacket_code)
                    weight = _assembly_weight_1km(
                        component_od, comp_weight, num_conductors, tf, True, jacket_code
                    )
                    resistance = _assembly_resistance_1km(comp_res, tf)
                    max_t = _max_temp(comp_max_t, shield_code, jacket_code)

                    pn = (f'M27500-{awg}{wire_code}{num_conductors}'
                          f'{shield_code}{jacket_code}{"T" if twisted else ""}')
                    desc = (f'{awg}AWG {num_conductors}-conductor '
                            f'{"twisted " if twisted else ""}'
                            f'shielded ({shield_desc}) '
                            f'{_JACKET_DESC[jacket_code]} jacketed '
                            f'{series} milspec cable')

                    values.append(dict(
                        part_number=pn, description=desc, mfg='TE', family='M27500',
                        series=series, image=None, datasheet=None, color='Vanilla',
                        cad=None, min_temp=comp_min_t, max_temp=max_t, material=comp_mat,
                        core_material=comp_plate, num_conductors=num_conductors,
                        shielded=1, tpi=effective_tpi, wire_size_dia=comp_dia,
                        wire_size_cross=comp_mm2, wire_size_awg=awg, od_mm=od,
                        weight_1km=weight, resistance_1km=resistance, strands=comp_strands,
                        volts=comp_volts))

    return values


def check_for_dupes(all_wires):
    pns = []

    def _iter_parts(pth):
        output = []

        with open(pth, 'r') as file:
            data = json.loads(file.read())

        for prt in data:
            part_num = prt['part_number']
            if part_num in pns:
                continue
            pns.append(part_num)
            output.append(prt)

        with open(pth, 'w') as file:
            file.write(json.dumps(output, indent=4))

    for part in all_wires:
        pn = part['part_number']
        if pn in pns:
            continue

        pns.append(pn)

    _iter_parts('te/wires.json')

    with open('wires.json', 'w') as f:
        f.write(json.dumps(all_wires, indent=4))


if __name__ == '__main__':
    wires = _build_wires()
    cables = _build_cables(wires)

    check_for_dupes(wires + cables)

    print(len(wires))
    print(len(cables))
