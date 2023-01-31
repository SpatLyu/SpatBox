import numpy as np

def gcj02_to_wgs84(lon,lat):
    '''
        lon : 要转换的点的经度, 列表类型 
        
        lat : 要转换的点的纬度, 列表类型
        
        return : 粗略转换为WGS84坐标的经纬度, 列表类型
    '''
    
    lon_wgs84,lat_wgs84 = [],[]
    
    def gcj02_to_wgs84_one(lng, lat):
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系的经度
        :param lat:火星坐标系纬度
        :return:
        """

        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626  # π
        a = 6378245.0  # 长半轴
        ee = 0.00669342162296594323  # 偏心率平方

        def _transformlng(lng, lat):
            lng, lat = np.array(lng), np.array(lat)
            ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
                  0.1 * lng * lat + 0.1 * np.sqrt(np.fabs(lng))
            ret += (20.0 * np.sin(6.0 * lng * pi) + 20.0 *
                    np.sin(2.0 * lng * pi)) * 2.0 / 3.0
            ret += (20.0 * np.sin(lng * pi) + 40.0 *
                    np.sin(lng / 3.0 * pi)) * 2.0 / 3.0
            ret += (150.0 * np.sin(lng / 12.0 * pi) + 300.0 *
                    np.sin(lng / 30.0 * pi)) * 2.0 / 3.0
            return ret

        def _transformlat(lng, lat):
            lng, lat = np.array(lng), np.array(lat)
            ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
                  0.1 * lng * lat + 0.2 * np.sqrt(np.fabs(lng))
            ret += (20.0 * np.sin(6.0 * lng * pi) + 20.0 *
                    np.sin(2.0 * lng * pi)) * 2.0 / 3.0
            ret += (20.0 * np.sin(lat * pi) + 40.0 *
                    np.sin(lat / 3.0 * pi)) * 2.0 / 3.0
            ret += (160.0 * np.sin(lat / 12.0 * pi) + 320 *
                    np.sin(lat * pi / 30.0)) * 2.0 / 3.0
            return ret

        lng, lat = np.array(lng), np.array(lat)
        dlat = _transformlat(lng - 105.0, lat - 35.0)
        dlng = _transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * pi
        magic = np.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = np.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * np.cos(radlat) * pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return lng * 2 - mglng, lat * 2 - mglat
    
    for l1,l2 in zip(lon,lat):
        lon_wgs84.append(gcj02_to_wgs84_one(l1,l2)[0])
        lat_wgs84.append(gcj02_to_wgs84_one(l1,l2)[1])
        
    return lon_wgs84,lat_wgs84