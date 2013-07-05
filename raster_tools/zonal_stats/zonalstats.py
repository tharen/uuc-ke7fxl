#!python zonalstats.py
"""
.. module:: zonalstats
    :synopsis: Computes raster grid zone statistics
    
.. moduleauthor:: Tod Haren <tod.haren@gmail.com>

"""

import os
import sys
import logging
import logging.handlers
from collections import OrderedDict

import numpy
import gdal
import ogr
import osr
import shapely.geometry
import shapely.prepared
import shapely.geos

log = logging.getLogger()

if shapely.geos.geos_capi_version > (1,6,2):
    raise ImportError(
            'GEOS version > (1,6,2) includes a bug that breaks '
            'zonalstats.py.  Use Shapely version <= 1.2.10')

#Statistical functions to compute
stat_funcs = {
    'mean': numpy.mean
    ,'stdev': numpy.std
    ,'pctl': lambda x: numpy.percentile(
            x,(0.0,0.01,0.25,0.05,0.10,0.25,0.5,0.75,0.90,0.95,0.975,0.99,1.0))
    ,'pctl_names': [
        'min', 'p01', 'p025', 'p05', 'p10', 'p25', 'p50'
        , 'p75', 'p90', 'p95', 'p975', 'p99', 'max']
    }

def calc_percentiles(values,*args,**kargs):
    pctl_names = (
            'min','p01','p025','p05','p10','p25','p50'
            ,'p75','p90','p95','p975','p99','max')
    pctl_vals =  (
            0.0  ,0.01 ,0.25  ,0.05 ,0.10 ,0.25 ,0.5  
            ,0.75 ,0.90 ,0.95 ,0.975 ,0.99 ,1.0)
    
    pct = dict(zip(pctl_names, numpy.percentile(values,pctl_vals)))
    return pct
                
def calc_gini(values,*args,**kargs):
    """
    Computes a Gini coefficient for a 1-D array of values.
    
    Reference:
        http://www.heckler.com.br/blog/2010/06/15/gini-coeficient-having-fun-in-both-sql-and-python/
    """
    values.sort()
    N = float(values.size)
    prod = 0.0
    sum = 0.0
    
    for i, value in enumerate(values[::-1]):
        prod += ((i+1)*value)
        sum += value
    
    u = sum/N
    G = (N+1.0)/(N-1.0) - (prod/(N*(N-1.0)*u))*2.0
    
    return G
    
def calc_stats(values, cellsize=1):
    """
    Calculate descriptive statistics for a set of values.
    
    Args:
        values (array): Array of values to compute statistics on
        cellsize (float): Size of the array grid cells.  (Not currently used)
    
    Returns:
        stats: A dict of the descriptive statistics.

    """
    ##TODO: add spatial stats, diversity index, etc.
    ##TODO: Use a list of available calculation functions
    stats = OrderedDict()

    try:
        stats['n'] = numpy.size(values)
        stats['mean'] = numpy.mean(values)
        stats['stdev'] = numpy.std(values)
        stats.update(calc_percentiles(values))
        
        stats['gini'] = calc_gini(values.compressed())
                
    except:
        log.exception('Error computing summary statistics')
        #TODO: return null data rather than bailing
        raise
        #return None

    return stats

def main(raster_path,zones_dsn,zoneslyr_sql,zone_attr,stats_path
        ,prefix=None,raster_band=1):
    
    raster = Raster(raster_path)
    ds = ogr.Open(zones_dsn)
    lyr = ds.ExecuteSQL(zoneslyr_sql)
    
    ct = osr.CoordinateTransformation(lyr.GetSpatialRef(),raster.spatial_ref)
    
    zone_polys = []
    zone_ids = []
    for ftr in lyr:
        zone_ids.append(ftr.GetField(zone_attr))
        fg = ftr.GetGeometryRef()
        polys = []
        for g in xrange(fg.GetGeometryCount()):
            geom = fg.GetGeometryRef(g)
            geom.Transform(ct)
            polys.append(shapely.geometry.Polygon(geom.GetPoints()))
            
        if len(polys)>1:
            zone_polys.append(shapely.geometry.MultiPolygon(polys))
        else:
            zone_polys.append(polys[0])
            
    stats = zonalstats(raster,zone_polys,raster_band=0)
    
    stats_file = open(stats_path,'w')
    stat_names = stats[0].keys()
    h = 'zone_id,'
    h += '{}\n'.format(','.join(
            ['{}{}'.format(prefix,stat) for stat in stat_names]))
    stats_file.write(h)

    for i,zone_id in enumerate(zone_ids):
        l = '{:<d},'.format(zone_id)
        l += '{}\n'.format(','.join(
                ['{}'.format(stats[i][stat]) for stat in stat_names]))
        stats_file.write(l)

def get_poly_gridvalues(poly_geom,rasterband,minx,maxy,cellwidth,cellheight):
    """
    Return a numpy masked array of grid values intersecting a geometry.
    
    Args:
        poly_geom: Shapely geometry to intersect with the grid.
        rasterband: GDAL raster band to extract values from.
        minx: Raster origin X coordinate (left edge).
        maxy: Raster origin Y coordinate (top edge).
        cellwidth: Raster grid cell width.
        cellheight: Raster grid cell height (negative value).
    
    Returns:
        array: A Numpy masked array with intersecting grid values unmasked.
    
    Notes:
        Cell height is generally a negative value since raster grids originate 
        at the top left by convention.  Computing offsets is then an additive
        process from left to right and top to bottom.
        
    """
    #compute the envelope orgin cell and the window size
    env = poly_geom.bounds
    xoff = int((env[0]-minx)/cellwidth)
    yoff = int((env[3]-maxy)/cellheight)
    xwin = int((env[2]-(minx + xoff * cellwidth))/cellwidth) + 1
    ywin = int((env[1]-(maxy + yoff * cellheight))/cellheight) + 1
    
    #get a masked array of all grid values intersecting the polygon envelope
    grid_values = numpy.ma.masked_array(
            rasterband.ReadAsArray(xoff,yoff,xwin,ywin),mask=1)
    
    #create a shapely (GEOS) prepared geometry to speedup the intersect process
    prep_geom = shapely.prepared.prep(poly_geom)

    #unmask grid values whos centers are within the polygon
    for col in xrange(xwin):
        xcoord = minx + (xoff+col+0.5) * cellwidth
        for row in xrange(ywin):
            ycoord = maxy + (yoff+row+0.5) * cellheight
            pnt = shapely.geometry.Point(xcoord,ycoord)
            
            if prep_geom.contains(pnt):
                grid_values.mask[row,col] = numpy.ma.nomask
    
    return grid_values

class Raster(list):
    def __init__(self, raster_path):
        """
        Represents a GDAL raster with convenience methods for data access.
        """
        self.path = raster_path
        
        self.__initialize_raster()
        
    def __initialize_raster(self):
        self.raster = gdal.OpenShared(self.path)
        self.row_count = self.raster.RasterXSize
        self.col_count = self.raster.RasterYSize
        gt = self.raster.GetGeoTransform()
        self.minx = gt[0]
        self.cellwidth = gt[1]
        self.maxy = gt[3]
        self.cellheight = gt[5]
        self.maxx = self.minx + self.row_count * self.cellwidth
        self.miny = self.maxy + self.col_count * self.cellheight
        
        self.bands = [self.raster.GetRasterBand(i+1)
                for i in xrange(self.raster.RasterCount)]
        
        self.spatial_ref = osr.SpatialReference()
        self.spatial_ref.ImportFromWkt(self.raster.GetProjection())
    
    def __getitem__(self,i):
        return self.bands[i]
        
def zonalstats(value_raster,zone_polys,raster_band=0):
    """
    Compute statistics for raster grid centers contained by each polygon
    
    Args:
        value_raster (Raster): Raster object to compute zone statistics from.
        zone_polys (iterable): Tuples of shapely compatible zone polygons and
                associated zone ids.
        raster_band (int): Band number of the raster to use as zone values.
    
    Returns:
        names (tuple): Names of zone stats computed
        values (list): List of dicts containing the 
    """
    value_band = value_raster[raster_band]

    minx = value_raster.minx
    maxy = value_raster.maxy
    cellwidth = value_raster.cellwidth
    cellheight = value_raster.cellheight
    
    stats = []
    for p,poly in enumerate(zone_polys):
        gridvalues = get_poly_gridvalues(
                poly, value_band
                ,minx,maxy,cellwidth,cellheight)
        stats.append(calc_stats(gridvalues))

        if p%100.0==0.0:
            print(p)
#            print stats
    
#        if f>=99: break
#        print gridvalues
#        print stats[p]
#        break

    print('Computed stats for {:<d} zones'.format(p+1))
    return stats

def batch(rasters,zones_dsn,zones_sql,zones_attr,dest,basename
        ,bands=None,names=None):
            
    for i,raster in enumerate(raster):
        if bands:
            b=bands[i]
        else:
            b=0
            
        if names:
            n=names[i]
        else:
            n=os.path.split(raster)[-1]
            n=os.path.splitext(n)[0]
        
        output = basename.format(n)
        
        main(raster,zones_dsn,zones_sql,zones_attr,output,raster_band=b)

def test():
    r = r'C:\data\landsat\landsat8\ls_201306_allbands.vrt'
    b = (2,3,4,5,6,7)
    
def xtest():
    r = '/mnt/shared_partition/shared/data/landsat/LC80470282013159LGN00/LC80470282013159LGN00_B4.TIF'
    d = '/mnt/shared_partition/shared/data/SLI/TL2010ROOTSfiles'
    s = 'select * from SLIpoly where STD_ID<99999 order by STD_ID'
    a = 'STD_ID'
    f = '/mnt/shared_partition/shared/data/SLI/TL2010ROOTSfiles/zone_stats.txt'
    
    r = r'C:\data\landsat\landsat8\ls_201306_allbands.vrt'
    p = 'LS8_B2_'
    d = r'C:\data\SLI\Tillamook\TL20110407ROOTSfiles'
    f = r'C:\data\SLI\Tillamook\TL20110407ROOTSfiles\TL_LS9_B2_zonal_stats.csv'
#    f = r'C:\data\SLI\Tillamook\TL20110407ROOTSfiles\foo.csv'
    w = r'C:\data\SLI\Tillamook\TL20110407ROOTSfiles'
    
    main(r,d,s,a,f,prefix=p,raster_band=1)
    
if __name__=='__main__':
    if '--test' in sys.argv:
        test()
        
    else:
        main(*sys.argv[1:])
