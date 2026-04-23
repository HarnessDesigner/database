import json
import math

from decimal import Decimal as _d


def _build_wires():
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
                8: {'dia': 4.11, 'od': 6.48, 'weight': 115.00, 'resistance': 2.16},
                10: {'dia': 2.74, 'od': 4.73, 'weight': 63.30, 'resistance': 3.90},
                12: {'dia': 2.18, 'od': 4.24, 'weight': 46.00, 'resistance': 5.94},
                14: {'dia': 1.70, 'od': 3.81, 'weight': 33.50, 'resistance': 9.45},
                16: {'dia': 1.35, 'od': 3.30, 'weight': 24.70, 'resistance': 14.80},
                18: {'dia': 1.19, 'od': 2.92, 'weight': 19.20, 'resistance': 19.00},
                20: {'dia': 0.97, 'od': 2.54, 'weight': 13.60, 'resistance': 30.10},
                22: {'dia': 0.76, 'od': 2.29, 'weight': 10.10, 'resistance': 49.50},
                24: {'dia': 0.61, 'od': 2.03, 'weight': 7.60, 'resistance': 79.70}
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
                8: {'dia': 4.14, 'od': 6.48, 'weight': 118.00, 'resistance': 2.28},
                10: {'dia': 2.77, 'od': 4.73, 'weight': 64.80, 'resistance': 4.07},
                12: {'dia': 2.18, 'od': 4.24, 'weight': 47.50, 'resistance': 6.20},
                14: {'dia': 1.70, 'od': 3.81, 'weight': 34.70, 'resistance': 9.84},
                16: {'dia': 1.35, 'od': 3.30, 'weight': 25.20, 'resistance': 15.60},
                18: {'dia': 1.19, 'od': 2.92, 'weight': 19.50, 'resistance': 20.00},
                20: {'dia': 0.97, 'od': 2.54, 'weight': 13.90, 'resistance': 32.10},
                22: {'dia': 0.76, 'od': 2.29, 'weight': 10.40, 'resistance': 52.50},
                24: {'dia': 0.61, 'od': 2.03, 'weight': 7.70, 'resistance': 85.00}
            }
        },
        'M22759/7': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with abrasion-resistant mineral fillers',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                8: {'dia': 4.11, 'od': 5.72, 'weight': 101.00, 'resistance': 2.16},
                10: {'dia': 2.74, 'od': 4.11, 'weight': 55.70, 'resistance': 3.90},
                12: {'dia': 2.18, 'od': 3.48, 'weight': 38.30, 'resistance': 5.94},
                14: {'dia': 1.70, 'od': 3.00, 'weight': 25.80, 'resistance': 9.45},
                16: {'dia': 1.35, 'od': 2.67, 'weight': 18.90, 'resistance': 14.80},
                18: {'dia': 1.19, 'od': 2.39, 'weight': 15.20, 'resistance': 19.00},
                20: {'dia': 0.97, 'od': 2.13, 'weight': 10.90, 'resistance': 30.10},
                22: {'dia': 0.76, 'od': 1.91, 'weight': 7.44, 'resistance': 49.50},
                24: {'dia': 0.61, 'od': 1.63, 'weight': 5.51, 'resistance': 79.70}
            }
        },
        'M22759/8': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with abrasion-resistant mineral fillers',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8: {'dia': 4.14, 'od': 5.72, 'weight': 104.00, 'resistance': 2.28},
                10: {'dia': 2.77, 'od': 4.11, 'weight': 57.20, 'resistance': 4.07},
                12: {'dia': 2.18, 'od': 3.48, 'weight': 42.80, 'resistance': 6.20},
                14: {'dia': 1.70, 'od': 3.00, 'weight': 27.00, 'resistance': 9.84},
                16: {'dia': 1.35, 'od': 2.67, 'weight': 19.40, 'resistance': 15.60},
                18: {'dia': 1.19, 'od': 2.39, 'weight': 15.50, 'resistance': 20.00},
                20: {'dia': 0.97, 'od': 2.13, 'weight': 11.20, 'resistance': 32.10},
                22: {'dia': 0.76, 'od': 1.91, 'weight': 7.66, 'resistance': 52.50},
                24: {'dia': 0.61, 'od': 1.63, 'weight': 5.66, 'resistance': 85.00}
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
                8: {'dia': 4.11, 'od': 5.38, 'weight': 97.30, 'resistance': 2.16},
                10: {'dia': 2.74, 'od': 3.68, 'weight': 52.50, 'resistance': 3.90},
                12: {'dia': 2.18, 'od': 3.15, 'weight': 34.70, 'resistance': 5.94},
                14: {'dia': 1.70, 'od': 2.62, 'weight': 24.00, 'resistance': 9.45},
                16: {'dia': 1.35, 'od': 2.21, 'weight': 15.80, 'resistance': 14.80},
                18: {'dia': 1.19, 'od': 2.03, 'weight': 12.90, 'resistance': 19.00},
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 30.10},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 49.50},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 79.70},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 126.00},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 209.00}
            }
        },
        'M22759/10': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8: {'dia': 4.11, 'od': 5.13, 'weight': 98.80, 'resistance': 2.28},
                10: {'dia': 2.74, 'od': 3.48, 'weight': 53.40, 'resistance': 4.07},
                12: {'dia': 2.18, 'od': 2.95, 'weight': 34.80, 'resistance': 6.20},
                14: {'dia': 1.70, 'od': 2.46, 'weight': 24.10, 'resistance': 9.84},
                16: {'dia': 1.35, 'od': 2.11, 'weight': 16.10, 'resistance': 15.60},
                18: {'dia': 1.19, 'od': 1.93, 'weight': 12.90, 'resistance': 20.00},
                20: {'dia': 0.97, 'od': 1.68, 'weight': 9.06, 'resistance': 32.00},
                22: {'dia': 0.76, 'od': 1.47, 'weight': 6.40, 'resistance': 52.50},
                24: {'dia': 0.61, 'od': 1.30, 'weight': 4.66, 'resistance': 85.00},
                26: {'dia': 0.48, 'od': 1.17, 'weight': 3.54, 'resistance': 138.00},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 223.00}
            }
        },
        'M22759/11': {
            'start': 8,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                8: {'dia': 4.11, 'od': 5.23, 'weight': 86.10, 'resistance': 2.16},
                10: {'dia': 2.74, 'od': 3.63, 'weight': 52.00, 'resistance': 3.90},
                12: {'dia': 2.18, 'od': 2.90, 'weight': 35.00, 'resistance': 5.94},
                14: {'dia': 1.70, 'od': 2.34, 'weight': 21.90, 'resistance': 9.45},
                16: {'dia': 1.35, 'od': 1.96, 'weight': 14.30, 'resistance': 14.80},
                18: {'dia': 1.19, 'od': 1.78, 'weight': 11.30, 'resistance': 19.00},
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.66, 'resistance': 30.10},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.12, 'resistance': 49.50},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.59, 'resistance': 79.70},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.59, 'resistance': 126.00},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.82, 'resistance': 209.00}
            }
        },
        'M22759/12': {
            'start': 8,
            'stop': 25,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                8: {'dia': 4.11, 'od': 5.28, 'weight': 87.50, 'resistance': 2.28},
                10: {'dia': 2.74, 'od': 3.63, 'weight': 52.80, 'resistance': 4.07},
                12: {'dia': 2.18, 'od': 2.90, 'weight': 35.70, 'resistance': 6.20},
                14: {'dia': 1.70, 'od': 2.34, 'weight': 22.00, 'resistance': 9.84},
                16: {'dia': 1.35, 'od': 1.96, 'weight': 14.50, 'resistance': 15.60},
                18: {'dia': 1.19, 'od': 1.78, 'weight': 11.40, 'resistance': 20.00},
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.72, 'resistance': 32.00},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.15, 'resistance': 52.50},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.60, 'resistance': 85.00},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.60, 'resistance': 138.00},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.83, 'resistance': 223.00}
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
                -2: {'dia': 11.70, 'od': 14.00, 'weight': 722.00, 'resistance': 0.30},
                -1: {'dia': 10.50, 'od': 12.30, 'weight': 566.00, 'resistance': 0.38},
                1: {'dia': 9.40, 'od': 11.10, 'weight': 437.00, 'resistance': 0.49},
                2: {'dia': 8.38, 'od': 9.96, 'weight': 344.00, 'resistance': 0.60},
                4: {'dia': 6.60, 'od': 8.03, 'weight': 227.00, 'resistance': 0.92},
                6: {'dia': 5.13, 'od': 6.43, 'weight': 144.00, 'resistance': 1.46},
                8: {'dia': 4.11, 'od': 5.13, 'weight': 91.50, 'resistance': 2.30},
                10: {'dia': 2.79, 'od': 3.61, 'weight': 50.60, 'resistance': 4.13},
                12: {'dia': 2.18, 'od': 2.97, 'weight': 32.40, 'resistance': 6.63},
                14: {'dia': 1.70, 'od': 2.41, 'weight': 21.60, 'resistance': 10.00},
                16: {'dia': 1.35, 'od': 2.06, 'weight': 14.40, 'resistance': 15.80},
                18: {'dia': 1.22, 'od': 1.85, 'weight': 11.40, 'resistance': 20.40},
                20: {'dia': 0.97, 'od': 1.57, 'weight': 7.71, 'resistance': 32.40},
                22: {'dia': 0.76, 'od': 1.37, 'weight': 5.24, 'resistance': 53.10},
                24: {'dia': 0.61, 'od': 1.19, 'weight': 3.65, 'resistance': 85.90}
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
                20: {'dia': 0.97, 'od': 1.57, 'weight': 7.38, 'resistance': 35.10},
                22: {'dia': 0.76, 'od': 1.37, 'weight': 5.06, 'resistance': 57.40},
                24: {'dia': 0.61, 'od': 1.19, 'weight': 3.45, 'resistance': 93.20},
                26: {'dia': 0.48, 'od': 1.07, 'weight': 2.49, 'resistance': 147.00}
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
                10: {'dia': 2.79, 'od': 3.48, 'weight': 49.30, 'resistance': 4.13},
                12: {'dia': 2.18, 'od': 2.80, 'weight': 31.30, 'resistance': 6.63},
                14: {'dia': 1.70, 'od': 2.21, 'weight': 20.40, 'resistance': 10.00},
                16: {'dia': 1.35, 'od': 1.83, 'weight': 13.30, 'resistance': 15.80},
                18: {'dia': 1.19, 'od': 1.60, 'weight': 10.30, 'resistance': 20.40},
                20: {'dia': 0.97, 'od': 1.35, 'weight': 6.85, 'resistance': 32.40},
                22: {'dia': 0.76, 'od': 1.14, 'weight': 4.52, 'resistance': 53.10},
                24: {'dia': 0.61, 'od': 0.97, 'weight': 3.01, 'resistance': 85.90},
                26: {'dia': 0.48, 'od': 0.86, 'weight': 2.26, 'resistance': 135.00}
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
                20: {'dia': 0.97, 'od': 1.35, 'weight': 6.62, 'resistance': 35.10},
                22: {'dia': 0.76, 'od': 1.14, 'weight': 4.27, 'resistance': 57.40},
                24: {'dia': 0.61, 'od': 0.97, 'weight': 2.86, 'resistance': 93.20},
                26: {'dia': 0.48, 'od': 0.86, 'weight': 2.02, 'resistance': 147.00}
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
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 35.10},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 57.40},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 93.20},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 147.00},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 244.00}
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
                20: {'dia': 0.97, 'od': 1.78, 'weight': 9.06, 'resistance': 37.40},
                22: {'dia': 0.76, 'od': 1.57, 'weight': 6.40, 'resistance': 61.00},
                24: {'dia': 0.61, 'od': 1.40, 'weight': 4.66, 'resistance': 98.70},
                26: {'dia': 0.48, 'od': 1.27, 'weight': 3.54, 'resistance': 162.00},
                28: {'dia': 0.38, 'od': 1.14, 'weight': 2.65, 'resistance': 259.00}
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
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.72, 'resistance': 35.10},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.28, 'resistance': 57.40},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.74, 'resistance': 93.20},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.74, 'resistance': 147.00},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.89, 'resistance': 244.00}
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
                20: {'dia': 0.97, 'od': 1.52, 'weight': 7.84, 'resistance': 37.40},
                22: {'dia': 0.76, 'od': 1.30, 'weight': 5.39, 'resistance': 61.00},
                24: {'dia': 0.61, 'od': 1.14, 'weight': 3.79, 'resistance': 98.70},
                26: {'dia': 0.48, 'od': 1.02, 'weight': 2.77, 'resistance': 162.00},
                28: {'dia': 0.38, 'od': 0.89, 'weight': 1.92, 'resistance': 259.00}
            }
        },
        'M22759/28': {
            'start': 14,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with polyimide hard coat.',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                14: {'dia': 1.70, 'od': 2.39, 'weight': 22.00, 'resistance': 9.45},
                16: {'dia': 1.35, 'od': 2.01, 'weight': 14.50, 'resistance': 14.80},
                18: {'dia': 1.19, 'od': 1.80, 'weight': 11.40, 'resistance': 19.00},
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.80, 'resistance': 30.10},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.22, 'resistance': 49.50},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.68, 'resistance': 79.70},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.68, 'resistance': 126.00},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.89, 'resistance': 209.00}
            }
        },
        'M22759/29': {
            'start': 14,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with polyimide hard coat.',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                14: {'dia': 1.70, 'od': 2.39, 'weight': 22.00, 'resistance': 9.84},
                16: {'dia': 1.35, 'od': 2.01, 'weight': 14.50, 'resistance': 15.60},
                18: {'dia': 1.19, 'od': 1.80, 'weight': 11.40, 'resistance': 20.00},
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.80, 'resistance': 32.00},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.22, 'resistance': 52.50},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.68, 'resistance': 85.00},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.68, 'resistance': 138.00},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.89, 'resistance': 223.00}
            }
        },
        'M22759/30': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ag/Cu',
            'material': 'Extruded PTFE with polyimide hard coat.',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 200,
            'data': {
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.80, 'resistance': 35.10},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.22, 'resistance': 57.40},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.68, 'resistance': 93.20},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.68, 'resistance': 147.00},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.89, 'resistance': 244.00}
            }
        },
        'M22759/31': {
            'start': 20,
            'stop': 29,
            'step': 2,
            'con_plate': 'Ni/Cu',
            'material': 'Extruded PTFE with polyimide hard coat.',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 260,
            'data': {
                20: {'dia': 0.97, 'od': 1.55, 'weight': 7.86, 'resistance': 37.40},
                22: {'dia': 0.76, 'od': 1.32, 'weight': 5.24, 'resistance': 61.00},
                24: {'dia': 0.61, 'od': 1.17, 'weight': 3.69, 'resistance': 98.70},
                26: {'dia': 0.48, 'od': 1.04, 'weight': 2.69, 'resistance': 162.00},
                28: {'dia': 0.38, 'od': 0.91, 'weight': 1.90, 'resistance': 259.00}
            }
        },
        'M22759/32': {
            'start': 12,
            'stop': 31,
            'step': 2,
            'con_plate': 'Sn/Cu',
            'material': 'Fluoropolymer Cross-linked Modified (ETFE)',
            'volts': 600,
            'min_temp': -55,
            'max_temp': 150,
            'data': {
                12: {'dia': 0.00, 'od': 2.62, 'weight': 29.00, 'resistance': 6.63},
                14: {'dia': 0.00, 'od': 2.16, 'weight': 19.00, 'resistance': 10.00},
                16: {'dia': 0.00, 'od': 1.73, 'weight': 12.30, 'resistance': 15.80},
                18: {'dia': 0.00, 'od': 1.52, 'weight': 9.67, 'resistance': 20.40},
                20: {'dia': 0.00, 'od': 1.27, 'weight': 6.40, 'resistance': 32.40},
                22: {'dia': 0.00, 'od': 1.09, 'weight': 4.17, 'resistance': 53.20},
                24: {'dia': 0.00, 'od': 0.94, 'weight': 2.98, 'resistance': 86.00},
                26: {'dia': 0.00, 'od': 0.81, 'weight': 2.08, 'resistance': 136.00},
                28: {'dia': 0.00, 'od': 0.68, 'weight': 1.35, 'resistance': 225.00},
                30: {'dia': 0.00, 'od': 0.61, 'weight': 0.98, 'resistance': 330.00}
            }
        },

        # 'M22759/80': {},
        # 'M22759/81': {},
        # 'M22759/82': {},
        # 'M22759/83': {},
        # 'M22759/84': {},
        # 'M22759/85': {},
        # 'M22759/86': {},
        # 'M22759/87': {},
        # 'M22759/88': {},
        # 'M22759/89': {},
        # 'M22759/90': {},
        # 'M22759/91': {},
        # 'M22759/92': {}
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
        9: 'White'
    }

    def __awg_to_mm2(a: int) -> float:
        d_in = _d('0.005') * (_d('92.0') ** ((_d('36.0') - _d(str(a))) / _d('39.0')))
        d_mm = d_in * _d('25.4')
        area_mm2 = (_d(str(math.pi)) / _d('4.0')) * (d_mm ** _d('2.0'))
        return float(round(area_mm2, 4))

    pn_template = '{series}-{awg}-{primary}{secondary}'

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

            dia = wire_data['data'][awg]['dia']
            od_mm = wire_data['data'][awg]['od']
            weight = wire_data['data'][awg]['weight'] * 1000.0
            resistance = wire_data['data'][awg]['resistance']

            mm_2 = __awg_to_mm2(awg)

            image = None
            datasheet = None
            cad = None

            colors = [
                'Black',
                'Brown',
                'Red',
                'Orange',
                'Yellow',
                'Green',
                'Blue',
                'Violet',
                'Gray',
                'White'
            ]

            for p_id, color in enumerate(colors):
                part_number = pn_template.format(series=family, awg=awg, primary=p_id, secondary='')
                description = f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]} Tefzel milspec single conductor wire'
                stripe_color = None
                num_conductors = 1
                shielded = 0
                tpi = 0.0

                values.append(
                    dict(
                        part_number=part_number,
                        description=description,
                        mfg='TE',
                        family=family,
                        series='Tefzel',
                        color=color,
                        image=image,
                        datasheet=datasheet,
                        cad=cad,
                        min_temp=min_temp,
                        max_temp=max_temp,
                        material=material,
                        stripe_color=stripe_color,
                        core_material=plating,
                        num_conductors=num_conductors,
                        shielded=shielded,
                        tpi=tpi,
                        conductor_dia_mm=dia,
                        size_mm2=mm_2,
                        size_awg=awg,
                        od_mm=od_mm,
                        weight_1km=weight,
                        resistance_1km=resistance,
                        volts=volts
                        )
                    )

                for s_id, stripe_color in enumerate(colors):
                    if stripe_color == color:
                        continue

                    description = f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]}/{color_mapping[s_id]} Tefzel milspec single conductor wire'

                    values.append(
                        dict(
                            part_number=part_number + str(s_id),
                            description=description,
                            mfg='TE',
                            family=family,
                            series='Tefzel',
                            color=color,
                            image=image,
                            datasheet=datasheet,
                            cad=cad,
                            min_temp=min_temp,
                            max_temp=max_temp,
                            material=material,
                            stripe_color=stripe_color,
                            core_material=plating,
                            num_conductors=num_conductors,
                            shielded=shielded,
                            tpi=tpi,
                            conductor_dia_mm=dia,
                            size_mm2=mm_2,
                            size_awg=awg,
                            od_mm=od_mm,
                            weight_1km=weight,
                            resistance_1km=resistance,
                            volts=volts
                            )
                        )

    return values


import json

print(json.dumps(_build_wires(), indent=4))
