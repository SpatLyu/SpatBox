# 地理编码
def geocoding(address_list,key,city):
    
    '''
        address_list  :  用于地理编码的地名列表,
        
        key           :  高德地图地理编码应用对应的密钥
        
        city          :  检索地名所在的地级市行政区划名称
        
        return        :   对应的地理编码结果
    '''
    
    print('此函数返回由地名，火星坐标系下地名对应的经度和纬度组成的pandas格式数据')
    
    #导入必要库
    import requests
    import json
    import pandas as pd 
    
    #定义请求地理编码工作的高德服务网址
    url='https://restapi.amap.com/v3/geocode/geo'
    #保存输出结果的变量
    lon,lat,spatial = [],[],[]
    
    for a in address_list:
        try:
            params = { 'key': key,
                       'address': a,
                       'city': city }

            res = requests.get(url, params)
            jd = json.loads(res.text)
            coords = jd['geocodes'][0]['location']
            lon.append(coords[:10])
            lat.append(coords[-9:])
        except:
            lon.append('-1')
            lat.append('-1')
    
    for l1,l2 in zip(lon,lat):
        spatial.append([float(l1),float(l2)])
    spatial = pd.DataFrame(spatial,columns=['lon','lat'])
    spatial['name']=address_list
    spatial=spatial[['name','lon','lat']]
    
    return spatial  






# 逆地理解码
def inverse_geocoding(lon,lat,key):
    '''
        lon  :   要查询地名对应的经度
        
        lat  :   要查询地名对应的纬度
        
        key  :   高德服务对应的key
    
    '''
    
    import requests
    import json 
    
    location_name = list()
    
    def getname(lon,lat):
        url = 'https://restapi.amap.com/v3/geocode/regeo?key={}&location={},{}'.format(key,lon,lat)
        res = requests.get(url)
        json_data = json.loads(res.text)
        json_data=json_data['regeocode']['formatted_address'] 
        return json_data
    
    for l1,l2 in zip(lon,lat):
        location_name.append(getname(l1,l2)) 
        
    return location_name






        
        
        
        
        
        

            
