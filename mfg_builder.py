

import json


def _build_mfgs():

    data = (
        (0, 'None', '', '', '', ''),
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
        (7, 'Milspecwiring.com', '', '', '', 'https://www.milspecwiring.com'),
    )


    res = []
    for id, name, phone, address, email, website in data:
        ext = ''
        contact_person = ''
        description = ''


        res.append(dict(id=id, name=name, description=description, address=address, phone=phone, ext=ext, email=email, website=website))

    return res


print(json.dumps(_build_mfgs(), indent=4))
