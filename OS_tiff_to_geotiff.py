# gdal must match system gdal
# gdainfo --version
# pip install gdal==2.4
#  Example, GDAL 2.4, Python 3.8, Windows x64
#    Download the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal -- GDAL-2.4.1-cp38-cp38-win_amd64.whl 
#    python -m pip install c:\temp\GDAL-2.4.1-cp38-cp38-win_amd64.whl --user

import gdal #recent versions of Python: from osgeo import gdal
import osr
import shutil
import os
import json
import pdb

from tkinter import *
from tkinter.filedialog import askopenfilename
# pip install pillow
from PIL import Image, ImageTk, ImageDraw

# bypass error: "PIL.Image.DecompressionBombError: Image size (211225084 pixels) exceeds limit of 178956970 pixels, could be decompression bomb DOS attack."
Image.MAX_IMAGE_PIXELS = None

def createDir(path):
    if not os.path.exists(path):
        os.mkdir(path)

createDir('./OS_gcps/')
createDir('./OS_tiffs_gcps/')
createDir('./OS_geotiffs/')
createDir('./OS_tiffs_cut/')

# Extract the map area
def extractMap(path):
    event2canvas = lambda e, c: (c.canvasx(e.x), c.canvasy(e.y))
    if __name__ == "__main__":
        root = Tk()

        #setting up a tkinter canvas with scrollbars
        frame = Frame(root, width=1500, height=1000, bd=2, relief=SUNKEN)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        xscroll = Scrollbar(frame, orient=HORIZONTAL)
        xscroll.grid(row=1, column=0, sticky=E+W)
        yscroll = Scrollbar(frame)
        yscroll.grid(row=0, column=1, sticky=N+S)
        canvas = Canvas(frame, bd=0, width=1500, height=1000, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        canvas.grid(row=0, column=0, sticky=N+S+E+W)
        xscroll.config(command=canvas.xview)
        yscroll.config(command=canvas.yview)
        frame.pack(fill=BOTH,expand=True)

        #adding the image
        # File = askopenfilename(parent=root, initialdir="./",title='Choose an image.')
        # print("opening %s" % File)
        img = Image.open('./OS_tiffs/' + path)
        imgTk = ImageTk.PhotoImage(Image.open('./OS_tiffs/' + path))
        canvas.create_image(0,0,image=imgTk,anchor="nw")
        canvas.config(scrollregion=canvas.bbox(ALL))

        global corners_pixels
        corners_pixels = []

        #function to be called when mouse is clicked
        def printcoords(event):
            #outputting x and y coords to console
            cx, cy = event2canvas(event, canvas)
            print ("(%d, %d) / (%d, %d)" % (event.x,event.y,cx,cy))
            if [cx,cy] not in corners_pixels:
                print(len(corners_pixels))
                corners_pixels.append([cx,cy])
                if len(corners_pixels) > 3:
                    # Cut map from image border
                    mask=Image.new('L', img.size, color=0)
                    draw=ImageDraw.Draw(mask)

                    points = tuple(tuple(sub) for sub in corners_pixels)
                    draw.polygon((points), fill=255)
                    img.putalpha(mask)

                    rgb = Image.new('RGB', img.size, (255, 255, 255))
                    rgb.paste(img, mask=img.split()[3])
                    rgb.save('./OS_tiffs_cut/' + path, 'TIFF', resolution=100.0)
                    root.destroy()

    #mouseclick event
    canvas.bind("<ButtonPress-1>",printcoords)
    # canvas.bind("<ButtonRelease-1>",printcoords)
    root.mainloop()

OS_coords = json.load(open('./One_Inch_Old_Series_England_Wales.geojson'))

def createCornerLatLng(sheet_r):
    for f in OS_coords['features']:
        if f['properties']['Name'] == sheet_r:
            coords = f['geometry']['coordinates'][0]
            break

        # TODO Sort corners_pixels
        corners = [
          # {'location': [corners_latLng['x_west_edge'], corners_latLng['y_north_edge']], 'pixel': corners_pixels[0]},
          {'location': coords[0], 'pixel': corners_pixels[0]},
          {'location': coords[1], 'pixel': corners_pixels[1]},
          {'location': coords[2], 'pixel': corners_pixels[2]},
          {'location': coords[3], 'pixel': corners_pixels[3]}
        ]
        # TODO Save corners
    return corners

def createGcps(coords):
    gcps = []
    for coord in coords:
        # 'coord' = {'location': [-3.756732387660781, 50.57983418053561], 'pixel': [2164, 966]}
        col = coord['pixel'][0]
        row = coord['pixel'][1]
        x = coord['location'][0]
        y = coord['location'][1]
        z = 0
        gcp = gdal.GCP(x, y, z, col, row)
        gcps.append(gcp)

    return gcps

# # https://stackoverflow.com/questions/55681995/how-to-georeference-an-unreferenced-aerial-imgage-using-ground-control-points-in
def addGcps(path, gcps):
  src = './OS_tiffs_cut/' + path
  dst = './OS_tiffs_gcps/' + path
  # Create a copy of the original file and save it as the output filename:
  shutil.copy(src, dst)
  # Open the output file for writing for writing:
  ds = gdal.Open(dst, gdal.GA_Update)
  # Set spatial reference:
  sr = osr.SpatialReference()

  # WGS84 sr.ImportFromEPSG(4326)
  sr.ImportFromEPSG(3857)

  # Apply the GCPs to the open output file:
  ds.SetGCPs(gcps, sr.ExportToWkt())

  # Close the output file in order to be able to work with it in other programs:
  ds = None

def createGeoTiff(path):
  src = './OS_tiffs_gcps/' + path
  dst = './OS_geotiffs/' + path
  input_raster = gdal.Open(src)
  # WGS 84 gdal.Warp(dst,input_raster,dstSRS='EPSG:4326',dstNodata=255)
  gdal.Warp(dst,input_raster,dstSRS='EPSG:3857',dstNodata=255)

tiffpaths = os.listdir('./OS_tiffs')

for path in tiffpaths:
    if not path.startswith('.'): 
        print(path)
        sheet_ref = path.replace('OS_old_series_1_63360_', '').replace('.tif', '')
        extractMap(path)
        corners = createCornerLatLng(sheet_ref)
        gcps = createGcps(corners)
        addGcps(path, gcps)
        createGeoTiff(path)

shutil.rmtree('./OS_tiffs_gcps/')
shutil.rmtree('./OS_gcps/')
shutil.rmtree('./OS_tiffs_cut/')
