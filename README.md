# OS_jpg_to_geotiff

Geolocate OS 1 Inch Old Series England Wales maps found here https://commons.wikimedia.org/wiki/Category:Ordnance_Survey_Old/First_series_England_and_Wales_1:63360_

### Install dependencies  
PIL `pip install pillow`.
GDAL must match system gdal.
gdainfo --version.
`pip install gdal==2.4`.

### Jpg files prep -- Skip is using TIFF files
Add jpg files to a new folder called `./OS_jpgs`. Jpgs are found here https://commons.wikimedia.org/wiki/Category:Ordnance_Survey_Old/First_series_England_and_Wales_1:63360_

Ensure the files are named with the map sheet number at the end and in the following format `OS_old_series_1_63360_8.jpg`. See One_Inch_Old_Series_England_Wales.geojson `properties['Name']` value.

Convert jpgs to tiffs using `python3 jpg_to_tif.py`.

### Create Geotiffs
Convert tiffs to GeoTiffs using `python3 OS_tiff_to_geotiff.py`.

Click on four corners of map area in NW, NE, SE, SW order.
Remember when moving focus to the image popup click on the top of the popup where it says 'tk' otherwise you will use up once of your clicks in moving the focus.

You will find your Geotiffs in `./OS_geotiffs`.
