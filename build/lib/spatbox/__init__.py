__version__ = "0.1.7",
__author__ = "SpatLyu"

import os
os.environ['USE_PYGEOS'] = '0'
import geopandas
import spatbox as stx
import spatbox.vector
import spatbox.raster 
import spatbox.model 
import spatbox.datasets
from rasterio.plot import show

