# compute coordinates of tif pixel
# https://stackoverflow.com/questions/50191648/gis-geotiff-gdal-python-how-to-get-coordinates-from-pixel

import gdal,osr,pyproj,sys

def crs_ref():
        # create lat/long crs with WGS84 datum
        # same as PROJ.4 : +proj=longlat +datum=WGS84 +no_defs
        # test with gdalsrsinfo epsg:4326
        crs = osr.SpatialReference()
        #crs.ImportFromEPSG(4326) # 4326 is the EPSG id of lat/long crs 
        crs.SetWellKnownGeogCS('WGS84')
        return crs

def crs_ds(ds):
        # get CRS from dataset 
        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjectionRef())
        return crs

def xy2lonlat(name,x,y):
        ds=gdal.Open(name)
        xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
    
        # supposing x and y are your pixel coordinate this 
        # is how to get the coordinate in space.
        posX = px_w * x + rot1 * y + xoffset
        posY = rot2 * x + px_h * y + yoffset
    
        # shift to the center of the pixel
        posX += px_w / 2.0
        posY += px_h / 2.0

        t = osr.CoordinateTransformation(crs_ds(ds), crs_ref())
        lat, lon, z = t.TransformPoint(posX, posY)
        return lon, lat

def lonlat2xy(name,lon,lat):
        ds=gdal.Open(name)
        xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()

        t = osr.CoordinateTransformation(crs_ref(),crs_ds(ds))
        posX, posY, z  = t.TransformPoint(lat,lon,0)

        posX -= px_w / 2.0
        posY -= px_h / 2.0

        transform = ds.GetGeoTransform()
        gt = [transform[0],transform[1],0,transform[3],0,transform[5]]
        inverse_gt = gdal.InvGeoTransform(gt)
  
        x = inverse_gt[0] + inverse_gt[1] * posX + inverse_gt[2] * posY
        y = inverse_gt[3] + inverse_gt[4] * posX + inverse_gt[5] * posY

        return x,y

def test_inv(name,x,y):
    print "converting to WGS84 lon lat and back"
    lon, lat = xy2lonlat(name,x,y)
    print 'pixel',x,y,'lon lat',lon,lat
    xx,yy = lonlat2xy(name,lon,lat)
    # print 'pixel',xx,yy,'lon lat',lon,lat
    print "error",xx-x,yy-y
    
if __name__ == '__main__':
    if len(sys.argv) == 4:
        name = sys.argv[1] 
        x=float(sys.argv[2])
        y=float(sys.argv[3])
        test_inv(name,x,y)
    if len(sys.argv) == 6:
        name = sys.argv[1] 
        x1=float(sys.argv[2])
        y1=float(sys.argv[3])
        x2=float(sys.argv[4])
        y2=float(sys.argv[5])
        test_inv(name,x1,y1)
        test_inv(name,x2,y2)
        lon1, lat1 = xy2lonlat(name,x1,y1)
        lon2, lat2 = xy2lonlat(name,x2,y2)
        geod = pyproj.Geod(ellps='WGS84')
        azimuth1, azimuth2, distance = geod.inv(lon1, lat1, lon2, lat2)
        print 'distance', distance
        print 'azimuth', azimuth1, azimuth2
    else:
        print "usage: file.tif x y"
        print "usage: file.tif x1 y1 x2 y2"
        sys.exit(1)

