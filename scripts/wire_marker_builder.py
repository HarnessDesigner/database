import json


def _build_wire_markers():
    data = {
        'SH RNF-3000-3/1-{color_id}': {
            'min_awg': 18,
            'max_awg': 10,
            'description': 'Shrink Markers ({color}/Standard)',
            'min_diameter': 1.0,
            'max_diameter': 3.0,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20RNF-3000-3%201-{color_id}_thumbnail.jpg'
        },
        'SH RNF-3000-0-{color_id}': {
            'min_awg': 26,
            'max_awg': 18,
            'description': 'Shrink Markers ({color}/Mini)',
            'min_diameter': 0.5,
            'max_diameter': 1.5,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20RNF-3000-{color_id}_thumbnail.jpg'
        }
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

    mfg = 'Milspecwiring.com'
    res = []

    for color_id, color in color_mapping.items():
        for pn, item_data in data.items():
            part_number = pn.format(color_id=color_id)
            description = item_data['description'].format(color=color)
            min_awg = item_data['min_awg']
            max_awg = item_data['max_awg']
            min_diameter = item_data['min_diameter']
            max_diameter = item_data['max_diameter']
            image = item_data['image_url'].format(color_id=color_id)
            length = 5.0
            weight = 0.0
            datasheet = None
            cad = None
            has_label = 0

            family = None
            series = None

            min_temp = None
            max_temp = None

            res.append(
                dict(
                    part_number=part_number,
                    description=description,
                    mfg=mfg,
                    family=family,
                    series=series,
                    color=color,
                    image=image,
                    datasheet=datasheet,
                    cad=cad,
                    min_temp=min_temp,
                    max_temp=max_temp,
                    min_diameter=min_diameter,
                    max_diameter=max_diameter,
                    min_awg=min_awg,
                    max_awg=max_awg,
                    length=length,
                    weight=weight,
                    has_label=has_label
                    )
                )

    data = {
        'SH CT 3/32K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 3/32" Shrink Label',
            'min_diameter': 0.79,
            'max_diameter': 2.36,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20quarter%20inch%20fixed_thumbnail.jpg'

        },
        'SH CT 1/8K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 1/8" Shrink Label',
            'min_diameter': 1.07,
            'max_diameter': 3.18,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20quarter%20inch%20fixed_thumbnail.jpg'

        },
        'SH CT 3/16K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 3/16" Shrink Label',
            'min_diameter': 1.57,
            'max_diameter': 4.75,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20quarter%20inch%20fixed_thumbnail.jpg'

        },
        'SH CT 1/4K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 1/4" Shrink Label',
            'min_diameter': 6.35,
            'max_diameter': 2.11,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20quarter%20inch%20fixed_thumbnail.jpg'

        },
        'SH CT 3/8K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 3/8" Shrink Label',
            'min_diameter': 3.18,
            'max_diameter': 9.53,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20quarter%20inch%20fixed_thumbnail.jpg'

        },
        'SH CT 1/2K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 1/2" Shrink Label',
            'min_diameter': 4.22,
            'max_diameter': 12.7,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20half%20inch_thumbnail.jpg'

        },
        'SH CT 3/4K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 3/4" Shrink Label',
            'min_diameter': 6.35,
            'max_diameter': 19.05,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%20half%20inch_thumbnail.jpg'

        },
        'SH CT 1K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 1" Shrink Label',
            'min_diameter': 8.46,
            'max_diameter': 25.4,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%201K%20updated_thumbnail.jpg'

        },
        'SH CT 1-1/2K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 1-1/2" Shrink Label',
            'min_diameter': 19.05,
            'max_diameter': 38.1,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%201K%20updated_thumbnail.jpg'

        },
        'SH CT 2K': {
            'min_awg': None,
            'max_awg': None,
            'description': 'Custom 2" Shrink Label',
            'min_diameter': 25.4,
            'max_diameter': 50.8,
            'image_url': 'https://www.milspecwiring.com/assets/images/thumbnails/SH%20TRAC%201K%20updated_thumbnail.jpg'

        }
    }

    for part_number, item_data in data.items():
        description = item_data['description']
        min_awg = item_data['min_awg']
        max_awg = item_data['max_awg']
        has_label = 1
        min_diameter = item_data['min_diameter']
        max_diameter = item_data['max_diameter']
        image = item_data['image_url']
        length = -1.0
        weight = 0.0
        datasheet = None
        cad = None
        color = 'Transparent'

        family = None
        series = None

        min_temp = None
        max_temp = None

        res.append(
            dict(
                part_number=part_number,
                description=description,
                mfg=mfg,
                family=family,
                series=series,
                color=color,
                image=image,
                datasheet=datasheet,
                cad=cad,
                min_temp=min_temp,
                max_temp=max_temp,
                min_diameter=min_diameter,
                max_diameter=max_diameter,
                min_awg=min_awg,
                max_awg=max_awg,
                length=length,
                weight=weight,
                has_label=has_label
                )
            )

    return res


print(json.dumps(_build_wire_markers(), indent=4))
