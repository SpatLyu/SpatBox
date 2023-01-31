import rasterio as rio
from rasterio import features
from shapely.geometry import shape
import geopandas as gpd
import numpy as np

def raster_to_polygon(rasterfile,outfile,nodata=np.nan):
    '''
        rasterfile ： 输入要转换的栅格文件, 字符串类型
        outfile  : 输出的矢量文件, 字符串类型
        nodata   : 缺失值填充，numpy数值类型
        
        当栅格数据集全为整型时，请设置缺失值为0或None
    '''

    out_shp = gpd.GeoDataFrame(columns=['category','geometry'])

    with rio.open(rasterfile) as f:
        image = f.read(1)
        img_crs = f.crs
        image[image == f.nodata] = nodata
        image = image.astype(np.float32)
        
        i = 0
        for coords, value in features.shapes(image, transform=f.transform):
            if value != nodata:
                geom = shape(coords)
                out_shp.loc[i] = [value,geom]
                i += 1

    out_shp.set_geometry('geometry',inplace=True)
    out_shp = out_shp.dissolve(by='category',as_index=False)
    out_shp.set_crs(img_crs,inplace=True)
    out_shp.to_file(outfile, encoding = 'utf-8')
    print('raster to polygon have finished!')
    
    return None 