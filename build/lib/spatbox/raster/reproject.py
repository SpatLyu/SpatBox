import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject
from rasterio.enums import Resampling
import numpy as np

def raster_reproject(src_img,dst_img,dst_crs):
    '''
        src_img:输入图像的位置, 字符串类型 
        
        dst_img:输出图像的位置, 字符串类型 
        
        dst_crs：输出图像坐标系统
    '''
    src_ds = rio.open(src_img)
    
    # 计算在新空间参考系下的仿射变换参数，图像尺寸
    dst_transform, dst_width, dst_height = calculate_default_transform(
        src_ds.crs, # 输入坐标系
        dst_crs, # 输出坐标系
        src_ds.width, # 输入图像宽
        src_ds.height, # 输入图像高
        *src_ds.bounds) # 输入数据源的图像范围

    # 更新数据集的元数据信息
    profile = src_ds.meta.copy()
    profile.update({
        'crs': dst_crs,
        'driver':'GTiff',
        'transform': dst_transform,
        'width': dst_width,
        'height': dst_height
            })

    # 重投影并写入数据
    with rio.open(dst_img, 'w',**profile) as dst_ds:
        for i in range(1, src_ds.count + 1): # 遍历每个图层，通常只需要第一层即可
            src_array = src_ds.read(i)
            dst_array = np.empty((dst_height, dst_width), dtype=profile['dtype']) # 初始化输出图像数据

            # 重投影
            reproject(
                # 源文件参数
                source=src_array,
                src_crs=src_ds.crs,
                src_transform=src_ds.transform,
                # 目标文件参数
                destination=dst_array,
                dst_transform=dst_transform,
                dst_crs=dst_crs,
                # 其它配置
                resampling=Resampling.average,
                num_threads=2)
            # 写入图像
            dst_ds.write(dst_array, i)