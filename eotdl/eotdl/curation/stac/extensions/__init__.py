from .sar import SarExtensionObject
from .raster import RasterExtensionObject
from .projection import ProjExtensionObject
from .dem import DEMExtensionObject
from .eo import EOS2ExtensionObject
from .label import LabelExtensionObject


SUPPORTED_EXTENSIONS = ('eo', 'sar', 'proj', 'raster')


type_stac_extensions_dict = {
    "sar": SarExtensionObject(),
    "eo": EOS2ExtensionObject(),
    "dem": DEMExtensionObject(),
    "raster": RasterExtensionObject(),
    "proj": ProjExtensionObject()
}
