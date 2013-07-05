# -*- coding: utf-8 -*-
"""
Read landsat metadata file into a hierarchical dictionary

Created on Fri Jul 05 00:06:48 2013

@author: THAREN

references:
    http://ibis.colostate.edu/WebContent/WS/ColoradoView/TutorialsDownloads/CO_RS_Tutorial10.pdf
    https://landsat.usgs.gov/Landsat8_Using_Product.php
"""

import string
from collections import OrderedDict

class LandsatMetadata(object):
    def __init__(self, metadata_path, reflectance_bands=9):
        self.metadata_path = metadata_path
        self.reflectance_bands = reflectance_bands
        self.groups = OrderedDict()
        
        self.__read()
    
    def sun(self):
        rad = {}
        rad['sun_azimuth'] = self.groups['L1_METADATA_FILE']['IMAGE_ATTRIBUTES']['SUN_AZIMUTH']
        rad['sun_elevation'] = self.groups['L1_METADATA_FILE']['IMAGE_ATTRIBUTES']['SUN_ELEVATION']
        rad['earth_sun_distance'] = self.groups['L1_METADATA_FILE']['IMAGE_ATTRIBUTES']['EARTH_SUN_DISTANCE']
        
        return rad
    
    def radiance_scaling(self):
        scaling = {}
        for i in xrange(1,self.reflectance_bands+1):
            mult = self.groups['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_{}'.format(i)]
            add = self.groups['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_{}'.format(i)]
            scaling[i] = {'mult':mult,'add':add}
        
        return scaling
    
    def reflectance_scaling(self):
        scaling = {}
        for i in xrange(1,self.reflectance_bands+1):
            mult = self.groups['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['REFLECTANCE_MULT_BAND_{}'.format(i)]
            add = self.groups['L1_METADATA_FILE']['RADIOMETRIC_RESCALING']['REFLECTANCE_ADD_BAND_{}'.format(i)]
            scaling[i] = {'mult':mult,'add':add}
        
        return scaling
        
    def __read_group(self,groupname,metadatafile):
        groupdict = OrderedDict()

        l = metadatafile.readline()        
        while l:
            name,value = map(string.strip,l.split('='))
            
            if name.lower()=='end_group':
                #print groupname,name,value
                return groupdict
            
            if name.lower()=='group':
                groupdict[value] = self.__read_group(value,metadatafile)
            
            else:
                if '.' in value:
                    try:
                        value=float(value)
                    except:
                        pass
                else:
                    try:
                        value=int(value)
                    except:
                        pass
                    
                groupdict[name] = value

            l = metadatafile.readline()
        
    def __read(self):
        with open(self.metadata_path) as foo:
            self.groups = OrderedDict()
            
            l = foo.readline()
            while l:
#                print l.strip()
                if l.strip().lower()=='end':
                    return
                    
                name,value = map(string.strip,l.split('='))
                if name.lower()=='group':
                    self.groups[value] = self.__read_group(value,foo)
                
                l = foo.readline()
        

def test():
    p=r'C:\data\landsat\landsat8\LC80470282013159LGN00\LC80470282013159LGN00_MTL.txt'
    md = LandsatMetadata(p,reflectance_bands=9)
    
    print md.sun()
    print md.radiance_scaling()
    print md.reflectance_scaling()
    
if __name__=='__main__':
    test()