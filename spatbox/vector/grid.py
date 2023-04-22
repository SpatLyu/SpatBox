import os 
import numpy as np
import pandas as pd 
from osgeo import ogr
from math import ceil
import geopandas as gpd 
from shapely.geometry import MultiPoint
from shapely.ops import voronoi_diagram



def Make_Honeycomb_Polygon(vectorfile,outfile,gridwidth,gridheight):
    '''
        vectorfile   :    要创建蜂窝多边形的矢量文件，字符串类型
        outfile      :    导出创建的蜂窝多边形文件地址，字符串类型
        girdwidth    :    划分格网的宽度，数值类型
        gridheight   :    划分格网的高度，数值类型
        gridwidth,gridheight一般取相同的值
    '''

    
    #此函数创建正方形渔网
    def Fishgrid(outfile,xmin,xmax,ymin,ymax,gridwidth,gridheight):
        #参数转换到浮点型
        xmin = float(xmin)
        xmax = float(xmax)
        ymin = float(ymin)
        ymax = float(ymax)
        gridwidth = float(gridwidth)
        gridheight = float(gridheight)

        #计算行数和列数
        rows = ceil((ymax-ymin)/gridheight)
        cols = ceil((xmax-xmin)/gridwidth)

        #初始化起始格网四角范围
        ringXleftOrigin = xmin
        ringXrightOrigin = xmin+gridwidth
        ringYtopOrigin = ymax
        ringYbottomOrigin = ymax-gridheight

        #创建输出文件
        outdriver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(outfile):
            outdriver.DeleteDataSource(outfile)
        outds = outdriver.CreateDataSource(outfile)
        outlayer = outds.CreateLayer(outfile,geom_type = ogr.wkbPolygon)
        #不添加属性信息，获取图层属性
        outfielddefn  = outlayer.GetLayerDefn()
        #遍历列，每一列写入格网
        col = 0
        while col<cols:
            #初始化，每一列写入完成都把上下范围初始化
            ringYtop = ringYtopOrigin
            ringYbottom = ringYbottomOrigin
            #遍历行，对这一列每一行格子创建和写入
            row = 0
            while row<rows:
                #创建左上角第一个格子
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(ringXleftOrigin,ringYtop)
                ring.AddPoint(ringXrightOrigin,ringYtop)
                ring.AddPoint(ringXrightOrigin,ringYbottom)
                ring.AddPoint(ringXleftOrigin,ringYbottom)
                ring.CloseRings()
                #写入几何多边形
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
                #创建要素，写入多边形
                outfeat = ogr.Feature(outfielddefn)
                outfeat.SetGeometry(poly)
                #写入图层
                outlayer.CreateFeature(outfeat)
                outfeat = None
                #下一多边形，更新上下范围
                row+=1
                ringYtop = ringYtop - gridheight
                ringYbottom = ringYbottom-gridheight
            #一列写入完成后，下一列，更新左右范围
            col+=1
            ringXleftOrigin = ringXleftOrigin+gridwidth
            ringXrightOrigin = ringXrightOrigin+gridwidth
        #写入后清除缓存
        outds = None 
        
        # 此函数为生成六边形格网的一些参数的计算
    def spatial_transform(width,height):
        area = width*height ## 面积
        l = np.sqrt((2*area)/(3*np.sqrt(3))) ##蜂窝边长
        cellWidth = 3*l ## 渔网宽度
        cellHeight = (np.sqrt(3))*l ## 渔网高度
        deltaX = 1.5 * l ## 横向偏移
        deltaY = (np.sqrt(3)/2)*l ## 纵向偏移
        
        return l,cellWidth,cellHeight,deltaX,deltaY 
    
    #首先生成正方型渔网
    l,cellWidth,cellHeight,deltaX,deltaY = spatial_transform(gridwidth,gridheight)
    spatialdata = gpd.read_file(vectorfile)
    
    Fishgrid(outfile,
             xmin=spatialdata.bounds.minx-cellWidth*5,#后期不都是六边形可以加大这个倍数
             ymin=spatialdata.bounds.miny-cellHeight*5,
             xmax=spatialdata.bounds.maxx+cellWidth*5,
             ymax=spatialdata.bounds.maxy+cellHeight*5,
             gridwidth=cellWidth,
             gridheight=cellHeight)
    #读取并为生成的正方形格网添加投影信息
    gw=gpd.read_file(outfile)
    gw.set_crs(spatialdata.crs,inplace=True)
    #获取对应的网格点：
    pointvalue = gw.geometry.centroid
    #存贮会用到创建蜂窝渔网的点
    point = pd.DataFrame()
    point['x'] = pointvalue.geometry.x
    point['y'] = pointvalue.geometry.y
    point_transform = pd.DataFrame()
    point_transform['x'] = point['x']+deltaX
    point_transform['y'] = point['y']+deltaY 
    point = pd.concat([point,point_transform],axis=0)
    point.index = range(point.shape[0])
    #上一步的点转换成空间文件：
    point_new = gpd.GeoDataFrame(data=point,
                                 geometry=gpd.points_from_xy(point['x'],point['y']),
                                 crs=spatialdata.crs)
    #生成对应的面
    multipoint=MultiPoint(point_new.geometry)
    ploygon=gpd.GeoSeries(voronoi_diagram(multipoint).geoms)
    #为生成的渔网面设置投影
    ploygon.set_crs(spatialdata.crs,inplace=True)
    #选择出矢量文件附近的面
    #首先得到对应面的索引值
    index=list()
    for i,p in zip(range(ploygon.shape[0]),ploygon):
        if spatialdata.intersects(p).bool()==True:
            index.append(i)
    #获取需要的面状要素：
    ploygon1=ploygon[index]
    ploygon1.index=range(ploygon1.shape[0])
    #增加蜂窝多边形渔网面id信息
    ploygon_need = gpd.GeoDataFrame(data={'id':range(1,ploygon1.shape[0]+1)},
                                    geometry=ploygon1)
    #导出蜂窝多边形渔网数据
    ploygon_need.to_file(outfile)
    #打印提示信息
    print('Successfully Create Honeycomb Polygon!')
    
    
# 创建正方形网络
def Make_Fishgrid(inputfile, outfile, gridwidth, gridheight):
        '''
            inputfile   :    要创建网格的矢量文件，字符串类型
            outfile      :    导出创建的网格文件地址，字符串类型
            girdwidth    :    划分格网的宽度，数值类型
            gridheight   :    划分格网的高度，数值类型
            gridwidth,gridheight一般取相同的值
        '''
        
        _pcs = gpd.read_file(inputfile)
    
        xmin = float(_pcs.bounds.minx.values[0]),
        ymin = float(_pcs.bounds.miny.values[0]),
        xmax = float(_pcs.bounds.maxx.values[0]),
        ymax = float(_pcs.bounds.maxy.values[0]),
        xmin,xmax,ymin,ymax = xmin[0],xmax[0],ymin[0],ymax[0]
        gridwidth = float(gridwidth)
        gridheight = float(gridheight)
        #计算行数和列数
        rows = ceil((ymax-ymin)/gridheight)
        cols = ceil((xmax-xmin)/gridwidth)

        #初始化起始格网四角范围
        ringXleftOrigin = xmin
        ringXrightOrigin = xmin+gridwidth
        ringYtopOrigin = ymax
        ringYbottomOrigin = ymax-gridheight

        #创建输出文件
        outdriver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(outfile):
            outdriver.DeleteDataSource(outfile)
        outds = outdriver.CreateDataSource(outfile)
        outlayer = outds.CreateLayer(outfile,geom_type = ogr.wkbPolygon)
        #不添加属性信息，获取图层属性
        outfielddefn  = outlayer.GetLayerDefn()
        #遍历列，每一列写入格网
        col = 0
        while col<cols:
            #初始化，每一列写入完成都把上下范围初始化
            ringYtop = ringYtopOrigin
            ringYbottom = ringYbottomOrigin
            #遍历行，对这一列每一行格子创建和写入
            row = 0
            while row<rows:
                #创建左上角第一个格子
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(ringXleftOrigin,ringYtop)
                ring.AddPoint(ringXrightOrigin,ringYtop)
                ring.AddPoint(ringXrightOrigin,ringYbottom)
                ring.AddPoint(ringXleftOrigin,ringYbottom)
                ring.CloseRings()
                #写入几何多边形
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
                #创建要素，写入多边形
                outfeat = ogr.Feature(outfielddefn)
                outfeat.SetGeometry(poly)
                #写入图层
                outlayer.CreateFeature(outfeat)
                outfeat = None
                #下一多边形，更新上下范围
                row+=1
                ringYtop = ringYtop - gridheight
                ringYbottom = ringYbottom-gridheight
            #一列写入完成后，下一列，更新左右范围
            col+=1
            ringXleftOrigin = ringXleftOrigin+gridwidth
            ringXrightOrigin = ringXrightOrigin+gridwidth
        #写入后清除缓存
        outds = None
    
        pcs_ = gpd.read_file(outfile)
        pcs_.set_crs(_pcs.crs,inplace=True)
    
        outdriver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(outfile):
            outdriver.DeleteDataSource(outfile) 
        pcs_ = gpd.clip(pcs_,_pcs)   
        pcs_.to_file(outfile, encoding='utf-8')
    
        print("Successfully Create Grid!")
        
        
def make_grid(inputfile,outfile,gridsize,square=True):
    '''
        inputfile : 输入要创建网格的矢量数据；string
        
        outfile   : 输出创建的网格矢量；string
        
        gridsize  : 网格的尺寸；numberic
        
        square    : 是否创建正方形格网；True创建正方形，False创建六边形渔网;logical
    '''
    if square:
        Make_Fishgrid(inputfile,outfile,gridwidth=gridsize,gridheight=gridsize)
    else:
        Make_Honeycomb_Polygon(inputfile,outfile,gridsize,gridsize)
    

    