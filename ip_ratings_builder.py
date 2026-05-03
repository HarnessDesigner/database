IP_SOLIDS = [
    # (id, code, name, description)
    (0, "0", "No protection",
     "No protection against solid objects or contact."),
    (1, "1", "≥50 mm objects",
     "Protected against solid objects ≥50 mm (e.g. back of a hand). "
     "Does not protect against deliberate contact."),
    (2, "2", "≥12.5 mm objects",
     "Protected against solid objects ≥12.5 mm (e.g. a finger)."),
    (3, "3", "≥2.5 mm objects",
     "Protected against solid objects ≥2.5 mm (tools, thick wires)."),
    (4, "4", "≥1 mm objects",
     "Protected against solid objects ≥1 mm (most wires and small screws)."),
    (5, "5", "Dust-protected",
     "Dust-protected. Ingress is not fully prevented but dust shall not "
     "enter in sufficient quantity to impair operation or safety."),
    (6, "6", "Dust-tight",
     "Dust-tight. No ingress of dust under a vacuum of 20 mbar below "
     "ambient applied for 8 hours. Complete contact protection."),
    (7, "X", "Not rated / not tested",
     "Not rated for solid particle ingress. No claim is made; absence of "
     "a rating does not imply no protection."),
]

IP_LIQUIDS = [
    # (id, code, name, description)
    (0, "0", "No protection",
     "No protection against liquid ingress."),
    (1, "1", "Dripping water (vertical)",
     "Protected against vertically dripping water when mounted normally. "
     "Test: 1 mm/min for 10 min."),
    (2, "2", "Dripping water (tilted ±15°)",
     "Protected against vertically dripping water when tilted up to 15° "
     "from normal. Test: 3 mm/min, 2.5 min per quadrant (4 positions)."),
    (3, "3", "Spraying water (up to 60° from vertical)",
     "Protected against water sprayed up to 60° from vertical. "
     "Test: oscillating fixture ±60°, 0.7 L/min per nozzle, 5 min."),
    (4, "4", "Splashing water (all directions)",
     "Protected against water splashing from any direction. "
     "Test: oscillating fixture 360°, 10 L/min, 10 min."),
    (5, "5", "Water jets (6.3 mm nozzle, any direction)",
     "Protected against water jets from a 6.3 mm nozzle at any angle. "
     "Test: 12.5 L/min at 30 kPa, nozzle 2.5–3 m, at least 3 min."),
    (6, "6", "Powerful water jets (12.5 mm nozzle, any direction)",
     "Protected against powerful water jets from a 12.5 mm nozzle. "
     "Test: 100 L/min at 100 kPa, nozzle 2.5–3 m, at least 3 min."),
    (7, "7", "Temporary immersion (up to 1 m / 30 min)",
     "Protected against temporary immersion to 1 m for 30 min."),
    (8, "8", "Continuous immersion (beyond 1 m, manufacturer-specified)",
     "Protected against continuous immersion beyond 1 m. Exact depth and "
     "duration must be declared by the manufacturer — two IP68 products "
     "may be tested at very different conditions."),
    (9, "9K", "High-pressure high-temperature jet (steam wash-down)",
     "Protected against steam/pressure jet wash-down per DIN 40050-9 / "
     "ISO 20653 (K = Kraftfahrzeug). "
     "Test: 80 °C water, 8–10 MPa (80–100 bar), 14–16 L/min, nozzle "
     "100–150 mm, 30 s per angle at 0°/30°/60°/90°. "
     "IP69K ≠ IP68: they test entirely different hazards. An IP69K "
     "enclosure may not survive prolonged submersion."),
    (10, "6K", "High-pressure water jets — automotive (6.3 mm nozzle)",
     "Protected against high-pressure water jets per DIN 40050-9 / ISO 20653 "
     "(K = Kraftfahrzeug). Uses a 6.3 mm nozzle at 1000 kPa — NOT simply a "
     "higher tier of IPx6. Passing IPx6 does NOT imply passing IPx6K. "
     "Test: 75 L/min at 1000 kPa, nozzle 150–200 mm, at least 3 min."),
    (11, "4K", "Splashing water — automotive elevated flow rate",
     "Protected against splashing water at elevated flow rate "
     "(automotive variant per ISO 20653 / DIN 40050-9). "
     "Distinct from IPx4; the K denotes Kraftfahrzeug (motor vehicle origin)."),
    (12, "X", "Not rated / not tested",
     "Not rated for liquid ingress. No claim is made."),
    # plain digit 9 (IEC 60529 native, rarely used standalone)
    (13, "9", "High-pressure / high-temperature water jets (IEC 60529 digit)",
     "Protected against high-pressure/high-temperature water jets per "
     "IEC 60529. Verify whether the manufacturer intends IPx9K "
     "(ISO 20653 automotive test) rather than the plain digit 9."),
]

# id chosen to match ASCII value offset: A=0,B=1,C=2,D=3,H=4,M=5,S=6,W=7
IP_SUPPLEMENTARY = [
    # (id, code, name, description)
    (0, "A", "Back of hand",
     "Additional touch protection: back of hand (50 mm sphere probe, >50 mm depth)."),
    (1, "B", "Finger",
     "Additional touch protection: finger (12 mm diameter, 80 mm long probe)."),
    (2, "C", "Tool",
     "Additional touch protection: tool (2.5 mm diameter, 100 mm long probe)."),
    (3, "D", "Wire",
     "Additional touch protection: wire (1 mm diameter, 100 mm long probe)."),
    (4, "H", "High-voltage apparatus",
     "High-voltage apparatus."),
    (5, "M", "Moving (during water test)",
     "Moving parts were in motion during the water ingress test."),
    (6, "S", "Stationary (during water test)",
     "Moving parts were stationary during the water ingress test "
     "(explicit statement of the default condition)."),
    (7, "W", "Weather conditions",
     "Suitable for specified weather conditions; additional protective "
     "features or processes are provided."),
]


import json


# Enumerate all standard IP ratings (no supplementary/additional letters).
# The combinatorial space is solid(0-6,X) × liquid(0-9,9K,6K,4K,X) = 8×13 = 104
# We only store the practically meaningful ones used in real products + conversions.
# The query layer handles all combinations dynamically; this table is a pre-built
# index of real ratings encountered in conversion tables and common practice.
# Supplementary/additional variants are derived at query time from the name string.

def _build_ip_ratings():
    """Return rows for ip_ratings covering all single-digit combinations
    plus the K-variants and X placeholders."""
    solid_codes  = ["0","1","2","3","4","5","6","X"]
    liquid_codes = ["0","1","2","3","4","5","6","7","8","9","9K","6K","4K","X"]

    solid_id = {r[1]: r[0] for r in IP_SOLIDS}
    liquid_id = {r[1]: r[0] for r in IP_LIQUIDS}
    supp_id = {r[1]: r[0] for r in IP_SUPPLEMENTARY}

    rows = []
    for sc in solid_codes:
        for lc in liquid_codes:
            name = f"IP{sc}{lc}"
            rows.append(dict(name=name, solid_id=solid_id[sc], liquid_id=liquid_id[lc], supp1_id=None, supp2_id=None))

    # Supplementary variants for the most-used base ratings
    # (name, solid_code, liquid_code, supp1_code, supp2_code)
    supp_variants = [
        ("IP54BM", "5", "4", "B", "M"),
        ("IP54BS", "5", "4", "B", "S"),
        ("IP54AM", "5", "4", "A", "M"),
        ("IP54CM", "5", "4", "C", "M"),
        ("IP55BM", "5", "5", "B", "M"),
        ("IP65BM", "6", "5", "B", "M"),
        ("IP66BM", "6", "6", "B", "M"),
        ("IP67BM", "6", "7", "B", "M"),
        ("IP68BM", "6", "8", "B", "M"),
        ("IP44BM", "4", "4", "B", "M"),
        ("IP54HM", "5", "4", "H", "M"),
        ("IP55HS", "5", "5", "H", "S"),
        ("IP65HS", "6", "5", "H", "S"),
        ("IP54W",  "5", "4", "W", None),
        ("IP65W",  "6", "5", "W", None),
    ]
    for (name, sc, lc, s1c, s2c) in supp_variants:
        rows.append(dict(
            name=name,
            solid_id=solid_id[sc],
            liquid_id=liquid_id[lc],
            supp1_id=supp_id.get(s1c),
            supp2_id=supp_id.get(s2c) if s2c else None,
        ))
    return rows


ip_solids = []
for id, code, name, description in IP_SOLIDS:
    ip_solids.append(dict(id=id, code=code, name=name, description=description))


with open('ip_solids.json', 'w') as f:
    f.write(json.dumps(ip_solids, indent=4))


ip_liquids = []
for id, code, name, description in IP_LIQUIDS:
    ip_liquids.append(dict(id=id, code=code, name=name, description=description))


with open('ip_liquids.json', 'w') as f:
    f.write(json.dumps(ip_liquids, indent=4))


ip_supps = []
for id, code, name, description in IP_SUPPLEMENTARY:
    ip_supps.append(dict(id=id, code=code, name=name, description=description))


with open('ip_supps.json', 'w') as f:
    f.write(json.dumps(ip_supps, indent=4))


with open('ip_ratings.json', 'w') as f:
    f.write(json.dumps(_build_ip_ratings(), indent=4))


IK_LEVELS = [
    # (id, code, name, energy_j, mass_kg, height_mm, hammer_type, striker,
    #  description, test_detail, typical_use, sector_note)
    (0, "00", "No protection (unrated)", None, None, None, None, None,
     "No impact protection. IK00 is an affirmative no-protection declaration, "
     "not merely 'untested'. Absence of any IK marking on a datasheet implies IK00.",
     "No test conducted. IK00 is an explicit no-protection declaration, "
     "not simply 'not yet tested'.",
     "Delicate bench instruments; items always housed inside a secondary enclosure.",
     None),

    (1, "01", "0.15 J impact protection", 0.15, 0.2, 75,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 0.15 J impact (200 g dropped from 75 mm). "
     "Very light accidental contact only.",
     "Impact energy 0.15 J: 0.2 kg dropped from 75 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Light indoor equipment with minimal accidental contact risk.",
     None),

    (2, "02", "0.2 J impact protection", 0.2, 0.2, 100,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 0.2 J impact (200 g dropped from 100 mm).",
     "Impact energy 0.2 J: 0.2 kg dropped from 100 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Consumer electronics in protected indoor environments.",
     None),

    (3, "03", "0.35 J impact protection", 0.35, 0.2, 175,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 0.35 J impact (200 g dropped from 175 mm).",
     "Impact energy 0.35 J: 0.2 kg dropped from 175 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Office and commercial equipment with low accidental impact risk.",
     None),

    (4, "04", "0.5 J impact protection", 0.5, 0.2, 250,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 0.5 J impact (200 g dropped from 250 mm). "
     "Common threshold for general indoor commercial and light-industrial enclosures.",
     "Impact energy 0.5 J: 0.2 kg dropped from 250 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Light-industrial control panels, commercial equipment.",
     "IEC 60598 (luminaires): IK04 acceptable for non-public indoor luminaires."),

    (5, "05", "0.7 J impact protection", 0.7, 0.2, 350,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 0.7 J impact (200 g dropped from 350 mm).",
     "Impact energy 0.7 J: 0.2 kg dropped from 350 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Moderate-duty indoor enclosures, building-automation panels.",
     None),

    (6, "06", "1 J impact protection", 1.0, 0.5, 200,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 1 J impact (500 g dropped from 200 mm). "
     "Hammer mass doubles from 200 g to 500 g at this level — a design threshold. "
     "Commonly the minimum for public-access equipment.",
     "Impact energy 1 J: 0.5 kg dropped from 200 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "ATMs, vending machines, wall-mounted distribution boards.",
     "IEC 60598: IK06 minimum for standard indoor luminaires."),

    (7, "07", "2 J impact protection", 2.0, 0.5, 400,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 2 J impact (500 g dropped from 400 mm). "
     "Common for outdoor street furniture, metering, and telecom cabinets.",
     "Impact energy 2 J: 0.5 kg dropped from 400 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Outdoor cabinets, utility metering, street furniture, telecom junction boxes.",
     "IEC 60598: IK07 for indoor luminaires in moderate-vandalism locations."),

    (8, "08", "5 J impact protection", 5.0, 1.7, 300,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 5 J impact (1.7 kg dropped from 300 mm) — "
     "approximately the energy of a moderate hammer blow. "
     "Hammer mass jumps from 0.5 kg to 1.7 kg at this level. "
     "IK08 is the most widely-specified industrial and outdoor level.",
     "Impact energy 5 J: 1.7 kg dropped from 300 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Industrial switchgear, machine guards, outdoor public luminaires, "
     "railway trackside, traffic control.",
     "IEC 60598: IK08 minimum for luminaires mounted below 2.5 m in public areas."),

    (9, "09", "10 J impact protection", 10.0, 5.0, 200,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 10 J impact (5 kg dropped from 200 mm) — "
     "comparable to a deliberate hard kick or thrown hand tool. "
     "Hammer mass jumps from 1.7 kg to 5.0 kg at this level.",
     "Impact energy 10 J: 5.0 kg dropped from 200 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "High-vandalism environments (car parks, transit), heavy-duty industrial, mining.",
     None),

    (10, "10", "20 J impact protection", 20.0, 5.0, 400,
     "Eh2 pendulum or Eh3 free-fall (IEC 60068-2-75)",
     "10 mm polyamide hemisphere",
     "Protected against 20 J impact (5 kg dropped from 400 mm) — "
     "the maximum IK classification; energy of a heavy deliberate blow. "
     "Note: 'IK10+' or 'IK11' markings are not part of IEC 62262 and have "
     "no standardised meaning; request the actual test energy and report.",
     "Impact energy 20 J: 5.0 kg dropped from 400 mm "
     "(Eh2 pendulum or Eh3 free-fall per IEC 60068-2-75). "
     "Striker: 10 mm polyamide hemisphere. "
     "Procedure: 3 blows at 3 points on every significant face at 15–35 °C. "
     "Pass criterion: no damage that compromises the declared IP rating "
     "or allows access to live/hazardous parts.",
     "Anti-vandal street furniture, secure/prison facilities, "
     "blast-resistant switchgear, offshore/marine heavy machinery guards.",
     None),
]


ik_ratings = []
for id, code, name, energy_j, mass_kg, height_mm, hammer_type, striker, description, test_detail, typical_use, sector_note in IK_LEVELS:
    ik_ratings.append(dict(id=id, code=code, name=name, energy_j=energy_j, mass_kg=mass_kg,
                           height_mm=height_mm, hammer_type=hammer_type, striker=striker,
                           description=description, test_detail=test_detail, typical_use=typical_use,
                           sector_note=sector_note))

with open('ik_ratings.json', 'w') as f:
    f.write(json.dumps(ik_ratings, indent=4))



# NEMA rows: (name, solid_desc, liquid_desc, special_text_or_None, note_text)
NEMA_ROWS = [
    ("1",
     "General-purpose indoor. Protects against incidental contact with "
     "enclosed equipment and against falling dirt.",
     "No liquid protection beyond falling-dirt exclusion.",
     None,
     "Approximate IP floor: IP20."),
    ("2",
     "Drip-proof indoor. Protects against falling dirt and dripping "
     "and light splashing of non-corrosive liquids.",
     "Drip and light splash, non-corrosive; not hose-directed.",
     None,
     "Approximate IP floor: IP21."),
    ("3",
     "Weatherproof outdoor. Protects against windblown dust, rain, and sleet.",
     "Rain and sleet from any angle; windblown dust excluded.",
     "Enclosure must remain operable while externally iced.",
     "Approximate IP floor: IP54."),
    ("3R",
     "Rainproof outdoor. Protects against falling rain and sleet; "
     "windblown-dust protection not required.",
     "Rain and sleet; less stringent than NEMA 3 for dust.",
     "Operable while externally iced.",
     "Approximate IP floor: IP44."),
    ("3S",
     "Weatherproof outdoor, same protection as NEMA 3. "
     "External operating mechanism must remain operable while iced.",
     "Rain, sleet, windblown dust.",
     "External mechanism (e.g. handle, interlock) operable while externally iced.",
     "Approximate IP floor: IP54."),
    ("3X",
     "Corrosion-resistant variant of NEMA 3.",
     "Rain, sleet, windblown dust.",
     "Corrosion-resistant construction required.",
     "Approximate IP floor: IP54."),
    ("3RX",
     "Corrosion-resistant variant of NEMA 3R.",
     "Rain and sleet.",
     "Corrosion resistant.",
     "Approximate IP floor: IP44."),
    ("3SX",
     "Corrosion-resistant variant of NEMA 3S.",
     "Rain, sleet, windblown dust.",
     "Corrosion resistant; external mechanism operable while iced.",
     "Approximate IP floor: IP54."),
    ("4",
     "Indoor or outdoor. Protects against windblown dust and rain, "
     "splashing water, and hose-directed water.",
     "Hose-directed water (~450 kPa) from any direction. Operable while externally iced.",
     "Not corrosion-resistant — see NEMA 4X.",
     "Approximate IP floor: IP66. NEMA 4 exceeds IP66 due to hose and ice tests."),
    ("4X",
     "Same environmental protection as NEMA 4 with corrosion resistance added. "
     "Indoor or outdoor.",
     "Hose-directed water (~450 kPa), rain, dust. Operable while iced.",
     "Corrosion-resistant construction (stainless steel, fibreglass, or equivalent). "
     "Widely used in food/beverage and marine environments.",
     "Approximate IP floor: IP66."),
    ("5",
     "Indoor only. Protects against settling airborne dust, lint, fibres, "
     "and flyings. Drip-tight.",
     "Drip-tight against non-corrosive falling liquids; not hose or splash rated.",
     "External oil and coolant drip resistant.",
     "Approximate IP floor: IP52."),
    ("6",
     "Indoor or outdoor. Protects against entry of water during occasional "
     "temporary submersion.",
     "Temporary submersion at limited depth. Operable while externally iced.",
     None,
     "Approximate IP floor: IP67."),
    ("6P",
     "Indoor or outdoor. Protects against entry of water during prolonged "
     "submersion at depth.",
     "Prolonged submersion. Operable while externally iced.",
     None,
     "Approximate IP floor: IP68 (manufacturer must specify depth and duration)."),
    ("12",
     "Industrial indoor. Protects against dust, dirt, fibres, and dripping "
     "non-corrosive liquids.",
     "Drip-tight; protects against seepage of oil and coolants. No knockouts.",
     "See NEMA 12K for the knockout variant.",
     "Approximate IP floor: IP54."),
    ("12K",
     "Same as NEMA 12 with knockouts permitted.",
     "Drip-tight; oil and coolant seepage resistant.",
     "Knockouts permitted.",
     "Approximate IP floor: IP54."),
    ("13",
     "Indoor only. Protects against dust and against spraying of water, "
     "oil, and non-corrosive coolants.",
     "Oil-spray and coolant-spray resistant; not hose-directed water.",
     "Higher oil/coolant spray resistance than NEMA 12.",
     "Approximate IP floor: IP54."),
]

nema_ratings = []
for name, solid_desc, liquid_desc, notes, _ in NEMA_ROWS:
    nema_ratings.append(dict(name=name, solid_desc=solid_desc, liquid_desc=liquid_desc, notes=notes))

with open('nema_ratings.json', 'w') as f:
    f.write(json.dumps(nema_ratings, indent=4))


UL_ROWS = [
    ("1",
     "UL 50 Type 1 — general-purpose indoor, falling dirt.",
     "No liquid protection.",
     None,
     "Equivalent to NEMA 1. Approximate IP floor: IP20."),
    ("2",
     "UL 50 Type 2 — drip-proof indoor.",
     "Dripping and light splashing of non-corrosive liquids.",
     None,
     "Equivalent to NEMA 2. Approximate IP floor: IP21."),
    ("3",
     "UL 50 Type 3 — outdoor, windblown dust, rain, sleet.",
     "Rain and sleet from any angle.",
     "Operable while externally iced.",
     "Equivalent to NEMA 3. Approximate IP floor: IP54."),
    ("3R",
     "UL 50 Type 3R — outdoor, rain, sleet; no windblown-dust requirement.",
     "Rain and sleet.",
     "Operable while iced.",
     "Equivalent to NEMA 3R. Approximate IP floor: IP44."),
    ("3S",
     "UL 50 Type 3S — outdoor, windblown dust, rain, sleet; "
     "mechanism operable while iced.",
     "Rain, sleet, windblown dust.",
     "External mechanism operable while iced.",
     "Equivalent to NEMA 3S. Approximate IP floor: IP54."),
    ("3X",
     "UL 50 Type 3X — corrosion-resistant variant of Type 3.",
     "Rain, sleet, windblown dust.",
     "Corrosion resistant.",
     "Equivalent to NEMA 3X. Approximate IP floor: IP54."),
    ("3RX",
     "UL 50 Type 3RX — corrosion-resistant variant of Type 3R.",
     "Rain and sleet.",
     "Corrosion resistant.",
     "Equivalent to NEMA 3RX. Approximate IP floor: IP44."),
    ("3SX",
     "UL 50 Type 3SX — corrosion-resistant; mechanism operable while iced.",
     "Rain, sleet, windblown dust.",
     "Corrosion resistant; external mechanism operable while iced.",
     "Equivalent to NEMA 3SX. Approximate IP floor: IP54."),
    ("4",
     "UL 50 Type 4 — indoor/outdoor, windblown dust, rain, hose-directed water.",
     "Hose-directed water (~450 kPa) from any direction. Operable while iced.",
     "Not corrosion-resistant.",
     "Equivalent to NEMA 4. Approximate IP floor: IP66."),
    ("4X",
     "UL 50 Type 4X — same as Type 4 with corrosion resistance.",
     "Hose-directed water, rain, dust. Operable while iced.",
     "Corrosion resistant.",
     "Equivalent to NEMA 4X. Approximate IP floor: IP66."),
    ("5",
     "UL 50 Type 5 — indoor, settling dust, lint, drip-tight.",
     "Drip-tight non-corrosive liquids; not hose-directed.",
     "Oil and coolant drip resistant.",
     "Equivalent to NEMA 5. Approximate IP floor: IP52."),
    ("6",
     "UL 50 Type 6 — indoor/outdoor, temporary submersion.",
     "Temporary submersion. Operable while iced.",
     None,
     "Equivalent to NEMA 6. Approximate IP floor: IP67."),
    ("6P",
     "UL 50 Type 6P — indoor/outdoor, prolonged submersion.",
     "Prolonged submersion. Operable while iced.",
     None,
     "Equivalent to NEMA 6P. Approximate IP floor: IP68."),
    ("12",
     "UL 50 Type 12 — industrial indoor, dust, drip-tight, no knockouts.",
     "Drip-tight; oil and coolant seepage resistant.",
     None,
     "Equivalent to NEMA 12. Approximate IP floor: IP54."),
    ("12K",
     "UL 50 Type 12K — same as Type 12 with knockouts.",
     "Drip-tight; oil and coolant seepage resistant.",
     "Knockouts permitted.",
     "Equivalent to NEMA 12K. Approximate IP floor: IP54."),
    ("13",
     "UL 50 Type 13 — indoor, dust, oil/coolant spray resistant.",
     "Oil-spray and coolant-spray resistant; not hose-directed water.",
     None,
     "Equivalent to NEMA 13. Approximate IP floor: IP54."),
    ("508A-4",
     "UL 508A Type 4 — industrial control panels, indoor/outdoor, hose-directed water.",
     "Hose-directed water. Operable while iced.",
     "Industrial control panel rating (UL 508A scope).",
     "Equivalent to NEMA 4. Approximate IP floor: IP66."),
    ("508A-4X",
     "UL 508A Type 4X — industrial control panels, corrosion-resistant, hose-directed water.",
     "Hose-directed water. Operable while iced.",
     "Industrial control panel rating; corrosion resistant.",
     "Equivalent to NEMA 4X. Approximate IP floor: IP66."),
    ("508A-12",
     "UL 508A Type 12 — industrial control panels, indoor, dust, drip-tight.",
     "Drip-tight; oil seepage resistant.",
     "Industrial control panel rating.",
     "Equivalent to NEMA 12. Approximate IP floor: IP54."),
]

CSA_ROWS = [
    ("1",
     "CSA Type 1 — general-purpose indoor, falling dirt.",
     "No liquid protection.",
     None,
     "Equivalent to NEMA 1 / UL 50 Type 1. Approximate IP floor: IP20."),
    ("2",
     "CSA Type 2 — drip-proof indoor.",
     "Dripping and light splashing, non-corrosive.",
     None,
     "Equivalent to NEMA 2. Approximate IP floor: IP21."),
    ("3",
     "CSA Type 3 — outdoor, windblown dust, rain, sleet.",
     "Rain and sleet from any angle.",
     "Operable while externally iced.",
     "Equivalent to NEMA 3. Approximate IP floor: IP54."),
    ("3R",
     "CSA Type 3R — outdoor, rain, sleet; no dust requirement.",
     "Rain and sleet.",
     "Operable while iced.",
     "Equivalent to NEMA 3R. Approximate IP floor: IP44."),
    ("3S",
     "CSA Type 3S — outdoor, windblown dust, rain, sleet; "
     "mechanism operable while iced.",
     "Rain, sleet, windblown dust.",
     "External mechanism operable while iced.",
     "Equivalent to NEMA 3S. Approximate IP floor: IP54."),
    ("4",
     "CSA Type 4 — indoor/outdoor, windblown dust, rain, hose-directed water.",
     "Hose-directed water (~450 kPa) from any direction. Operable while iced.",
     None,
     "Equivalent to NEMA 4. Approximate IP floor: IP66."),
    ("4X",
     "CSA Type 4X — same as Type 4 with corrosion resistance.",
     "Hose-directed water, rain, dust. Operable while iced.",
     "Corrosion resistant.",
     "Equivalent to NEMA 4X. Approximate IP floor: IP66."),
    ("5",
     "CSA Type 5 — indoor, settling dust, lint, drip-tight.",
     "Drip-tight non-corrosive liquids.",
     "Oil and coolant drip resistant.",
     "Equivalent to NEMA 5. Approximate IP floor: IP52."),
    ("6",
     "CSA Type 6 — indoor/outdoor, temporary submersion.",
     "Temporary submersion. Operable while iced.",
     None,
     "Equivalent to NEMA 6. Approximate IP floor: IP67."),
    ("6P",
     "CSA Type 6P — indoor/outdoor, prolonged submersion.",
     "Prolonged submersion. Operable while iced.",
     None,
     "Equivalent to NEMA 6P. Approximate IP floor: IP68."),
    ("12",
     "CSA Type 12 — industrial indoor, dust, drip-tight, oil resistant.",
     "Drip-tight; oil and coolant seepage resistant.",
     None,
     "Equivalent to NEMA 12. Approximate IP floor: IP54."),
    ("13",
     "CSA Type 13 — indoor, dust, oil/coolant spray resistant.",
     "Oil-spray and coolant-spray resistant.",
     None,
     "Equivalent to NEMA 13. Approximate IP floor: IP54."),
]

SAE_DUST = [
    # (id, code, name, description, ip_note)
    (1, "A", "Light dust (Category A)",
     "Category A — light dust environment. Protected against settling dust "
     "in quantities representative of road use; not sealed against fine dust. "
     "Equivalent to dust-protected intent (IP5X class).",
     "Approximate IP solid digit: 5 (dust-protected)."),
    (2, "B", "Heavy dust / dust-tight (Category B)",
     "Category B — heavy dust / dust-tight. Protected against significant "
     "concentrations of fine dust typical of off-road and construction "
     "environments. Full dust exclusion is the design intent. "
     "Equivalent to dust-tight intent (IP6X class).",
     "Approximate IP solid digit: 6 (dust-tight)."),
]

SAE_WATER = [
    # (id, code, name, description, ip_note)
    (1, "I", "Drip and condensation (Category I)",
     "Water Category I — drip and condensation. Protection against water "
     "dripping vertically onto the unit and against condensation. "
     "Representative of under-cab or protected-compartment installations.",
     "Approximate IP liquid digit: 1–2 (dripping water)."),
    (2, "II", "Splash and spray (Category II)",
     "Water Category II — splash and spray. Protection against water "
     "splashing from any direction, including road spray and wash-down "
     "from adjacent components. Representative of exposed underhood or "
     "underbody locations not directly in the wheel spray path.",
     "Approximate IP liquid digit: 3–4 (spraying / splashing water)."),
    (3, "III", "Direct water jet (Category III)",
     "Water Category III — direct water jet. Protection against water "
     "projected by a nozzle from any direction, representative of "
     "pressure-washing and direct road spray. Typical for exposed "
     "underbody and chassis-mounted equipment.",
     "Approximate IP liquid digit: 5–6 (water jets)."),
    (4, "IV", "Temporary immersion (Category IV)",
     "Water Category IV — temporary immersion. Protection against "
     "submersion in water for a defined period, representative of "
     "fording or flooding conditions. "
     "Typical for axle, transmission, and driveline-adjacent electronics.",
     "Approximate IP liquid digit: 7 (temporary immersion to 1 m / 30 min)."),
]

# All 8 combinations of dust × water
SAE_RATINGS = [
    (f"{d}/{w}", d_id, w_id)
    for d, d_id in [("A", 1), ("B", 2)]
    for w, w_id in [("I", 1), ("II", 2), ("III", 3), ("IV", 4)]
]
