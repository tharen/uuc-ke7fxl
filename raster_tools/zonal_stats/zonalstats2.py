
import os
import sys

import numpy
import gdal
import ogr
import osr

def main(zones_path,zones_attr,raster_path,output_path,tolerance=0.1):
    
    raster = gdal.Open(raster_path, gdal.GA_ReadOnly)
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjection())
    raster_gt = raster.GetGeoTransform()
    
    d,f = os.path.split(zones_path)
    l,e = os.path.splitext(f)
    zones_ds = ogr.Open(d,update=False)
    zones_lyr = zones_ds.GetLayerByName(l)
    zones_srs = zones_lyr.GetSpatialRef()
    
    output = open(output_path,'w')
    
    # Project zone features to the SRS of the raster    
    coord_trans = osr.CoordinateTransformation(zones_srs,raster_srs)
    
    mem_drv = gdal.GetDriverByName('MEM')
    
    fc=0
    ftr = zones_lyr.GetNextFeature()
    w = raster_gt[1]
    h = raster_gt[5]
    while ftr:
        fc+=1
        
        if fc%100.0==0.0:
            print fc
            
        zone_id = ftr.GetField(zones_attr)
        geom = ftr.GetGeometryRef()
        geom.Transform(coord_trans)
        
        #Create a vector grid of cell center points
        bbox = geom.GetEnvelope()
        bbox_offset = bbox2offset(bbox, raster_gt)
#        bbox_vals = raster.ReadAsArray(*bbox_offset)
        bbox_pnts = ogr.Geometry(type=ogr.wkbMultiPoint)
#        g_mask = numpy.ones(bbox_vals.shape,numpy.bool)
        p=[None] * (bbox_offset[3]*bbox_offset[2])
        g=0
        for r in xrange(bbox_offset[3]):
            for c in xrange(bbox_offset[2]):
                x = (c + 0.5) * w + bbox[0]
                y = (r + 0.5) * h + bbox[3]
                
#                print len(p),i,x,y
                p[g] = (x,y)
                g += 1
                
        p = ','.join('{} {}'.format(*c) for c in p)
        pnts = ogr.CreateGeometryFromWkt('MULTIPOINT({})'.format(p))
        bbox_pnts.AddGeometry(pnts)
#        buff = geom.Buffer(tolerance)
#        bbox_pnts = bbox_pnts.Intersection(buff)
        
#        n = bbox_pnts.GetGeometryCount()
#        if n>0:
#            vals = numpy.zeros((n))
#            
#            for gc in xrange(n):
#                pnt = bbox_pnts.GetGeometryRef(gc)
#                x = pnt.GetX()
#                y = pnt.GetY()
#                
#                c = (x - raster_gt[0])/raster_gt[2]
#                r = (y - raster_gt[3])/raster_gt[5]
#                
#                vals[gc] = raster.ReadAsArray[r,c]
#            
#            mean = numpy.mean(vals)
#            stdev = numpy.std(vals)
#        
#            output.write('{zone_id},{mean},{stdev}\n'.format(**locals()))
        
#                if not gc.Within(g):
#                    g_mask[r,c]=0
        
#        g_gt = (raster_gt[0] + (bbox_offset[0] * raster_gt[1])
#                ,raster_gt[1],0.0
#                raster_gt[3] + (bbox_offset[1]*raster_gt[5])
#                ,0.0,raster_gt[5]
#                )
#        temp_ds = driver.Create('',pixx,pixy,1,gdal.GDT_Byte)
#        temp_ds.SetProjection(raster_srs)
#        temp_ds.SetGeoTransform(g_gt)
        
#        print zone_id
#        print g_mask
#        print bbox_vals*g_mask
#
#        print numpy.mean(bbox_vals[g_mask])
#        print numpy.median(vals)
#        print numpy.std(vals)
        
        ftr.Destroy()
        ftr = zones_lyr.GetNextFeature()
        
        if fc>10000:
            break

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
    o=r'c:\temp\zonal_stats\tl_sli_b4.csv'    
    main(z,a,r,o)
    
if __name__=='__main__':
    if '--test' in sys.argv:
        test()
        
    else:
        main(*sys.argv[1:])