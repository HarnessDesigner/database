# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Decide which table a TE product belongs to.

TE's category alone is not enough: one category holds several kinds of part (602 of the "Standard Rectangular Connectors" are
caps, "Connector Hardware" holds latches, position assurance and mounting parts, a hood and its base are one category).
So a product is placed by its category AND its own features. ``classify`` returns ``(table, reason)``: the table is ``None``
for a product that is left out, and the reason says why, so the converter can count what was dropped.
"""

from te_product import Product


# Connector categories that can be a harness connector. The board level test below applies to all of them except the ones in
# ALWAYS_HARNESS, which are wire connectors by their nature.
CONNECTOR_CATEGORIES = {
    'Automotive Housings', 'Data Connectivity Housings', 'Crimp Terminal Housings', 'Standard Rectangular Connectors',
    'Standard Circular Connectors', 'D-Shaped Connectors', 'Circular Power Connectors', 'Coax Connectors',
    'Ribbon Cable Connectors', 'Rectangular Connector Hoods & Bases', 'Automotive Headers', 'Data Connectivity Headers',
    'PCB Headers & Receptacles', 'RJ45 Connectors', 'RJ11 Connectors', 'RJ14 Connectors', 'RJ22 Connectors',
    'RJ25 Connectors', 'RJ Point Five Connectors', 'USB Connectors', 'HDMI Connectors', 'DisplayPort Connectors',
    'IEEE 1394 Connectors', 'FPC Connectors', 'FFC Connectors', 'Poke-In Connectors', 'Internal I/O Connectors',
    'Plug & Socket Lighting Connectors', 'Industrial Mini I/O Connectors', 'Busbar Connectors', 'Rack & Panel Connectors',
    'Backplane Power Connectors', 'Card Edge Power Connectors', 'Street Lighting Connectors', 'Street Lighting Receptacles',
    'Ballast Connectors', 'DC Jack Connectors', 'Docking Connectors', 'High Speed Pluggable IO Connectors & Cages',
    'SAS & MiniSAS', 'SATA & Micro SATA', 'Eurocard Connectors', 'Hard Metric Backplane Connectors',
    'High Speed Backplane Connectors', 'Standard Edge Connectors', 'PCI & PCI Express Connectors', 'M.2 Connectors',
    'Two-Piece Edge Connectors', 'Combo Jacks', 'Panel & PCB Outlets', 'Board-In Connectors', 'Wire-to-Board Jumpers & Shunts',
    'Board-to-Board Jumpers & Shunts', 'Card Edge Connector Housings', 'Backplane Connector Housings', 'SDL Connectors',
    'HSSDC2 Connectors', 'DIN Connectors', 'SIM Card Connectors', 'Smart Card Connectors', 'SD Card Connectors',
    'CompactFlash Connectors', 'Mini PCI Express & mSATA',
}
ALWAYS_HARNESS = {
    'Automotive Housings', 'Data Connectivity Housings', 'Crimp Terminal Housings', 'Standard Rectangular Connectors',
    'Standard Circular Connectors', 'D-Shaped Connectors', 'Circular Power Connectors', 'Coax Connectors',
    'Ribbon Cable Connectors', 'Rectangular Connector Hoods & Bases',
}

# terminals; a contact category can hold board level contacts, the others are wire terminals by their nature
TERMINAL_CATEGORIES = {
    'Automotive Terminals', 'Connector Contacts', 'RF Contacts', 'Ring Terminals', 'Spade Terminals', 'Quick Disconnects',
    'Crimp Wire Pins, Tabs & Ferrules', 'Magnet Wire Terminals', 'Power Terminals', 'Special Purpose Terminals',
    'Foil Terminals', 'Knife Disconnects', 'PCB Terminals', 'Junction Contacts',
}
WIRE_TERMINALS = TERMINAL_CATEGORIES - {'Automotive Terminals', 'Connector Contacts', 'RF Contacts', 'PCB Terminals'}

SPLICE_CATEGORIES = {'Splices', 'Junction Splices', 'Cable-to-Cable Splicing'}
SEAL_CATEGORIES = {'Connector Seals & Cavity Plugs', 'Cable Entry Seals'}
COVER_CATEGORIES = {'Automotive Connector Caps & Covers', 'Connector Caps & Covers', 'Connector Backshells', 'Heat Shrink Caps'}
BOOT_CATEGORIES = {'Heat Shrink Boots', 'EMI Shielded Boots', 'Connector Strain Relief', 'Insulation Boots & Sleeves'}
WIRE_CATEGORIES = {
    'Twisted Pair Cable', 'Hook Up Wire', 'Power Cable', 'High Speed Digital & Data Cable', 'Sensor Cable', 'Primary Wire',
    'Multicore Cable', 'Ribbon & Flat Cable',
}
ACCESSORY_CATEGORIES = {
    'Connector Hardware', 'Other Automotive Connector Accessories', 'Automotive Connector EMC Shielding', 'Cable Ties',
    'Cable Tie Mounts & Accessories',
}
LOCK_CATEGORY = 'Automotive Connector Locks & Position Assurance'
TRANSITION_CATEGORY = 'Cable Transitions & Breakouts'
SOLDERSLEEVE_CATEGORY = 'SolderSleeve Shield Terminators'

# Energy & Power categories that attach to a wire or cable (user, 2026-11-04). A part that joins two wires with the connection
# in the middle of one of them is a splice, any other part that is fitted to a wire is a terminal; a connector that takes two or
# more wires is a housing.
COMPRESSION_CATEGORY = 'Compression Connectors'
TERMINATION_CATEGORY = 'Power Cable Terminations'
JOINT_CATEGORY = 'Joints & Splices'
WEDGE_CATEGORY = 'Wedge Connectors'
INSERT_CATEGORY = 'Rectangular Contact Inserts'
COMPRESSION_SPLICES = ('Splice', 'Sleeve', 'Branch Connector')

TPA_TYPES = ('TPA (Terminal Position Assurance)', 'Secondary Lock', 'Retainer', 'Double Lock Plate')
CPA_TYPES = ('CPA (Connector Position Assurance)', 'Latch Arm')

_WIRE_WORDS = ('wire', 'cable', 'bus bar', 'busbar', 'coax', 'tube')


def wire_side(product: Product) -> bool | None:
    """Does the part take part in a wire or cable connection? ``None`` when the part says nothing about it.

    A connector's ``Connector System`` is ``Wire-to-Board``, ``Cable-to-Panel``, ``Board-to-Board`` ...; a contact says what it
    ``Terminates To``.
    """
    system = product.first('Connector System')

    if system:
        return any(word in system.lower() for word in _WIRE_WORDS)

    for label in ('Connector & Contact Terminates To', 'Product Terminates To'):
        values = product.values(label)

        if values:
            return any(word in value.lower() for value in values for word in _WIRE_WORDS)

    return None


def classify(product: Product) -> tuple[str | None, str]:
    """``(table, reason)``; the table is ``None`` when the product is left out."""
    category = product.category

    if product.part_type == 'model':
        return None, 'family page (model), not a part'

    if not product.part_number:
        return None, 'no part number'

    if category == TRANSITION_CATEGORY:
        return 'transitions', ''

    if category in WIRE_CATEGORIES:
        return 'wires', ''

    if category == LOCK_CATEGORY:
        kind = product.first('Connector & Contact Retention Accessory Type')

        if kind in TPA_TYPES:
            return 'tpa_locks', ''

        if kind in CPA_TYPES:
            return 'cpa_locks', ''

        return 'accessories', f'lock of another kind ({kind}) kept as an accessory'

    if category in SPLICE_CATEGORIES:
        return 'splices', ''

    if category == SOLDERSLEEVE_CATEGORY:
        if product.first('Interconnect Device Splice Type') == 'SolderSleeve':
            return 'splices', ''

        return 'terminals', 'shield / wire terminator kept as a terminal'

    if category == COMPRESSION_CATEGORY:
        if product.first('Compression Connector Product Type') in COMPRESSION_SPLICES:
            return 'splices', 'compression connector that joins wires, kept as a splice'

        return 'terminals', 'compression connector kept as a terminal'

    if category == TERMINATION_CATEGORY:
        cores = product.span('Number of Cores')

        if cores is None:
            return 'terminals', 'power cable termination without a core count, kept as a terminal'

        if cores[1] >= 2:
            return 'housings', 'power cable termination of 2 or more cores, kept as a housing'

        return 'terminals', 'single core power cable termination kept as a terminal'

    if category == JOINT_CATEGORY:
        kind = product.first('Joints & Splice Product Type') or ''

        if kind in ('Live End Seal', 'Motor Connection Kit'):
            return 'terminals', f'{kind} is fitted to the end of a cable, kept as a terminal'

        if 'joint' in kind.lower() or (not kind and 'joint' in product.description.lower()):
            return 'splices', 'cable joint kept as a splice'

        return None, 'cable link box, not a wire connection'

    if category == WEDGE_CATEGORY:
        return 'splices', 'wedge connector taps a wire, kept as a splice'

    if category == INSERT_CATEGORY:
        # an insert holds the contacts of a connector and takes the wires: a housing. It has a wire size, so only an insert that
        # says it terminates to a board is left out.
        if wire_side(product) is False:
            return None, 'board level contact insert (terminates to a board)'

        return 'housings', 'contact insert kept as a housing'

    if category in SEAL_CATEGORIES:
        return 'seals', ''

    if category in BOOT_CATEGORIES:
        return 'boots', ''

    if category == 'Heat Shrink Tubing':
        if product.first('Tubing Product Type') == 'Heat Shrink Tubing':
            return 'bundles', ''

        return None, 'heat shrink kit / edging, not tubing'

    if category in ACCESSORY_CATEGORIES:
        return 'accessories', ''

    if category in TERMINAL_CATEGORIES:
        if category not in WIRE_TERMINALS and wire_side(product) is False:
            return None, 'board level contact (terminates to a board)'

        return 'terminals', ''

    if category in COVER_CATEGORIES:
        return 'covers', ''

    if category in CONNECTOR_CATEGORIES:
        housing_type = product.first('Connector & Housing Type')

        # a cap is a cover whatever the category says
        if housing_type == 'Cap':
            return 'covers', ''

        if category == 'Rectangular Connector Hoods & Bases':
            kind = product.first('Hood & Base Connector Product Type')

            if kind in ('Hood', 'Cover'):
                return 'covers', ''

            return 'housings', ''

        if category not in ALWAYS_HARNESS and wire_side(product) is not True:
            return None, 'board level connector (no wire or cable side)'

        return 'housings', ''

    return None, 'category is not wire harness material'
