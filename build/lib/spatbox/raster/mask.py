import rasterio as rio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject
import numpy as np
import fiona

def raster_mask(src_img,mask,dst_img):
    '''
        src_img : 要裁切的栅格数据文件名, 字符串类型 
        
        mask: 作为裁切标准的矢量数据文件名, 字符串类型 
        
        dst_img:输出裁切后的tif文件名, 字符串类型 
    '''
    
    with fiona.open(mask, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]

    src = rio.open(src_img)
    out_image, out_transform = rasterio.mask.mask(src, # 输入数据
                                                shapes, # 掩膜数据
                                                crop=True, # 是否裁剪
                                                nodata=np.nan) # 缺省值
    out_meta = src.meta # 元数据

# 更新元数据
    out_meta.update({"driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform}) # 转换函数

# 输出掩膜提取图像
    with rasterio.open(dst_img, "w", **out_meta) as dest:
        dest.write(out_image)