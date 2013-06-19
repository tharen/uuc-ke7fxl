
import os
import sys

import numpy
import gdal
import ogr

import rasterize

def main(poly,attr,raster,wkspc):
    temp = os.path.join(wkspc,'zones.tif')
    zonal_raster = rasterize.rasterize(poly,temp,raster,attr)

    zones = numpy.unique(zonal_raster.GetRasterBand(1).ReadAsArray())
    
    print('Zones:',zones)
    
if __name__=='__main__':
    main(*sys.argv[1:])
