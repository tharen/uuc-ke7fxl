
import os
import sys

import numpy
import gdal
import ogr
import osr
import shapely.geometry
import shapely.prepared

import rasterize

def calc_stats(values):
    mean = numpy.mean(values)
    stdev = numpy.std(values)
    min,p01,p025,p05,p10,p25,p50,p75,p90,p95,p975,p99,max = numpy.percentile(
        values,(0.0,0.01,0.25,0.05,0.10,0.25,0.5,0.75,0.90,0.95,0.975,0.99,1.0)
        )

    stats = locals()
    stats.pop('values')

    return(stats)

def main(raster_path,dsn,sql,attr,stats_path,wkspc):
    value_raster = gdal.Open(raster_path)
    value_band = value_raster.GetRasterBand(1)

    stats_file = open(stats_path,'w')
    stats_names = ('zone_id','mean','stdev','min','p01','p025','p05','p10'
            ,'p25','p50','p75','p90','p95','p975','p99','max')
    stats_file.write('{}\n'.format(','.join(stats_names)))

    minx,cellwidth,xrot,maxy,yrot,cellheight = value_raster.GetGeoTransform()
    to_srs = osr.SpatialReference()
    to_srs.ImportFromWkt(value_raster.GetProjection())

    zone_ds = ogr.Open(dsn)
    zone_lyr = zone_ds.ExecuteSQL(sql)
    from_srs = zone_lyr.GetSpatialRef()

    coord_trans = osr.CoordinateTransformation(from_srs, to_srs)

    for f,ftr in enumerate(zone_lyr):
        zone_id = ftr.GetFieldAsString(attr)
        zone_geom = ftr.GetGeometryRef()
        zone_geom.Transform(coord_trans)

        #compute the envelope orgin cell and the window size
        env = zone_geom.GetEnvelope()
        xoff = int((env[0]-minx)/cellwidth)
        yoff = int((env[3]-maxy)/cellheight)
        xwin = int((env[1]-(minx + xoff * cellwidth))/cellwidth) + 1
        ywin = int((env[2]-(maxy + yoff * cellheight))/cellheight) + 1
        grid_values = numpy.ma.masked_array(value_band.ReadAsArray(xoff,yoff,xwin,ywin),mask=1)
#        print grid_values

        #create a prepared GEOS geometry object for faster batch testing
        zone_geom = shapely.geometry.Polygon(zone_geom.GetGeometryRef(0).GetPoints())
        zone_geom = shapely.prepared.prep(zone_geom)

        for col in xrange(xwin):
            xcoord = minx + (xoff+col+0.5) * cellwidth

            for row in xrange(ywin):
                ycoord = maxy + (yoff+row+0.5) * cellheight

#                print xcoord,ycoord
                pnt = shapely.geometry.Point(xcoord,ycoord)

                if zone_geom.contains(pnt):
                    grid_values.mask[row,col] = 0

        stats = calc_stats(grid_values)
        stats['zone_id']=zone_id
        stats_file.write('{}\n'.format(','.join('{}'.format(stats[stat]) for stat in stats_names)))

        if f%100.0==0.0:
            print(f)
#            print stats

        if f>=99: break

#        print grid_values
#        break

    print('Computed stats for {:<d} zones'.format(f+1))
    return stats_path

def test():
    r = '/mnt/shared_partition/shared/data/landsat/LC80470282013159LGN00/LC80470282013159LGN00_B4.TIF'
    d = '/mnt/shared_partition/shared/data/SLI/TL2010ROOTSfiles'
    s = 'select * from SLIpoly where STD_ID<99999 order by STD_ID'
    a = 'STD_ID'
    f = '/mnt/shared_partition/shared/data/SLI/TL2010ROOTSfiles/zone_stats.txt'
    w = '/mnt/shared_partition/shared/data/SLI/TL2010ROOTSfiles'

    main(r,d,s,a,f,w)

if __name__=='__main__':
    if '--test' in sys.argv:
        test()

    else:
        main(*sys.argv[1:])
