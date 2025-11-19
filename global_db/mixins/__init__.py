
from . import adhesive as _adhesive
from . import color as _color  # NOQA
from . import resource as _resource  # NOQA
from . import description as _description  # NOQA
from . import dimension as _dimension  # NOQA
from . import direction as _direction  # NOQA
from . import family as _family  # NOQA
from . import gender as _gender  # NOQA
from . import manufacturer as _manufacturer  # NOQA
from . import material as _material  # NOQA
from . import name as _name  # NOQA
from . import overlay as _overlay  # NOQA
from . import part_number as _part_number  # NOQA
from . import sealing as _sealing  # NOQA
from . import series as _series  # NOQA
from . import temperature as _temperature  # NOQA
from . import wire_size as _wire_size  # NOQA
from . import protection as _protection
from . import weight as _weight
from . import cavity_lock as _cavity_lock
from . import model3d as _model3d


ColorMixin = _color.ColorMixin
ResourceMixin = _resource.ResourceMixin
DescriptionMixin = _description.DescriptionMixin
DimensionMixin = _dimension.DimensionMixin
DirectionMixin = _direction.DirectionMixin
FamilyMixin = _family.FamilyMixin
GenderMixin = _gender.GenderMixin
ManufacturerMixin = _manufacturer.ManufacturerMixin
MaterialMixin = _material.MaterialMixin
NameMixin = _name.NameMixin
OverlayMixin = _overlay.OverlayMixin
PartNumberMixin = _part_number.PartNumberMixin
SealingMixin = _sealing.SealingMixin
SeriesMixin = _series.SeriesMixin
TemperatureMixin = _temperature.TemperatureMixin
WireSizeMixin = _wire_size.WireSizeMixin
AdhesiveMixin = _adhesive.AdhesiveMixin
ProtectionMixin = _protection.ProtectionMixin
WeightMixin = _weight.WeightMixin
CavityLockMixin = _cavity_lock.CavityLockMixin
Model3DMixin = _model3d.Model3DMixin


del _adhesive
del _color
del _description
del _dimension
del _direction
del _family
del _gender
del _resource
del _manufacturer
del _material
del _name
del _overlay
del _part_number
del _sealing
del _series
del _temperature
del _wire_size
del _protection
del _weight
del _cavity_lock
del _model3d
