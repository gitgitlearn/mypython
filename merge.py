#!/usr/bin/env python3
# encoding: utf-8
import os
import netCDF4 as  nc
import re
import numpy as np


class Merge:
    '''合并多个含、经度、纬度的二维气象nc数据变成三维；
       对相同维度的矩阵做集合平均及和,把矩阵全放在一个list里
       juzhen不用管它只用来计算均值
       每次改变merge后需要重新import才能生效
       具体用法：from merge import Merge
                target=Merge(filenamebeforedata=..., location=..., varible=...)
                target.combine()
    '''

    def __init__(self, filenamebeforedata=None, location=None, varible=None, juzhen=None):

        self.__filename = filenamebeforedata
        self.__location = location
        self.__varible = varible
        self._juzhen = juzhen

    def combine(self):
        # 得到对应文件夹中所有文件
        filelist = []
        aimfile = []
        for root, dirs, files in os.walk(self.__location, topdown=True):
            filelist += files
        # 得到具有相同前缀名的文件
        for x in filelist:
            fileind = re.search('^' + self.__filename, x)
            if fileind != None:
                aimfile.append(x)
        # print(aimfile)

        # 给文件按时间顺序排序
        dataall = list()
        for x in aimfile:
            data = x.split(self.__filename)[1]
            dataall.append(data)
        # print(dataall)
        rise = sorted(dataall)
        print('连接文件的顺序:', rise)
        orig = [self.__filename + x for x in rise]
        print(orig)

        # 打开所有文件
        avepre = list()
        time = list()
        for x in orig:
            print(self.__location + '\\' + x)
            nc_file = nc.Dataset(self.__location + '\\' + x)
            aq = nc_file[self.__varible][:]
            lon = nc_file['lon'][:]
            lat = nc_file['lat'][:]
            #mm=np.reshape(aq, (1, np.size(aq, 0), np.size(aq, 1))
            avepre.append(aq.reshape(1, np.size(aq, 0), np.size(aq, 1)))
            #time.append(nc_file['time'][:])

        # 在第一个维度上拼接a和c
        # axis指的是你想在第几个维度上进行拼接，因为numpy是0-base，所以第一个维度其实是0
        axis = 0
        finadata = np.concatenate((avepre[0], avepre[1]), axis=axis)
        #ftime = np.concatenate((time[0], time[1]), axis=axis)
        for x in range(2, len(avepre)):
            finadata = np.concatenate((finadata, avepre[x]), axis=axis)
        # ftime = np.concatenate((ftime, time[x]), axis=axis)
        ftime = np.arange(np.size(finadata, 0))
        # 写nc文件
        f_name = nc.Dataset(self.__location + '\\' + self.__filename + '.nc', 'w', format='NETCDF4')
        # 确定基础变量的维度信息。相对与坐标系的各个轴(x,y,z)
        f_name.createDimension('time', np.size(finadata, 0))
        f_name.createDimension('lat', len(lat))
        f_name.createDimension('lon', len(lon))
        # print(dir(np))
        ##创建变量。参数依次为：‘变量名称’，‘数据类型’，‘基础维度信息’
        ntime = f_name.createVariable('time', np.float32, ('time'))
        nlat = f_name.createVariable('lat', np.float32, ('lat'))
        nlon = f_name.createVariable('lon', np.float32, ('lon'))

        # 写入变量time,lon,lat的数据。维度必须与定义的一致。

        ntime[:] = ftime
        nlat[:] = lat
        nlon[:] = lon

        # 新创建一个多维度变量，并写入数据，
        ntar = f_name.createVariable(self.__varible, np.float32, ('time', 'lat', 'lon'))
        ntar[:] = finadata

        # 对nc文件增加说明变量（依照需要改动）
        # f_name.description = 'sea level pressure'
        # f_name.source = 'cmip6'
        # ntar.unit = 'pa'

        # 关闭文件
        f_name.close()

    def jihepingjun(self):
        summ = np.add(self._juzhen[0], self._juzhen[1])
        print(summ.shape)
        for x in range(2, len(self._juzhen) - 1):
            summ = np.add(summ, x)
        ave = np.divide(summ, len(self._juzhen))
        return ave, summ
