
import os
import sys

import numpy
import gdal
import ogr
import osr
import shapely.wkb
import shapely.geometry
import shapely.prepared

import pylab

def main(zones_path,zones_attr,raster_path,output_path,tolerance=0.1):
    
    raster = gdal.Open(raster_path, gdal.GA_ReadOnly)
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjection())
#    print raster.GetProjection()
    raster_gt = raster.GetGeoTransform()
    
    d,f = os.path.split(zones_path)
    l,e = os.path.splitext(f)
    zones_ds = ogr.Open(d,update=False)
    #zones_lyr = zones_ds.GetLayerByName(l)
    zones_lyr = zones_ds.ExecuteSQL('select * from {} order by {}'.format(l,zones_attr))
    zones_srs = zones_lyr.GetSpatialRef()
    
    output = open(output_path,'w')
    flds = ('zone_id','zmean','zstd','zmin','zp025','zp05','zp10'
            ,'zp25','zp50','zp75','zp90','zp95','zp975','zmax')
    output.write('{}\n'.format(','.join(flds)))
    
    # Project zone features to the SRS of the raster    
    coord_trans = osr.CoordinateTransformation(zones_srs,raster_srs)
    
    # Create an in memory layer to hold the BBOX raster values
    temp_drv = ogr.GetDriverByName('Memory')
    temp_ds = temp_drv.CreateDataSource('temp')
    temp_lyr = temp_ds.CreateLayer('temp',raster_srs,ogr.wkbPoint)
    temp_fld = ogr.FieldDefn('value',ogr.OFTReal)
    temp_lyr.CreateField(temp_fld)
    
    fc=0
    zone_ftr = zones_lyr.GetNextFeature()
    w = abs(raster_gt[1])
    h = abs(raster_gt[5])
    while zone_ftr:
        fc+=1
        
        if fc%100.0==0.0:
            print fc
        
        zone_id = zone_ftr.GetField(zones_attr)
        
        #transform the zone geometry to match the value raster        
        zone_geom = zone_ftr.GetGeometryRef()
        zone_geom.Transform(coord_trans)
        
        #Create a vector grid of cell center points
        env = zone_geom.GetEnvelope()
        bbox_offset = bbox2offset(env,raster_gt)
        
        vals = numpy.ma.masked_array(
                raster.ReadAsArray(*bbox_offset)
                , mask=1)
#        print vals
        
#        zone_poly = shapely.wkb.loads(zone_geom.ExportToWkb())
#        zone_poly = shapely.prepared.prep(zone_poly.exterior)

        pnts = zone_geom.GetGeometryRef(0).GetPoints()
        zone_poly = shapely.geometry.Polygon(pnts)
#        p = zone_poly.centroid
#        print p
#        print zone_poly.envelope
#        zone_poly = shapely.prepared.prep(zone_poly.envelope)
        
#        grid_points = numpy.empty(vals.shape,dtype=numpy.object)
#        mask = numpy.ones(grid_points.size,dtype=int)
        
        # Origin row center (top row center)        
        y0 = raster_gt[3] + (bbox_offset[1] + 0.5) * raster_gt[5]
        gi=0
        for r in xrange(bbox_offset[3]):
            #increment the row center coordinate
            y = y0 + r * raster_gt[5]
            
            #Reset the origin column center (left column center)
            x0 = raster_gt[0] + (bbox_offset[0] + 0.5) * raster_gt[1]
            for c in xrange(bbox_offset[2]):
#                print r,c
                #increment the column center coordinate
                x = x0 + c * raster_gt[1]
                
#                print x,y
#                g.SetPoint_2D(0,x,y)
#                if not zone_geom.Contains(g):
#                p = shapely.geometry.Point(x,y)
#                #if not zone_poly.intersects(p):
#                if not p.within(zone_poly):
#                    vals[r,c] = numpy.ma.masked
#                print y,x
                p = shapely.geometry.Point(x,y)
                gi += 1
                if zone_poly.contains(p):
                    vals.mask[r,c] = numpy.ma.nomask
                p = None
        
        ##TODO: mask is only covering the west edge
        #gp = grid_points.flat
        #m = numpy.zeros(gp.shape,dtype=bool)
        #m = map(zone_poly.contains, grid_points.flat)
#        for i,p in enumerate(grid_points.flat):
#            if zone_poly.contains(p):
#                print i
#                mask[i]=numpy.ma.masked
#        print mask
#        vals.mask = mask.reshape(grid_points.shape)
                #g.Destroy()
        
#        print m
#        print vals
#        break
#        vals = numpy.ma.masked_array(vals,numpy.isnan(vals))
        zmean = numpy.mean(vals)
        zstd = numpy.std(vals)
        zmin = numpy.min(vals)
        zp025 = numpy.percentile(vals,2.5)
        zp05 = numpy.percentile(vals,5.0)
        zp10 = numpy.percentile(vals,10.0)
        zp25 = numpy.percentile(vals,25.0)
        zp50 = numpy.percentile(vals,50.0)
        zp75 = numpy.percentile(vals,75.0)
        zp90 = numpy.percentile(vals,90.0)
        zp95 = numpy.percentile(vals,95.0)
        zp975 = numpy.percentile(vals,97.5)
        zmax = numpy.max(vals)
        
        w = ('{zone_id},{zmean:<.3f},{zstd:<.3f},{zmin:<.3f}'
            ',{zp025:<.3f},{zp05:<.3f},{zp10:<.3f},{zp25:<.3f}'
            ',{zp50:<.3f},{zp75:<.3f},{zp90:<.3f},{zp95:<.3f}'
            ',{zp975:<.3f},{zmax:<.3f}'.format(**locals()))
            
        output.write(w + '\n')
        
        zone_ftr.Destroy()
        zone_ftr = zones_lyr.GetNextFeature()
        
        if fc>100:
            break
    
    output.close()

def point_in_poly(x,y,poly):
    #http://geospatialpython.com/2011/01/point-in-polygon.html
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
    
def bbox2offset(bbox,gt):
#    print bbox
#    print gt
    
    x1 = int((bbox[0]-gt[0])/gt[1])
    x2 = int((bbox[1]-gt[0])/gt[1]) + 1
    y1 = int((bbox[3]-gt[3])/gt[5])
    y2 = int((bbox[2]-gt[3])/gt[5]) + 1
    
    winx = x2 - x1
    winy = y2 - y1
    
#    print x1,y1,winx,winy
    return (x1,y1,winx,winy)

def test():
    z=r'C:\data\SLI\Tillamook\TL20110407ROOTSfiles\SLIpoly.shp'
    a='STD_ID'
    r=r'C:\data\landsat\tm5\LT50470282011186PAC01\L5047028_02820110705_B40.TIF'
    o=r'c:\temp\zonal_stats\tl_sli_b4x.csv'
    main(z,a,r,o)
    
if __name__=='__main__':
    if '--test' in sys.argv:
        test()
        
    else:
        main(*sys.argv[1:])