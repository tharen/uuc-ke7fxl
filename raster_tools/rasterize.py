import sys
import os

import gdal
import ogr
import osr

def rasterize(poly,dest,target,attr):
    """
    Rasterize a polygon dataset, aligning the extent with a target image
    """
    
    #open the target raster
    targ = gdal.OpenShared(target)
    
    #open the polygon layer
    ds,p = os.path.split(poly)
    lyr_name,ext = os.path.splitext(p)
    
    print('Datasource: {}'.format(ds))
    print('Layer Name: {}'.format(lyr_name))

    poly_ds = ogr.OpenShared(ds)
    poly_lyr = poly_ds.GetLayerByName(lyr_name)

    targ_srs = osr.SpatialReference()
    targ_srs.ImportFromWkt(targ.GetProjection())
    poly_srs = osr.SpatialReference()
    poly_srs.ImportFromWkt(poly_lyr.GetSpatialRef().ExportToWkt())
    coord_trans = osr.CoordinateTransformation(poly_srs, targ_srs)

    temp_ds = ogr.GetDriverByName('Memory').CreateDataSource('temp')
    temp_lyr = temp_ds.CreateLayer('temp',srs=targ_srs)

    gt = targ.GetGeoTransform()
    pixx = int(gt[1])
    pixy = int(abs(gt[5]))
    
    pixx = targ.GetRasterBand(1).XSize
    pixy = targ.GetRasterBand(1).YSize

    ftr = poly_lyr.GetFeature(0)
    f = ftr.GetFieldDefnRef(attr)
    temp_lyr.CreateField(f)
    temp_defn = temp_lyr.GetLayerDefn()

    while ftr:
        g = ftr.GetGeometryRef()
        g.Transform(coord_trans)
        
        new_ftr = ogr.Feature(temp_defn)
        new_ftr.SetGeometry(g)
        new_ftr.SetField(attr,ftr.GetField(attr))
        temp_lyr.CreateFeature(new_ftr)

        ftr.Destroy()
        new_ftr.Destroy()

        ftr = poly_lyr.GetNextFeature()

    driver = gdal.GetDriverByName('GTIFF')
    outds = driver.Create(dest,pixx,pixy,1,gdal.GDT_UInt32)
    outds.SetProjection(targ.GetProjection())
    outds.SetGeoTransform(targ.GetGeoTransform())

    gdal.RasterizeLayer(outds, [1], temp_lyr
                        , options=['ATTRIBUTE={}'.format(attr)]
                        )
    
    print('Output: {}'.format(dest))
    poly_lyr = None
    temp_lyr = None

    return outds

if __name__=='__main__':
    rasterize(*sys.argv[1:])
