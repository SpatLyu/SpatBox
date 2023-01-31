import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject
from rasterio.enums import Resampling
import numpy as np

def raster_resample(inputfile,outputfile,resolution,resampling_way='average'):
    '''
        inputfile       :   输入要采样的栅格文件名, 字符串类型 
        outputfile      :   输出重采样后的栅格文件地址, 字符串类型 
        resolution      :   重采样后的分辨率，以元组形式传入,单位m
        resampling_way  :   重采样方式, 字符串类型 
    ''' 
    
    # 重采样方式定义：
    ways = dict([
                    ['nearest',Resampling.nearest],
                    ['bilinear',Resampling.bilinear],
                    ['cubic',Resampling.cubic],
                    ['cubic_spline',Resampling.cubic_spline],
                    ['lanczos',Resampling.lanczos],
                    ['average',Resampling.average],
                    ['mode',Resampling.mode],
                    ['max',Resampling.max],
                    ['min',Resampling.min],
                    ['med',Resampling.med],
                    ['sum',Resampling.sum],
                    ['rms',Resampling.rms],
                    ['q1',Resampling.q1],
                    ['q3',Resampling.q3]
               ])
    
    
    src_ds = rio.open(inputfile)
    dst_transform, dst_width, dst_height = calculate_default_transform(src_ds.crs, # 输入坐标系
                                                                       src_ds.crs, # 输出坐标系
                                                                       src_ds.width, # 输入图像宽
                                                                       src_ds.height, # 输入图像高
                                                                       resolution=resolution, # 输出图像分辨率，
                                                                       *src_ds.bounds) # 输入数据源的图像范围
    # 更新数据集的元数据信息
    profile = src_ds.meta.copy()
    profile.update({
        'crs': src_ds.crs,
        'transform': dst_transform,
        'width': dst_width,
        'height': dst_height
        })
    
    # 重投影并写入数据
    with rio.open(outputfile, 'w', **profile) as dst_ds:
        for i in range(1, src_ds.count + 1): # 遍历每个图层，通常只需要第一层即可
            src_array = src_ds.read(i)
            dst_array = np.empty((dst_height, dst_width), dtype=profile['dtype']) # 初始化输出图像数据

            # 重采样
            reproject(
                source=src_array,
                src_crs=src_ds.crs,
                src_transform=src_ds.transform,
                destination=dst_array,
                dst_transform=dst_transform,
                dst_crs=src_ds.crs,
                resampling=ways.get(resampling_way),
                num_threads=2)
            # 写入图像
            dst_ds.write(dst_array, i)
            
    print('{:-^30}'.format('重采样完成'))