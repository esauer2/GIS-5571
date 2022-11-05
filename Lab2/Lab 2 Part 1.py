# Import necessary packages
import requests
import json
import zipfile
import io
import pandas as pd
import os
import arcpy

# Set access url
url= "https://resources.gisdata.mn.gov/pub/data/elevation/lidar/county/anoka/laz/3542-19-16.laz"

# Pull necessary data
r = requests.get(url, verify=False)
print('Data pulled.')

# Open requested file as LAZ
with open("r.laz", "wb") as f:
    f.write(r.content)

# Convert LAZ to LAS
arcpy.conversion.ConvertLas(r"r.laz", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1", "SAME_AS_INPUT", '', "NO_COMPRESSION", "REARRANGE_POINTS", None, "ALL_FILES", 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]')

# Create DEM from LAS
arcpy.conversion.LasDatasetToRaster(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\r.las", r"c:\users\eriks\onedrive\documents\arcgis\projects\lab2 - arc1\lab2 - arc1.gdb\r_lasda", "ELEVATION", "BINNING AVERAGE LINEAR", "FLOAT", "CELLSIZE", 10, 1)

# Create TIN from Raster
arcpy.ddd.RasterTin("r_lasda", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\r_Tin", 6.71, 1500000, 1)

# Export DEM and TIN files
aprx = arcpy.mp.ArcGISProject("CURRENT")
DEMlyt = aprx.listLayouts("DEM")[0]
DEMlyt.exportToPDF(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\DEMexport.pdf", resolution = 300)
TINlyt = aprx.listLayouts("TIN")[0]
TINlyt.exportToPDF(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\TINexport.pdf", resolution = 300)

# Found using web inspector
PRISM_request_URL = r'https://prism.oregonstate.edu/fetchData.php'

# Save request params to variable (this is found using Google dev. tools, in network, after clicking on the item, clicking 'payload')
PRISM_params = r'type=all_bil&kind=normals&spatial=4km&elem=ppt&temporal=annual'

# Create final file access path to request data with parameters
final_PRISM_path = PRISM_request_URL + '?' + PRISM_params
print(final_PRISM_path)

# Get data with post request
PRISM_post_request = requests.post(final_PRISM_path)

# Create zipfile from resulting info
ourzipfile = zipfile.ZipFile(io.BytesIO(PRISM_post_request.content), mode='r')

# Create working directory 
os.chdir('C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\Lab2 - Arc1')
working_dir = os.getcwd()
bilsfolder = os.path.join(working_dir, r"bils1")
if not os.path.exists(bilsfolder):
   os.makedirs(bilsfolder)

# Extract data
ourzipfile.extractall(bilsfolder)

# Set workspace
arcpy.env.workspace = working_dir

# Create empty mosaic dataset
arcpy.management.CreateMosaicDataset(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\Lab2 - Arc1.gdb", "Bil_Mosaic", 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]', None, '', "NONE", None)

# Populate empty mosaic with rasters
arcpy.management.AddRastersToMosaicDataset("Bil_Mosaic", "Raster Dataset", r"'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM1.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM2.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM3.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM4.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM5.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM6.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM7.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM8.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM9.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM10.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM11.tif';'C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilraster\PRISM12.tif'", "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", r"C:\Users\eriks\AppData\Local\ESRI\rasterproxies\Bil_Mosaic")

# Add Time Dimension
arcpy.management.CalculateField(r"Bil_Mosaic\Footprint","Time",'!NAME![28:30] + r"15-2015"', "PYTHON3", '', "TEXT")

# Insert Multi-Dimensional Info
arcpy.md.BuildMultidimensionalInfo("Bil_Mosaic", "Name", "Time", None, "NO_DELETE_MULTIDIMENSIONAL_INFO")

# Create Space-time Cube
arcpy.stpm.CreateSpaceTimeCubeMDRasterLayer(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\Lab2 - Arc1.gdb\Bil_Mosaic", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\bilcube.nc", "ZEROS")
