# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""One TE product record, with safe access to its features.

TE's JSON repeats a feature in ``primaryFeatures`` and again inside a ``featureGroups`` entry, one label can be several
different features (``Wire Size`` in mm², in AWG and in CMA have different ids), a feature can exist for one part and not
for the next, and the unit is on the feature, not the value. So nothing here assumes a field exists: every getter takes a
default, and the units are converted to mm and g before a number is handed out.
"""

import re

import common


SITE = 'https://www.te.com'

NUMBER = re.compile(r'[-+]?\d*\.?\d+')
# "-65 – 150", "6 – 12", "1.65 – 1.75" (an en dash, as TE writes it)
RANGE = re.compile(r'^\s*([-+]?\d*\.?\d+)\s*[–—]\s*([-+]?\d*\.?\d+)\s*$')

_TO_MM = {'mm': 1.0, 'cm': 10.0, 'm': 1000.0, 'in': 25.4, 'ft': 304.8, 'mil': 0.0254, 'um': 0.001, 'µm': 0.001}
_TO_G = {'g': 1.0, 'kg': 1000.0, 'mg': 0.001, 'oz': 28.3495, 'lb': 453.592}


def _absolute(url: str | None) -> str | None:
    if not url:
        return None

    if url.startswith('/'):
        return SITE + url

    return url


class Product:
    """A product of TE's search answer (one entry of a page's ``products``)."""

    def __init__(self, raw: dict) -> None:
        self.raw = raw
        self._features: dict[str, list[tuple[str | None, list[str]]]] = {}
        seen = {}   # (feature id, label) -> position in self._features[label]

        features = list(raw.get('primaryFeatures') or [])

        for group in raw.get('featureGroups') or []:
            features.extend(group.get('features') or [])

        for feature in features:
            label = feature.get('label')

            if not label:
                continue

            values = [str(v.get('value')).strip() for v in feature.get('primaryValues') or [] if v.get('value') is not None]
            values = [v for v in values if v]
            unit = (feature.get('primaryUnit') or {}).get('code')
            key = (feature.get('code'), label)

            if key in seen:
                # the SAME feature again (the primary copy and the one in a group): keep the first copy that has values.
                # It must be matched by the feature id: a label can be several features (Wire Size in mm², AWG, CMA).
                position = seen[key]
                known_unit, known_values = self._features[label][position]

                if not known_values and values:
                    self._features[label][position] = (known_unit or unit, values)
                elif known_unit is None and unit:
                    self._features[label][position] = (unit, known_values)

                continue

            seen[key] = len(self._features.setdefault(label, []))
            self._features[label].append((unit, values))

    # ---------------------------------------------------------------------------------------------------- identity
    @property
    def tcpn(self) -> str:
        return str(self.raw.get('tcpn') or self.raw.get('id') or self.raw.get('marketingPartNumNormalized') or '')

    @property
    def part_number(self) -> str:
        return str(self.raw.get('marketingPartNumNormalized') or self.raw.get('tcpn') or '').strip()

    @property
    def description(self) -> str:
        return str(self.raw.get('friendlyDescription') or self.raw.get('description') or '').strip()

    @property
    def brand(self) -> str | None:
        return self.raw.get('brand')

    @property
    def status(self) -> str:
        return str(self.raw.get('status') or '')

    @property
    def part_type(self) -> str:
        """``regular``, ``derived`` or ``model`` (a family page, not a part)."""
        return str(self.raw.get('partType') or '')

    @property
    def base_category(self) -> str | None:
        return self.raw.get('baseCategory')

    @property
    def category(self) -> str:
        """The leaf category (``parentCategory``)."""
        return str(self.raw.get('parentCategory') or '')

    @property
    def family(self) -> str | None:
        trail = (self.raw.get('productFamily') or {}).get('crumbTrailItems') or []
        return trail[0].get('name') if trail else None

    @property
    def series(self) -> str | None:
        trail = (self.raw.get('seriesTrail') or {}).get('crumbTrailItems') or []
        return trail[0].get('name') if trail else None

    # ---------------------------------------------------------------------------------------------------- links
    @property
    def image(self) -> str | None:
        for key in ('images', 'primaryImages'):
            for image in self.raw.get(key) or []:
                url = image.get('imageUrl')

                if not url and image.get('path') and image.get('imageName'):
                    url = image['path'] + image['imageName']

                if url:
                    return _absolute(url)

        return None

    def _document(self, kinds: list[tuple[str, tuple[str, ...] | None]]) -> str | None:
        """The first document of the first kind that exists; a kind is (type, formats or None for any)."""
        documents = self.raw.get('documents') or []

        for doc_type, formats in kinds:
            for doc in documents:
                if doc.get('type') != doc_type or not doc.get('url'):
                    continue

                if formats is None or str(doc.get('format') or '') in formats:
                    return _absolute(doc['url'])

        return None

    @property
    def model3d(self) -> str | None:
        return self._document([('Customer View Model', ('3d_stp.zip',)), ('Customer View Model', ('3d_igs.zip',))])

    @property
    def cad(self) -> str | None:
        return self._document([('Customer Drawing', ('pdf',))])

    @property
    def datasheet(self) -> str | None:
        return self._document([('Data Sheet', ('pdf',)), ('Specification Or Standard', ('pdf',))])

    # ---------------------------------------------------------------------------------------------------- features
    def has(self, label: str) -> bool:
        return any(values for _unit, values in self._features.get(label, []))

    def values(self, label: str, unit: str | None = None) -> list[str]:
        """Every value of the first feature with this label that has any (an empty list when the part has none).

        ``unit`` picks one of several features that share a label (``Wire Size`` is separate in ``mm²``, ``AWG`` and ``CMA``).
        """
        for known_unit, values in self._features.get(label, []):
            if values and (unit is None or known_unit == unit):
                return values

        return []

    def first(self, *labels: str) -> str | None:
        """The first value of the first of ``labels`` that the part has."""
        for label in labels:
            values = self.values(label)

            if values:
                return values[0]

        return None

    def unit(self, label: str) -> str | None:
        for unit, values in self._features.get(label, []):
            if values:
                return unit

        return None

    def number(self, *labels: str, to: str | None = None) -> float | None:
        """The first number of the first of ``labels`` the part has. ``to`` is ``'mm'`` or ``'g'``: a value in another
        unit of that kind (inches, kg ...) is converted."""
        for label in labels:
            value = self.first(label)

            if value is None:
                continue

            match = NUMBER.search(value)

            if match is None:
                continue

            number = float(match.group())
            factors = _TO_MM if to == 'mm' else _TO_G if to == 'g' else None

            if factors:
                unit = (self.unit(label) or '').lower()
                number *= factors.get(unit, 1.0)

            return number

        return None

    def numbers(self, label: str, unit: str | None = None) -> list[float]:
        """The first number of every value of the feature (a wire size range lists several)."""
        found = []

        for value in self.values(label, unit):
            match = NUMBER.search(value)

            if match:
                found.append(float(match.group()))

        return found

    def span(self, *labels: str) -> tuple[float, float] | None:
        """``(min, max)`` of a value written ``"6 – 12"``; a single number is both ends."""
        for label in labels:
            value = self.first(label)

            if value is None:
                continue

            match = RANGE.match(value)

            if match:
                low, high = float(match.group(1)), float(match.group(2))
                return min(low, high), max(low, high)

            match = NUMBER.search(value)

            if match:
                return float(match.group()), float(match.group())

        return None

    def yes(self, label: str) -> bool | None:
        """``True`` for Yes / With, ``False`` for No / Without, ``None`` when the part has no such feature."""
        value = self.first(label)

        if value is None:
            return None

        return value.strip().lower() in ('yes', 'with', 'true')

    def temperatures(self) -> tuple[str | None, str | None]:
        """The minimum and maximum operating temperature as the temperatures table names them."""
        span = self.span('Operating Temperature Range')

        if span is None:
            high = self.number('Operating Temperature (Max)')
            low = self.number('Operating Temperature (Min)')
            return (common.temperature(low) if low is not None else None,
                    common.temperature(high) if high is not None else None)

        return common.temperature(span[0]), common.temperature(span[1])
