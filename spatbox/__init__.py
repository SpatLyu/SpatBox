__version__ = "0.1.8",
__author__ = "SpatLyu"

import os
os.environ['USE_PYGEOS'] = '0'
import geopandas
import spatbox as stx
from . import vector
from . import raster 
from . import analysis 
from . import utils
from rasterio.plot import show

