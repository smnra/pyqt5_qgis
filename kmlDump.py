#!usr/bin/env python  
#-*- coding:utf-8 _*-  

""" 
@Author: SMnRa 
@Email: smnra@163.com
@Project: pyqt5_qgis
@File: kmlDump.py
@Time: 2018/12/11 13:00

功能描述: 描述: 用于读取KML文件 写入csv 文件




"""

import re
from pykml import parser


def getTab(placemarks):
    """
    :param placemarks: 为 placemarks 标签的列表
    :return: [属性  point坐标 polygon坐标列表] 的 列表
    """
    # 查找value的正则表达式
    valueReStr = r'class="atr-value">(.+?)</span>'

    rows = []
    for placemark in placemarks:
        attribStr = placemark.description.text
        # keysReObj = re.finditer(keyReStr, attribStr)
        valuesReObj = re.finditer(valueReStr, attribStr)
        valueList = []
        for values in valuesReObj:
            value = values.group().replace('class="atr-value">', '').replace('</span>', '')
            valueList.append(value)
        point = placemark.MultiGeometry.Point.coordinates.text
        polygon = placemark.MultiGeometry.Polygon.outerBoundaryIs.LinearRing.coordinates.text

        rows.append(list([valueList, point, polygon]))
        print([valueList, point, polygon])
    return rows




def bigFileRead(fileName,readSize=102400,startPost=0 ,tagStr = '</Placemark>'):
    """
    :param fileName: 文件名
    :param readSize: 每次读取的文件块的大小
    :param startPost: 开始读取的位置
    :param tagStr: 达到读取size 大小 后 遇到 tagStr 字符串后停止读取
    :return: 返回  最后赌球的文件指针的位置 和 期间读取的字符串
    """
    with open(fileName, mode="r", encoding='utf-8') as f:
        # 移动文件指针到start 位置
        f.seek(startPost,0)

        # 读取size 大小的文件块
        content = f.read(readSize)

        # 循环一整行的读取文件 知道遇到 tagStr 字符串 为止
        line = ''
        isEnd = False
        while (tagStr not in line) or not line:
            line = f.readline()
            if not line:
                isEnd = True
                break
            elif tagStr in line:
                content = content + line
                break
            content = content + line

        return {'start':startPost, 'offset':f.tell(), 'isEnd':isEnd  , 'content':content}



def tagComplement(xmlTagStr):
    """
    自动补全 tagName标签 使标签闭合
    :param xmlTagStr: xml 字符串
    :return: 标签闭合的xml 字符串
    """
    xmlStr = xmlTagStr
    tagNames = ['Folder','Document','kml']

    # 如果不含有 <kml> 标签,则添加表头
    if '<kml' not in xmlTagStr:
        xmlStr = kmlTitle + xmlStr

    # 如果包含左标签 不包含右标签 则 添加右标签
    for tagName in tagNames:
        tagLeft =  '<' + tagName
        tagRight =  '</' + tagName
        if tagLeft in xmlStr:
            if tagRight not in xmlStr:
                xmlStr = xmlStr + tagRight + '>'

    return xmlStr


def getKmlTitle(fileName):
    """
    获取kml文件的头部
    :param fileName:
    :return: 返回头部字符串
    """
    with open(fileName, mode="r", encoding='utf-8') as f:
        content = ''
        line = ''
        while True :
            line = f.readline()
            if not line:
                return ''
            elif '<Placemark' in line:
                # 当遇到  '<Placemark' 时 把 当前行 '<Placemark' 前面的部分添加到content并 返回 content
                line = line.split("<Placemark")[0]
                content = content + line
                return content
            content = content + line


kmlTitle = getKmlTitle("temp.kml")

startPostion = 0
blockSize = 102400
isEnd = False

while not isEnd:
    xmlTag = bigFileRead("temp.kml",blockSize,startPostion, '</Placemark>')
    startPostion = xmlTag['offset']
    isEnd = xmlTag['isEnd']
    xmlTagStr = tagComplement(xmlTag['content']).encode(encoding='utf-8')
    kml = parser.fromstring(xmlTagStr)
    placemarkTags = kml.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
    aaa = getTab(placemarkTags)
keyReStr = r'class="atr-name">(.+?)</span>'  # 查找key的正则表达式





