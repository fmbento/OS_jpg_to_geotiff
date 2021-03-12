import os
import sys
from PIL import Image

originPath = './OS_jpgs/'

def createDir(path):
    if not os.path.exists(path):
        os.mkdir(path)

createDir('./OS_tiffs/')

def getFiles (originPath):
    originPaths = []
    for (dirpath, dirnames, filenames) in os.walk(originPath):
        originPaths.extend(filenames)
    return originPaths

originPaths = getFiles(originPath)

def processImage(infile):
    try:
        im = Image.open(infile)
    except IOError:
        print("Cant load", infile)
        sys.exit(1)

    try:
        infileLength = len(infile.split('.')[0].split('/'))
        im.save('./OS_tiffs/'+ infile.split('.')[1].split('/')[-1] +'.tif')

    except EOFError:
        pass # end of sequence

for p in originPaths:
    if 'jpg' in p:
        processImage(originPath + p)
