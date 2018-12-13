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

class KmlAnalysis():
    def __init__(self,fileName):
        # kml文件路径
        self.fileName = fileName

        # kml 文件声明及前缀
        self.kmlPrefix = ''

        # kml 文件 表格的标题
        self.kmlTableTitle = []

        # kml 文件读取完成 标志
        self.isEnd = False

        # kml大文件开始读取的位置 offset
        self.startPostion = 0

        # kml大文件 每次读取的 大小
        self.readBlockSize = 102400

        # 已读取feature 的个数
        self.featureCount = 0

    def getKmlPrefix(self):
        """
        获取kml文件的头部声明及 前缀
        :return: 返回头部字符串
        """
        with open(self.fileName, mode="r", encoding='utf-8') as f:
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
                    # 保存 kml 前缀
                    # self.kmlPrefix = content
                    return content
                content = content + line



    def getTab(self,placemarks):
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
            self.featureCount += 1
            # print([valueList, point, polygon])
            # print(self.featureCount)
        return rows



    def kmlFileBlockRead(self,readSize=10240, startPost=0 ,tagStr = '</Placemark>'):
        """
        读取kml大文件,从startPost位置开始读取 readSize 大小的 块 后的第一个 '</Placemark>' 行
        :param readSize: 每次读取的文件块的大小
        :param startPost: 开始读取的位置
        :param tagStr: 达到读取size 大小 后 遇到 tagStr 字符串后停止读取
        :return: 返回  最后读取的文件指针的位置 和 期间读取的字符串
        """
        with open(self.fileName, mode="r", encoding='utf-8') as f:
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



    def tagComplement(self,xmlTagStr):
        """
        自动补全 tagName标签 使标签闭合
        :param xmlTagStr: xml 字符串
        :return: 标签闭合的xml 字符串
        """
        xmlStr = xmlTagStr
        tagNames = ['Folder','Document','kml']

        # 如果不含有 <kml> 标签,则添加表头
        if '<kml' not in xmlTagStr:
            xmlStr = self.kmlPrefix + xmlStr

        # 如果包含左标签 不包含右标签 则 添加右标签
        for tagName in tagNames:
            tagLeft =  '<' + tagName
            tagRight =  '</' + tagName
            if tagLeft in xmlStr:
                if tagRight not in xmlStr:
                    xmlStr = xmlStr + tagRight + '>'

        return xmlStr




    def getTableTitle(self):
        """
        :param placemarks: 为 placemarks 标签的列表
        :return: [属性  point坐标 polygon坐标列表] 的 列表
        """

        # 读取文件 的第一个 <Placemark> 标签的内容
        placemark = self.kmlFileBlockRead(32, startPost=0, tagStr='</Placemark>')

        # 检查 kml文件是否完整
        kmlStr = self.tagComplement(placemark['content']).encode(encoding='utf-8')

        # 将kml字符串生成 kml 对象
        kml = parser.fromstring(kmlStr)
        placemarkTag = kml.findall('.//{http://www.opengis.net/kml/2.2}Placemark')[0]

        # 查找key的正则表达式
        keyReStr = r'class="atr-name">(.+?)</span>'

        attribStr = placemarkTag.description.text
        # keysReObj = re.finditer(keyReStr, attribStr)
        keyReObj = re.finditer(keyReStr, attribStr)
        keyList = []
        for keys in keyReObj:
            key = keys.group().replace('class="atr-name">', '').replace('</span>', '')
            keyList.append(key)

        # 保存 表头
        # self.kmlTableTitle = list(keyList)
        return list(keyList)


    def kmlBigFileRead(self):
        # 获取kml文件的 声明前缀
        self.kmlPrefix = self.getKmlPrefix()

        # 获取kml文件中的表头
        self.kmlTableTitle = self.getTableTitle()

        # 循环读取 kml文件 每次读取 self.readBlockSize 大小
        while not self.isEnd:
            xmlTag = self.kmlFileBlockRead(self.readBlockSize, self.startPostion, '</Placemark>')
            self.startPostion = xmlTag['offset']
            self.isEnd = xmlTag['isEnd']
            xmlTagStr = self.tagComplement(xmlTag['content']).encode(encoding='utf-8')
            kmlTag = parser.fromstring(xmlTagStr)
            placemarkTags = kmlTag.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
            aaa = self.getTab(placemarkTags)
            print(aaa)


if __name__=='__main__':
    kml = KmlAnalysis("wms.kml")
    kml.kmlBigFileRead()






