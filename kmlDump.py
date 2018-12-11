#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@Author: SMnRa 
@Email: smnra@163.com
@Project: pyqt5_qgis
@File: kmlTrans.py 
@Time: 2018/12/11 13:00

功能描述: 描述: 用于读取KML文件 写入csv 文件




"""

import re
from pykml import parser

# 定义kml格式的字符


with open("temp.kml", mode="r", encoding= 'utf-8') as f:
    kml = parser.parse(f).getroot()
placemarks = kml.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
# 遍历所有的Placemark

keyReStr = r'class="atr-name">(.+?)</span>'  # 查找key
valueReStr = r'class="atr-value">(.+?)</span>'   # 查找value




for placemark in placemarks:
    attribStr = placemark.description.text
    # keysReObj = re.finditer(keyReStr, attribStr)
    valuesReObj = re.finditer(valueReStr, attribStr)
    valueList = []
    for values in valuesReObj:
        value = values.group().replace('class="atr-value">','').replace('</span>','')
        valueList.append(value)
    point = placemark.MultiGeometry.Point.coordinates.text
    polygon = placemark.MultiGeometry.Polygon.outerBoundaryIs.LinearRing.coordinates.text
    print(point,polygon)
    print(valueList)