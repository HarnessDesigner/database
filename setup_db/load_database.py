import math
import os
import json

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')


def _build_temps():
    data = [(0, 'Unknown',)]

    for i in range(-100, 305, 5):
        if i > 0:
            i = '+' + str(i)
        else:
            i = str(i)

        i += '°C'
        data.append((len(data), i))

    return data


def _build_wires():
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
        d_in = 0.005 * (92 ** ((36 - a) / 39))
        d_mm = d_in * 25.4
        area_mm2 = (math.pi / 4) * (d_mm ** 2)
        return round(area_mm2, 4)

    pn_template = 'M22759/32-{awg}-{primary}{secondary}'

    values = []

    for awg in range(8, 31, 2):
        mm_2 = __awg_to_mm2(awg)

        for p_id in range(10):
            part_number = pn_template.format(awg=awg, primary=p_id, secondary='')
            description = f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]} Tefzel milspec single conductor wire'

            values.append((part_number, 2, description, str(mm_2), awg, p_id, '[]', 7))
            for s_id in range(10):
                if p_id == s_id:
                    continue
                description = f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]}/{color_mapping[s_id]} Tefzel milspec single conductor wire'

                values.append((part_number + str(s_id), 2, description, str(mm_2), awg, p_id, f'[{str(s_id)}]', 7))

    return values


def get_mfg_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM manufacturers WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO manufacturers (name, phone, address, email, website) '
                        'VALUES (?, ?, ?, ?, ?);', (name, '', '', '', ''))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_temperature_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM temperatures WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO temperatures (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_gender_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM genders WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO genders (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_protection_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM protections WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO protections (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_adhesive_id(con, cur, code):
    if not code:
        return 0

    res = cur.execute(f'SELECT id FROM adhesives WHERE code="{code}";')

    if not res:
        cur.executemany('INSERT INTO adhesives (code,) VALUES (?);', (code,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_cavity_lock_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM cavity_locks WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO cavity_locks (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_color_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM colors WHERE name="{name}";')

    if not res:
        raise RuntimeError(name)
    else:
        return res[0][0]


def get_direction_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM directions WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO directions (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


# TODO: IP Rating getter


def get_plating_id(con, cur, symbol):
    if not symbol:
        return 0

    res = cur.execute(f'SELECT id FROM platings WHERE symbol="{symbol}";')

    if not res:
        cur.executemany('INSERT INTO platings (symbol,) VALUES (?);', (symbol,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_material_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM materials WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO materials (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_shape_id(con, cur, name):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM shapes WHERE name="{name}";')

    if not res:
        cur.executemany('INSERT INTO shapes (name,) VALUES (?);', (name,))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_series_id(con, cur, name, mfg_id):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM series WHERE name="{name}" AND mfg_id={mfg_id};')

    if not res:
        cur.executemany('INSERT INTO series (name, mfg_id) VALUES (?, ?);', (name, mfg_id))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_family_id(con, cur, name, mfg_id):
    if not name:
        return 0

    res = cur.execute(f'SELECT id FROM families WHERE name="{name}" AND mfg_id={mfg_id};')

    if not res:
        cur.executemany('INSERT INTO families (name, mfg_id) VALUES (?, ?);', (name, mfg_id))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def get_resource_id(con, cur, path, type="UNKNOWN"):
    if not path:
        return 0

    res = cur.execute(f'SELECT id FROM resources WHERE path="{path}";')

    if not res:
        if type == 'UNKNOWN':
            if '.jpg' in path:
                type = 'jpg'
            elif '.pdf' in path:
                type = 'pdf'
            elif '.tif' in path:
                type = 'tif'
            elif '.png' in path:
                type = 'png'

        cur.executemany('INSERT INTO resources (path, type) VALUES (?);', (path, type))

        con.commit()
        return cur.lastrowid
    else:
        return res[0][0]


def add_cover(con, cur, part_number, mfg, series, length, width, height, color,
              pins, direction, min_temp, max_temp, image, cad):

    mfg_id = get_mfg_id(con, cur, mfg)
    series_id = get_series_id(con, cur, series, mfg_id)
    color_id = get_color_id(con, cur, color)
    image_id = get_resource_id(con, cur, image)
    direction_id = get_direction_id(con, cur, direction)
    if min_temp > 0:
        min_temp = '+' + str(min_temp) + '°F'
    else:
        min_temp = str(min_temp) + '°F'

    if max_temp > 0:
        max_temp = '+' + str(max_temp) + '°F'
    else:
        max_temp = str(max_temp) + '°F'

    min_temp_id = get_temperature_id(con, cur, min_temp)
    max_temp_id = get_temperature_id(con, cur, max_temp)

    cur.executemany('INSERT INTO covers (part_number, mfg_id, series_id, color_id, '
                    'image_id, direction_id, min_temp_id, max_temp_id, length, width, '
                    'height, pins) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, color_id, image_id, direction_id,
                     min_temp_id, max_temp_id, length, width, height, pins))

    con.commit()


def add_cpa_lock(con, cur, part_number, mfg, series, family, length, width, height, color,
                 pins, terminal_size, min_temp, max_temp, image, cad):

    mfg_id = get_mfg_id(con, cur, mfg)
    series_id = get_series_id(con, cur, series, mfg_id)
    family_id = get_family_id(con, cur, family, mfg_id)
    color_id = get_color_id(con, cur, color)
    image_id = get_resource_id(con, cur, image)
    cad_id = get_resource_id(con, cur, cad)

    if min_temp > 0:
        min_temp = '+' + str(min_temp) + '°F'
    else:
        min_temp = str(min_temp) + '°F'

    if max_temp > 0:
        max_temp = '+' + str(max_temp) + '°F'
    else:
        max_temp = str(max_temp) + '°F'

    min_temp_id = get_temperature_id(con, cur, min_temp)
    max_temp_id = get_temperature_id(con, cur, max_temp)

    cur.executemany('INSERT INTO cpa_locks (part_number, mfg_id, series_id, family_id, '
                    'color_id, image_id, cad_id, terminal_size, min_temp_id, max_temp_id, '
                    'length, width, height, pins) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, family_id, color_id, image_id,
                     cad_id, terminal_size, min_temp_id, max_temp_id, length, width,
                     height, pins))

    con.commit()


def add_tpa_lock(con, cur, part_number, mfg, series, family, length, width, height, color,
                 pins, terminal_size, min_temp, max_temp, image, cad):

    mfg_id = get_mfg_id(con, cur, mfg)
    series_id = get_series_id(con, cur, series, mfg_id)
    family_id = get_family_id(con, cur, family, mfg_id)
    color_id = get_color_id(con, cur, color)
    image_id = get_resource_id(con, cur, image)
    cad_id = get_resource_id(con, cur, cad)

    if min_temp > 0:
        min_temp = '+' + str(min_temp) + '°F'
    else:
        min_temp = str(min_temp) + '°F'

    if max_temp > 0:
        max_temp = '+' + str(max_temp) + '°F'
    else:
        max_temp = str(max_temp) + '°F'

    min_temp_id = get_temperature_id(con, cur, min_temp)
    max_temp_id = get_temperature_id(con, cur, max_temp)

    cur.executemany('INSERT INTO tpa_locks (part_number, mfg_id, series_id, family_id, '
                    'color_id, image_id, cad_id, terminal_size, min_temp_id, max_temp_id, '
                    'length, width, height, pins) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, family_id, color_id, image_id,
                     cad_id, terminal_size, min_temp_id, max_temp_id, length, width,
                     height, pins))

    con.commit()


def add_seal(con, cur, part_number, mfg, series, type, length, o_dia, i_dia, color,
             hardness, lubricant, min_temp, max_temp, image, cad, wire_dia_min, wire_dia_max):

    mfg_id = get_mfg_id(con, cur, mfg)
    series_id = get_series_id(con, cur, series, mfg_id)
    color_id = get_color_id(con, cur, color)
    image_id = get_resource_id(con, cur, image)
    cad_id = get_resource_id(con, cur, cad)

    if min_temp > 0:
        min_temp = '+' + str(min_temp) + '°F'
    else:
        min_temp = str(min_temp) + '°F'

    if max_temp > 0:
        max_temp = '+' + str(max_temp) + '°F'
    else:
        max_temp = str(max_temp) + '°F'

    min_temp_id = get_temperature_id(con, cur, min_temp)
    max_temp_id = get_temperature_id(con, cur, max_temp)

    cur.executemany('INSERT INTO seals (part_number, mfg_id, series_id, type, '
                    'color_id, image_id, cad_id, lubricant, min_temp_id, max_temp_id, '
                    'length, o_dia, i_dia, hardness, wire_dia_min, wire_dia_max) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, type, color_id, image_id,
                     cad_id, lubricant, min_temp_id, max_temp_id, length, o_dia,
                     i_dia, hardness, wire_dia_min, wire_dia_max))

    con.commit()


def add_terminal(con, cur, part_number, mfg, series, cavity_lock, wire_dia_min,
                 wire_dia_max, min_wire_cross, max_wire_cross, gender, blade_size,
                 sealing, plating, image, cad):

    mfg_id = get_mfg_id(con, cur, mfg)
    series_id = get_series_id(con, cur, series, mfg_id)
    cavity_lock_id = get_cavity_lock_id(con, cur, cavity_lock)
    plating_id = get_plating_id(con, cur, plating)
    gender_id = get_gender_id(con, cur, gender)
    image_id = get_resource_id(con, cur, image)
    cad_id = get_resource_id(con, cur, cad)

    cur.executemany('INSERT INTO seals (part_number, mfg_id, series_id, plating_id, '
                    'image_id, cad_id, gender_id, sealing, cavity_lock_id, blade_size, '
                    'wire_dia_min, wire_dia_max, min_wire_cross, max_wire_cross) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, plating_id, image_id,
                     cad_id, gender_id, sealing, cavity_lock_id, blade_size,
                     wire_dia_min, wire_dia_max, min_wire_cross, max_wire_cross))

    con.commit()


def add_housing(con, cur, part_number, mfg, family, series, num_pins, rows,
                centerline, gender, direction, color, sealed, min_temp, max_temp,
                length, width, height, cavity_lock, terminal_sizes, mates_to,
                compat_terminals, compat_seals, compat_covers, compat_cpas,
                compat_tpas, cad, image):

    mfg_id = get_mfg_id(con, cur, mfg)
    family_id = get_family_id(con, cur, family, mfg_id)
    series_id = get_series_id(con, cur, series, mfg_id)
    direction_id = get_direction_id(con, cur, direction)
    color_id = get_color_id(con, cur, color)

    if min_temp > 0:
        min_temp = '+' + str(min_temp) + '°F'
    else:
        min_temp = str(min_temp) + '°F'

    if max_temp > 0:
        max_temp = '+' + str(max_temp) + '°F'
    else:
        max_temp = str(max_temp) + '°F'

    min_temp_id = get_temperature_id(con, cur, min_temp)
    max_temp_id = get_temperature_id(con, cur, max_temp)

    cavity_lock_id = get_cavity_lock_id(con, cur, cavity_lock)
    gender_id = get_gender_id(con, cur, gender)
    image_id = get_resource_id(con, cur, image)
    cad_id = get_resource_id(con, cur, cad)

    cur.executemany('INSERT INTO housings (part_number, mfg_id, family_id, series_id, '
                    'color_id, min_temp_id, max_temp_id, image_id, cad_id, gender_id, '
                    'direction_id, length, width, height, cavity_lock_id, sealing, '
                    'rows, num_pins, terminal_sizes, centerline, compat_cpas, '
                    'compat_tpas, compat_covers, compat_terminals, compat_seals, '
                    'compat_housings) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, family_id, series_id, color_id,
                     min_temp_id, max_temp_id, image_id, cad_id, gender_id,
                     direction_id, length, width, height, cavity_lock_id,
                     sealed, rows, num_pins, terminal_sizes, centerline,
                     compat_cpas, compat_tpas, compat_covers, compat_terminals,
                     compat_seals, mates_to))

    con.commit()


def add_transition_branch(con, cur, idx, transition_id, **kwargs):
    kwargs['min_dia'] = kwargs.pop('min')
    kwargs['max_dia'] = kwargs.pop('max')

    keys = sorted(list(kwargs.keys()))
    values = []

    for key in keys:
        values.append(kwargs[key])

    keys = ', '.join(keys)

    questions = ['?'] * len(values)
    questions = ', '.join(questions)

    cur.executemany(f'INSERT INTO transition_branches  (transition_id, idx, {keys}) VALUES (?, ?, {questions});',
                    [transition_id, idx] + values)

    con.commit()


def add_transition(con, cur, part_number, description, series, material, shape,
                   max_temp, min_temp, resistances, adhesive, branch_count, branches,
                   cad, datasheet, image):

    mfg_id = 1
    series_id = get_series_id(con, cur, series, mfg_id)
    family_id = get_family_id(con, cur, 'RayChem', mfg_id)
    color_id = get_color_id(con, cur, 'Black')
    material_id = get_material_id(con, cur, material)
    shape_id = get_shape_id(con, cur, shape)
    if min_temp > 0:
        min_temp = '+' + str(min_temp) + '°F'
    else:
        min_temp = str(min_temp) + '°F'

    if max_temp > 0:
        max_temp = '+' + str(max_temp) + '°F'
    else:
        max_temp = str(max_temp) + '°F'

    min_temp_id = get_temperature_id(con, cur, min_temp)
    max_temp_id = get_temperature_id(con, cur, max_temp)

    protections = '\n'.join(resistances)
    protection_id = get_protection_id(con, cur, protections)

    if image:
        image_id = get_resource_id(con, cur, **image)
    else:
        image_id = 0

    if cad:
        cad_id = get_resource_id(con, cur, **cad)
    else:
        cad_id = 0

    if datasheet:
        datasheet_id = get_resource_id(con, cur, **datasheet)
    else:
        datasheet_id = 0

    adhesive_ids = str(adhesive)

    cur.executemany('INSERT INTO transitions (part_number, mfg_id, description, family_id, series_id, '
                    'color_id, material_id, branch_count, shape_id, protection_id, adhesive_ids, '
                    'cad_id, datasheet_id, image_id, min_temp_id, max_temp_id, sealing, '
                    'rows, num_pins, terminal_sizes, centerline, compat_cpas, '
                    'compat_tpas, compat_covers, compat_terminals, compat_seals, '
                    'compat_housings) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, description, family_id, series_id, color_id,
                     material_id, branch_count, shape_id, protection_id, adhesive_ids,
                     cad_id, datasheet_id, image_id, min_temp_id, max_temp_id))

    con.commit()

    transition_id = cur.lastrowid

    for i, branch in enumerate(branches):
        try:
            add_transition_branch(con, cur, i, transition_id, **branch)
        except:
            print('BRANCH ERROR:', part_number)
            continue


def add_manufacturers(con, cur):
    res = cur.execute('SELECT id FROM manufacturers WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'NOT SET', '', '', '', ''),
        (1, 'TE', '1-800-522-6752', '', '', 'https://www.te.com/en/home.html'),
        (2, 'Bosch', '+49 304 036 94077',
         'Robert-Bosch-Platz 1\n70839 Gerlingen-Schillerhöhe\nGERMANY\n',
         'Connectors-Webshop-Hotline.PSCTS1-CO@de.bosch.com',
         'https://bosch-connectors.com/bcp/b2bshop-psconnectors/en/EUR'),
        (3, 'Aptiv', '', '', '', 'https://www.aptiv.com/en/contact'),
        (4, 'Molex', '+800-786-6539', '2222 Wellington Ct\nLisle, IL 60532, USA', '',
         'https://www.molex.com/en-us/products/connectors'),
        (5, 'EPC', '', '', '', ''),
        (6, 'Yazaki', '', '', '', ''),
    )

    cur.executemany('INSERT INTO manufacturers (id, name, phone, address, email, website) '
                    'VALUES (?, ?, ?, ?, ?, ?);', data)
    con.commit()


def add_accessories(con, cur):
    res = cur.execute('SELECT id FROM accessories WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'N/A', 'N/A', 0),
        (1, 'S1017-1.0X50', '1" x 50\' Polyamide Adhesive, -20 – 60 °C [-4 – 140 °F], Hot Melt Tape', 1),
        (2, 'S1030', 'Polyolefin Adhesive, -80 – 80 °C [-112 – 176 °F], Hot Melt Tape', 1),
        (3, 'S1030-TAPE-3/4X33FT', '3/4" x 33\' Polyolefin Adhesive, -80 – 80 °C [-112 – 176 °F], Hot Melt Tape', 1),
        (4, 'S1048-TAPE-1X100-FT', '1" x 100\' Thermoplastic Adhesive, -55 – 120 °C [-67 – 248 °F], Hot Melt Tape', 1),
        (5, 'S1048-TAPE-3/4X100-FT', '3/4" x 100\' Thermoplastic Adhesive, -55 – 120 °C [-67 – 248 °F], Hot Melt Tape', 1),
        (6, 'S1125-KIT-1', 'Dual Pack, 5 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives', 1),
        (7, 'S1125-KIT-4', 'Dual Pack, 5 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives', 1),
        (8, 'S1125-KIT-5', 'Dual Pack, 1 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives', 1),
        (9, 'S1125-KIT-8', 'Dual Pack, 1 Packaging Quantity, 150 °C Temperature (Max), Epoxy Adhesives', 1),
        (10, 'S1125-APPLICATOR', 'Epoxy Adhesives Dispensing Gun', 1)
    )
    cur.executemany('INSERT INTO accessories (id, part_number, description, mfg_id) VALUES(?, ?, ?, ?);', data)
    con.commit()


def add_resources(con, cur):
    res = cur.execute('SELECT id FROM resources WHERE id=0;')
    if res.fetchall():
        return

    cur.execute('INSERT INTO resources (id, path) VALUES(0, "NOT SET");')
    con.commit()


def add_series(con, cur):
    res = cur.execute('SELECT id FROM series WHERE id=0;')
    if res.fetchall():
        return

    cur.execute('INSERT INTO series (id, name) VALUES(0, "N/A");')
    con.commit()


def add_families(con, cur):
    res = cur.execute('SELECT id FROM families WHERE id=0;')
    if res.fetchall():
        return

    data = ((0, 'N/A'),)
    cur.execute('INSERT INTO families (id, name) VALUES(?, ?);', data)
    con.commit()


def add_genders(con, cur):
    res = cur.execute('SELECT id FROM genders WHERE id=0;')
    if res.fetchall():
        return

    data = ((0, "Unknown"), (1, "Male"), (2, "Female"))
    cur.executemany('INSERT INTO genders (id, name) VALUES(?, ?);', data)
    con.commit()


def add_directions(con, cur):
    res = cur.execute('SELECT id FROM directions WHERE id=0;')
    if res.fetchall():
        return

    data = ((0, "N/A"), (1, "Left"), (2, "Right"), (3, "Straight"),
            (4, "90°"), (5, "180°"), (6, "270°"))
    cur.executemany('INSERT INTO directions (id, name) VALUES(?, ?);', data)
    con.commit()


def add_splice_types(con, cur):
    res = cur.execute('SELECT id FROM splice_types WHERE id=0;')
    if res.fetchall():
        return

    data = ((0, "N/A"), (1, "Butt"), (2, "Cable"), (3, "Closed End"),
            (4, "Parallel"), (5, "Pigtail"), (6, "Tap"),
            (7, "Thru"), (8, "Solder Sleeve"), (9, "Solder Sleeve w/Pigtail"))
    cur.executemany('INSERT INTO splice_types (id, name) VALUES(?, ?);', data)
    con.commit()


def add_temperatures(con, cur):
    res = cur.execute('SELECT id FROM temperatures WHERE id=0;')
    if res.fetchall():
        return

    cur.executemany('INSERT INTO temperatures (id, name) VALUES (?, ?);', _build_temps())
    con.commit()


def add_materials(con, cur):
    res = cur.execute('SELECT id FROM materials WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'N/A'),
        (1, 'Fluid Resistant Modified Elastomer')
    )
    cur.executemany('INSERT INTO materials (id, name) VALUES(?, ?);', data)
    con.commit()


def add_platings(con, cur):
    res = cur.execute('SELECT id FROM platings WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'N/A', 'Unknown'),
        (1, 'Sn', 'Tin'),
        (2, 'Cu', 'Copper'),
        (3, 'Al', 'Aluminum'),
        (4, 'Au', 'Gold'),
        (5, 'Ag', 'Silver'),
        (6, 'Ag/Cu', 'Silver-plated Copper'),
        (7, 'Sn/Cu', 'Tin-plated Copper'),
        (8, 'Au/Cu', 'Gold-plated Copper'),
        (9, 'Ag/Al', 'Silver-plated Aluminum'),
        (10, 'Sn/Al', 'Tin-plated Aluminum'),
        (11, 'Au/Al', 'Gold-plated Aluminum')
    )

    cur.executemany('INSERT INTO platings (id, symbol, desc) VALUES(?, ?, ?);', data)
    con.commit()


def add_cavity_locks(con, cur):
    res = cur.execute('SELECT id FROM cavity_locks WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'N/A'),
        (1, 'Cavity Lock'),
        (2, 'Locking Lance'),
        (3, 'Flex Arm'),
        (4, 'Insert Molded'),
        (5, 'Molded On'),
        (6, 'Nose Piece'),
        (7, 'Press Fit')
    )

    cur.executemany('INSERT INTO cavity_locks (id, name) VALUES (?, ?);', data)
    con.commit()


def add_colors(con, cur):
    res = cur.execute('SELECT id FROM colors WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'Black', 0x000000),
        (1, 'Brown', 0x8C7355),
        (2, 'Red', 0xFE0000),
        (3, 'Orange', 0xFFA500),
        (4, 'Yellow', 0xFFFF01),
        (5, 'Green', 0x28C629),
        (6, 'Blue', 0x0000FE),
        (7, 'Violet', 0x9400D4),
        (8, 'Gray', 0xA1A1A1),
        (9, 'White', 0xFFFFFF),
        (10, 'Natural', 0xE5D3BF),
        (11, 'Dark Red', 0x950606),
        (12, 'Red Brown', 0x942222),
        (13, 'Light Blue', 0x90D5FF),
        (14, 'Light Gray', 0xD3D3D3),
        (15, 'Transparent', 0xFFFFFF)
    )

    cur.executemany('INSERT INTO colors (id, name, rgb) VALUES(?, ?, ?);', data)
    con.commit()


def add_ip_fluids(con, cur):
    res = cur.execute('SELECT id FROM ip_fluids WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, '0', 'No Protection', 'No protection against ingress of water.', None),
        (1, '1', 'Dripping water', 'Dripping water (vertically falling drops) shall have no unsafe effect on the specimen when mounted upright.', open(f'{BASE_PATH}/image/ip/IPX1.png', 'rb').read()),
        (2, '2', 'Dripping water when tilted at 15°', 'Vertically dripping water shall have no harmful effect when the enclosure is tilted at an angle of 15° from its normal position.', open(f'{BASE_PATH}/image/ip/IPX2.png', 'rb').read()),
        (3, '3', 'Spraying water', 'Water falling as a spray at any angle up to 60° from the vertical shall have no harmful effect.', open(f'{BASE_PATH}/image/ip/IPX3.png', 'rb').read()),
        (4, '4', 'Splashing water', 'Water splashing against the enclosure from any direction shall have no harmful effect.', open(f'{BASE_PATH}/image/ip/IPX4.png', 'rb').read()),
        (5, '5', 'Water jets', 'Water projected by a nozzle (6.3 mm) against enclosure from any direction shall have no harmful effects.', open(f'{BASE_PATH}/image/ip/IPX5.png', 'rb').read()),
        (6, '6', 'Powerful water jets', 'Water projected in powerful jets (12.5 mm nozzle) against the enclosure from any direction shall have no harmful effects.', open(f'{BASE_PATH}/image/ip/IPX6.png', 'rb').read()),
        (7, '7', 'Immersion, up to 1 meter', 'Ingress of water in harmful quantity shall not be possible when the enclosure is immersed in water.', open(f'{BASE_PATH}/image/ip/IPX7.png', 'rb').read()),
        (8, '8', 'Immersion, 1 meter or more depth', 'The equipment is suitable for continuous immersion in water.', open(f'{BASE_PATH}/image/ip/IPX8.png', 'rb').read()),
        (9, '9', 'Powerful high-temperature water jets', 'Protected against close-range high-pressure, high-temperature spray downs.', open(f'{BASE_PATH}/image/ip/IPX9.png', 'rb').read()),
        (10, '6K', 'Powerful water jets with increased pressure', 'Water projected in powerful jets (6.3 mm nozzle) against the enclosure from any direction, under elevated pressure.', open(f'{BASE_PATH}/image/ip/IPX6K.png', 'rb').read()),
        (11, '9K', 'Steam Cleaning', 'Protection against high-pressure, high-temperature jet sprays, wash-downs or steam-cleaning procedures', open(f'{BASE_PATH}/image/ip/IPX9K.png', 'rb').read()),
        (12, 'X', 'Unknown', 'No data is available to specify a protection rating about this criterion.', None)
    )

    cur.executemany('INSERT INTO ip_fluids (id, name, short_desc, description, icon_data) VALUES (?, ?, ?, ?, ?);', data)
    con.commit()


def add_ip_solids(con, cur):
    res = cur.execute('SELECT id FROM ip_solids WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, '0', 'No Protection', 'No protection against contact and ingress of objects.', None),
        (1, '1', '>= 50.00mm sized objects', 'Any large surface of the body, such as the back of a hand, but no protection against deliberate contact with a body part.', open(f'{BASE_PATH}/image/ip/IP1X.png', 'rb').read()),
        (2, '2', '>= 12.50mm sized objects', 'Fingers or similar objects.', open(f'{BASE_PATH}/image/ip/IP2X.png', 'rb').read()),
        (3, '3', '>= 2.50mm sized objects', 'Tools, thick wires, etc.', open(f'{BASE_PATH}/image/ip/IP3X.png', 'rb').read()),
        (4, '4', '>= 1.00mm sized objects', 'Most wires, slender screws, large ants, etc.', open(f'{BASE_PATH}/image/ip/IP4X.png', 'rb').read()),
        (5, '5', 'Dust Protected', 'Ingress of dust is not entirely prevented.', open(f'{BASE_PATH}/image/ip/IP5X.png', 'rb').read()),
        (6, '6', 'Dust Tight', 'No ingress of dust.', open(f'{BASE_PATH}/image/ip/IP6X.png', 'rb').read()),
        (7, 'X', 'Unknown', 'No data is available to specify a protection rating about this criterion.', None)
    )

    cur.executemany('INSERT INTO ip_solids (id, name, short_desc, description, icon_data) VALUES (?, ?, ?, ?, ?);', data)
    con.commit()


def add_ip_supps(con, cur):
    res = cur.execute('SELECT id FROM ip_supps WHERE id=0;')
    if res.fetchall():
        return

    data = (
        ('D', 'Wire'),
        ('G', 'Oil resistant'),
        ('F', 'Oil resistant'),
        ('H', 'High voltage apparatus'),
        ('M', 'Motion during water test'),
        ('S', 'Stationary during water test'),
        ('W', 'Weather conditions')
    )

    cur.executemany('INSERT INTO ip_supps (name, description) VALUES (?, ?);', data)
    con.commit()


def add_ip_ratings(con, cur):
    res = cur.execute('SELECT id FROM ip_ratings WHERE id=0;')
    if res.fetchall():
        return

    add_ip_supps(con, cur)
    add_ip_solids(con, cur)
    add_ip_fluids(con, cur)

    data = (('IPXX', 7, 12), ('IP01', 0, 1), ('IP02', 0, 2), ('IP03', 0, 3),
            ('IP04', 0, 4), ('IP05', 0, 5), ('IP06', 0, 6), ('IP07', 0, 7),
            ('IP08', 0, 8), ('IP09', 0, 9), ('IP06K', 0, 10), ('IP09K', 0, 11),
            ('IP0X', 0, 12), ('IP10', 1, 0), ('IP11', 1, 1), ('IP12', 1, 2),
            ('IP13', 1, 3), ('IP14', 1, 4), ('IP15', 1, 5), ('IP16', 1, 6),
            ('IP17', 1, 7), ('IP18', 1, 8), ('IP19', 1, 9), ('IP16K', 1, 10),
            ('IP19K', 1, 11), ('IP1X', 1, 12), ('IP20', 2, 0), ('IP21', 2, 1),
            ('IP22', 2, 2), ('IP23', 2, 3), ('IP24', 2, 4), ('IP25', 2, 5),
            ('IP26', 2, 6), ('IP27', 2, 7), ('IP28', 2, 8), ('IP29', 2, 9),
            ('IP26K', 2, 10), ('IP29K', 2, 11), ('IP2X', 2, 12), ('IP30', 3, 0),
            ('IP31', 3, 1), ('IP32', 3, 2), ('IP33', 3, 3), ('IP34', 3, 4),
            ('IP35', 3, 5), ('IP36', 3, 6), ('IP37', 3, 7), ('IP38', 3, 8),
            ('IP39', 3, 9), ('IP36K', 3, 10), ('IP39K', 3, 11), ('IP3X', 3, 12),
            ('IP40', 4, 0), ('IP41', 4, 1), ('IP42', 4, 2), ('IP43', 4, 3),
            ('IP44', 4, 4), ('IP45', 4, 5), ('IP46', 4, 6), ('IP47', 4, 7),
            ('IP48', 4, 8), ('IP49', 4, 9), ('IP46K', 4, 10), ('IP49K', 4, 11),
            ('IP4X', 4, 12), ('IP50', 5, 0), ('IP51', 5, 1), ('IP52', 5, 2),
            ('IP53', 5, 3), ('IP54', 5, 4), ('IP55', 5, 5), ('IP56', 5, 6),
            ('IP57', 5, 7), ('IP58', 5, 8), ('IP59', 5, 9), ('IP56K', 5, 10),
            ('IP59K', 5, 11), ('IP5X', 5, 12), ('IP60', 6, 0), ('IP61', 6, 1),
            ('IP62', 6, 2), ('IP63', 6, 3), ('IP64', 6, 4), ('IP65', 6, 5),
            ('IP66', 6, 6), ('IP67', 6, 7), ('IP68', 6, 8), ('IP69', 6, 9),
            ('IP66K', 6, 10), ('IP69K', 6, 11), ('IP6X', 6, 12), ('IPX0', 7, 0),
            ('IPX1', 7, 1), ('IPX2', 7, 2), ('IPX3', 7, 3), ('IPX4', 7, 4),
            ('IPX5', 7, 5), ('IPX6', 7, 6), ('IPX7', 7, 7), ('IPX8', 7, 8),
            ('IPX9', 7, 9), ('IPX6K', 7, 10), ('IPX9K', 7, 11))

    cur.executemany('INSERT INTO ip_ratings (name, solid_id, fluid_id) VALUES (?, ?, ?);', data)
    con.commit()


def add_protections(con, cur):
    res = cur.execute('SELECT id FROM protections WHERE id=0;')
    if res.fetchall():
        return

    data = ((0, 'Not applicable'))

    cur.executemany('INSERT INTO protections (id, name) VALUES (?, ?);', data)
    con.commit()


def add_adhesives(con, cur):
    res = cur.execute('SELECT id FROM adhesives WHERE id=0;')
    if res.fetchall():
        return

    data = (
        (0, 'None', 'None', '[]'),
        (1, '225', 'Precoated latent-curing epoxy/polyamide', '[]'),
        (2, '42', 'Hot-melt/polyamide (Thermoplastic)', '[]'),
        (3, '86', 'Hot-melt,high performance (Thermoplastic)', '[]'),
        (4, 'S1006', 'Epoxy/polyamide two-part paste (Thermoset)', '[]'),
        (5, 'S1017', 'Hot-melt/polyamide (Thermoplastic)', '["S1017-1.0X50"]'),
        (6, 'S1030', 'Hot-melt/polyolefin (Thermoplastic)', '["S1030", "S1030-TAPE-3/4X33FT"]'),
        (7, 'S1048', 'Hot-melt,high performance (Thermoplastic)', '["S1048-TAPE-1X100-FT", "S1048-TAPE-3/4X100-FT"]'),
        (8, 'S1125', 'Epoxy/polyamide two-part paste (Thermoset)', '["S1125-KIT-1", "S1125-KIT-4", "S1125-KIT-5", "S1125-KIT-8","S1125-APPLICATOR"]')
    )

    cur.executemany('INSERT INTO adhesives (id, code, description, accessory_part_nums) VALUES (?, ?, ?, ?);', data)
    con.commit()


def add_shapes(con, cur):
    res = cur.execute('SELECT id FROM shapes WHERE id=0;')
    if res.fetchall():
        return

    data = ((0, 'N/A'),)
    cur.executemany('INSERT INTO shapes (id, name) VALUES (?, ?);', data)
    con.commit()


def cpa_locks(con, cur):
    add_manufacturers(con, cur)
    add_resources(con, cur)
    add_series(con, cur)
    add_families(con, cur)
    add_temperatures(con, cur)
    add_colors(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'cpa_locks.json')

    cur.execute('INSERT INTO cpa_locks (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_cpa_lock(con, cur, **item)


def tpa_locks(con, cur):
    add_manufacturers(con, cur)
    add_resources(con, cur)
    add_series(con, cur)
    add_families(con, cur)
    add_temperatures(con, cur)
    add_colors(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'tpa_locks.json')

    cur.execute('INSERT INTO tpa_locks (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_tpa_lock(con, cur, **item)


def seals(con, cur):
    add_manufacturers(con, cur)
    add_series(con, cur)
    add_colors(con, cur)
    add_temperatures(con, cur)
    add_resources(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'seals.json')

    cur.execute('INSERT INTO seals (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_seal(con, cur, **item)


def boots(con, cur):
    add_manufacturers(con, cur)
    add_series(con, cur)
    add_families(con, cur)
    add_colors(con, cur)
    add_resources(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'boots.json')

    cur.execute('INSERT INTO boots (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_seal(con, cur, **item)


def covers(con, cur):
    add_manufacturers(con, cur)
    add_resources(con, cur)
    add_series(con, cur)
    add_families(con, cur)
    add_temperatures(con, cur)
    add_colors(con, cur)
    add_directions(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'covers.json')

    cur.execute('INSERT INTO covers (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_cover(con, cur, **item)


def terminals(con, cur):
    add_manufacturers(con, cur)
    add_resources(con, cur)
    add_series(con, cur)
    add_families(con, cur)
    add_colors(con, cur)
    add_platings(con, cur)
    add_genders(con, cur)
    add_cavity_locks(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'terminals.json')

    cur.execute('INSERT INTO terminals (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_terminal(con, cur, **item)


def wires(con, cur):
    add_manufacturers(con, cur)
    add_families(con, cur)
    add_series(con, cur)
    add_colors(con, cur)
    add_temperatures(con, cur)
    add_resources(con, cur)
    add_materials(con, cur)
    add_platings(con, cur)

    json_path = os.path.join(DATA_PATH, 'wires.json')

    cur.executemany('INSERT INTO wires (part_number, mfg_id, description, size_mm2, size_awg, primary_color_id, addl_color_ids, core_material_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?);', _build_wires())
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_wire(con, cur, **item)


def housings(con, cur):
    add_manufacturers(con, cur)
    add_families(con, cur)
    add_series(con, cur)
    add_colors(con, cur)
    add_temperatures(con, cur)
    add_resources(con, cur)
    add_genders(con, cur)
    add_directions(con, cur)
    add_cavity_locks(con, cur)
    add_ip_ratings(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'housings.json')

    cur.execute('INSERT INTO housings (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_housing(con, cur, **item)


def splices(con, cur):
    add_manufacturers(con, cur)
    add_families(con, cur)
    add_series(con, cur)
    add_materials(con, cur)
    add_platings(con, cur)
    add_splice_types(con, cur)
    add_colors(con, cur)
    add_temperatures(con, cur)
    add_resources(con, cur)
    add_models3d(con, cur)

    json_path = os.path.join(DATA_PATH, 'splices.json')

    cur.execute('INSERT INTO splices (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_splice(con, cur, **item)


def bundle_covers(con, cur):
    add_manufacturers(con, cur)
    add_families(con, cur)
    add_series(con, cur)
    add_materials(con, cur)
    add_colors(con, cur)
    add_temperatures(con, cur)
    add_resources(con, cur)
    add_protections(con, cur)

    json_path = os.path.join(DATA_PATH, 'bundle_covers.json')

    cur.execute('INSERT INTO bundle_covers (id, part_number, description) VALUES(0, "N/A", "Unknown/Not Applicable");')
    con.commit()

    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for item in data:
        add_bundle_cover(con, cur, **item)



if __name__ == '__main__':
    import sqlite3
    con_ = sqlite3.connect('test.db')
    cur_ = con_.cursor()
    preload_database(con_, cur_)
    load_tpa_locks(con_, cur_)
    load_cpa_locks(con_, cur_)
    load_covers(con_, cur_)
    load_seals(con_, cur_)
    load_terminals(con_, cur_)
    load_housings(con_, cur_)
    load_cavity_maps(con_, cur_)
    load_transitions(con_, cur_)
    load_shrink_tube(con_, cur_)

    cur_.close()
    con_.close()
