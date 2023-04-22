__version__ = "0.2.0",
__author__ = "SpatLyu"

import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd  
import spatbox as stx
from . import vector
from . import raster 
from . import analysis 
from . import utils
from . import maptools
from rasterio.plot import show
from .vector.grid import make_grid

