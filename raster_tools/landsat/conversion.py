# -*- coding: utf-8 -*-
"""
Convert Landsat digital numbers to radiance and reflectance

Created on Fri Jul 05 01:30:15 2013

@author: THAREN

references:
        https://landsat.usgs.gov/Landsat8_Using_Product.php
"""

import os

import numpy
import gdal

import metadata

class BandStack(object):
    def __init__(self,dataset,imagename,bands=9):
        self.dataset = dataset
        self.imagename = imagename
        
        md = os.path.join(dataset,'{}_MTL.txt'.format(imagename))
        self.metadata = metadata.LandsatMetadata(md, reflectance_bands=bands)
        
        self.__getbands()
        
    def __getbands(self):
        self.bands={}
        for i in xrange(1,self.metadata.reflectance_bands+1):
            p = os.path.join(self.dataset,'{}_B{}.TIF'.format(self.imagename,i))
            b = gdal.OpenShared(p)
            self.bands[i] = b
    
    def calc_radiance(self,bands=None,save=False,dest_fn=None,driver='Gtiff'):
        """
        Compute top of atmosphere radiance from raw digital numbers
        """
        if bands==None:
            bands = xrange(1,self.metadata.reflectance_bands+1)
        
        radscale = self.metadata.radiance_scaling()
        
        if save:
            if not dest_fn:
                dest_fn = os.path.join(self.dataset,'{}_TOA_RAD.tif'.format(self.imagename))
            opts = [ 'TILED=YES', 'COMPRESS=DEFLATE' ]
        
        else:
            driver = 'MEM'
            dest_fn = 'foo'
            opts = []
            
        drv = gdal.GetDriverByName(driver)
        srs = self.bands[bands[0]].GetProjection()
        x = self.bands[bands[0]].RasterXSize
        y = self.bands[bands[0]].RasterYSize
        gt = self.bands[bands[0]].GetGeoTransform()
        self.radiance = drv.Create(dest_fn, x, y, len(bands), gdal.GDT_Float32, opts)
        
#        toa_rad = numpy.ones((7500,8000),dtype=numpy.float32)
        
        for i,b in enumerate(bands):
            print 'Calculating Top of Atmosphere Radiance for band {}'.format(b)
            a = self.bands[b].ReadAsArray()
            a = a * radscale[b]['mult'] + radscale[b]['add']
            self.radiance.GetRasterBand(i+1).WriteArray(a)

#            toa_rad[i,:,:] = a[:,:]
        
        return dest_fn, self.radiance

    def calc_reflectance(self,save=False,dest_fn=None,driver='Gtiff'):
        """
        Compute top of atmosphere reflectance from top of atmosphere radiance
        """
        
        refscale = self.metadata.reflectance_scaling()
        
        if save:
            if not dest_fn:
                dest_fn = os.path.join(self.dataset,'{}_TOA_REF.tif'.format(self.imagename))
            opts = [ 'TILED=YES', 'COMPRESS=DEFLATE' ]
        
        else:
            driver = 'MEM'
            dest_fn = 'foo'
            opts = []
            
        drv = gdal.GetDriverByName(driver)
        bc = self.radiance.RasterCount
        srs = self.radiance.GetProjection()
        x = self.radiance.RasterXSize
        y = self.radiance.RasterYSize
        gt = self.radiance.GetGeoTransform()
        self.reflectance = drv.Create(dest_fn, x, y, bc, gdal.GDT_Float32, opts)
        
#        toa_rad = numpy.ones((7500,8000),dtype=numpy.float32)
        
        for b in xrange(bc):
            print 'Calculating Top of Atmosphere Reflectance for band {}'.format(b)
            a = self.radiance.GetRasterBand(b+1).ReadAsArray()
            a = a * refscale[b+1]['mult'] + refscale[b+1]['add']
            self.reflectance.GetRasterBand(b+1).WriteArray(a)
            

#            toa_rad[i,:,:] = a[:,:]
        
        return dest_fn, self.reflectance

def test():
    p = r'C:\data\landsat\landsat8\LC80470282013159LGN00'
    im = 'LC80470282013159LGN00'
    stack = BandStack(p,im)
    
    o = r'C:\data\landsat\landsat8\LC80470282013159LGN00\{}'.format(im)
    toa_rad = stack.calc_radiance((1,),save=True)
    toa_ref = stack.calc_reflectance(save=True,dest_fn=None)

if __name__=='__main__':
    test()        