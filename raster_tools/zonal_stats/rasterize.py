import sys
import os
import logging
import time

import gdal
import ogr
import osr

#initialize the logger
log = logging.getLogger('zonal.rasterize')
hdlr = logging.StreamHandler(stream=sys.stdout)
log.addHandler(hdlr)

def rasterize(source_dataset,out_raster,align_raster,attr,clip=False):
    """
    Rasterize a polygon dataset, aligning the extent with a target raster.
    
    Args
    ----
    @param source_dataset: Path name of the dataset to rasterize.
    @param out_raster: Path name of the output raster dataset.
    @param align_raster: Path name of the raster image to align to.
    @param attr: Attribute of source_dataset to use as the grid value.
    @param clip: Clip the output to the extent of the input dataset.
    """
    
    tt = time.clock()
    
    #open the align_raster
    align = gdal.OpenShared(align_raster)
    
    #open the source_dataset layer
    ds,p = os.path.split(source_dataset)
    lyr_name,ext = os.path.splitext(p)    
    log.info('Rasterize features - datasource: {}, layer: {}'.format(ds,lyr_name))
    src_ds = ogr.OpenShared(ds)
    src_lyr = src_ds.GetLayerByName(lyr_name)
    
    #setup a coordinate transformation between the feature dataset and the align_raster
    align_srs = osr.SpatialReference()
    align_srs.ImportFromWkt(align.GetProjection())
    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(src_lyr.GetSpatialRef().ExportToWkt())
    coord_trans = osr.CoordinateTransformation(src_srs, align_srs)
    
    #Open an in-memory OGR dataset to hold projected features
    temp_ds = ogr.GetDriverByName('Memory').CreateDataSource('temp')
    temp_lyr = temp_ds.CreateLayer('temp',srs=align_srs)

    st=time.clock()
    ftr = src_lyr.GetFeature(0)
    f = ftr.GetFieldDefnRef(attr)
    temp_lyr.CreateField(f)
    temp_defn = temp_lyr.GetLayerDefn()
    
    i=0
    while ftr:
        i+=1
        g = ftr.GetGeometryRef()
        g.Transform(coord_trans)
        
        new_ftr = ogr.Feature(temp_defn)
        new_ftr.SetGeometry(g)
        new_ftr.SetField(attr,ftr.GetField(attr))
        temp_lyr.CreateFeature(new_ftr)

        ftr.Destroy()
        new_ftr.Destroy()

        ftr = src_lyr.GetNextFeature()
        
    log.debug('Projected {} features in {:<.3f} seconds'.format(i,(time.clock()-st)))
    #Create a new raster to hold the rasterized features
    driver = gdal.GetDriverByName('GTIFF')
    
    d,f = os.path.split(out_raster)
    if not os.path.exists(d):
        log.info('Created output folder: {}'.format(d))
        os.makedirs(d)
        
    #Match the size and shape of the align_raster
    pixx = align.GetRasterBand(1).XSize
    pixy = align.GetRasterBand(1).YSize
    ##TODO: determine datatype of the source attribute
    outds = driver.Create(out_raster,pixx,pixy,1,gdal.GDT_UInt32
            ,['COMPRESS=PACKBITS']
            )
    outds.SetProjection(align.GetProjection())
    outds.SetGeoTransform(align.GetGeoTransform())

    st=time.clock()
    #rasterize the projected features into the new raster dataset
    gdal.RasterizeLayer(outds, [1], temp_lyr
                        , options=['ATTRIBUTE={}'.format(attr)]
                        )
    
    log.debug('Rasterized in {:<.3f} seconds'.format(time.clock()-st))
    log.info('Rasterized features to: {}'.format(out_raster))
    log.info('Completed rasterization in {:<.3f}'.format(time.clock()-tt))
    
    align = None
    outds = None
    src_lyr = None
    temp_lyr = None

    return out_raster

def test():
    a=r'C:\data\landsat\tm5\LT50470282011186PAC01\L5047028_02820110705_B40.TIF'
    d=r'c:\temp\zonal_stats\zones.tif'
    s=r'C:\data\SLI\Tillamook\TL20110407ROOTSfiles\SLIpoly.shp'
    
    log.setLevel(logging.DEBUG)
    rasterize(s,d,a,'STD_ID',False)
    
if __name__=='__main__':
    if '--test' in sys.argv:
        test()
        sys.exit()
        
    rasterize(*sys.argv[1:])
