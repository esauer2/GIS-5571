# Import necessary packages
import requests
import json
from zipfile import *
import io
import pandas as pd
import os
import arcpy
import shapefile
import csv

# Set access urls
county_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/bdry_counties_in_minnesota/shp_bdry_counties_in_minnesota.zip"
NLCD_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/biota_landcover_nlcd_mn_2019/tif_biota_landcover_nlcd_mn_2019.zip"
DEM_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/elev_30m_digital_elevation_model/fgdb_elev_30m_digital_elevation_model.zip"
stream_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/water_strahler_stream_order/shp_water_strahler_stream_order.zip"
roads_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dot/trans_roads_centerlines/shp_trans_roads_centerlines.zip"

# Pull necessary data and verify
countyreq = requests.get(county_url, verify=True)
NLCDreq = requests.get(NLCD_url, verify=True)
DEMreq = requests.get(DEM_url, verify=True)
streamreq = requests.get(stream_url, verify=True)
roadsreq = requests.get(roads_url, verify=True)

# Create folder to store data
newdir = 'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects'
os.chdir(newdir)
working_dir = os.getcwd()
datafolder = os.path.join(working_dir, r"data")
if not os.path.exists(datafolder):
   os.makedirs(datafolder)

# Store Zipped Data to Working Directory
with open(datafolder + '\\County.zip', 'wb') as czip:
    czip.write(countyreq.content)
    
with open(datafolder + '\\NLCD.zip', 'wb') as NLCDzip:
    NLCDzip.write(NLCDreq.content)
    
with open(datafolder + '\\DEM.zip', 'wb') as DEMzip:
    DEMzip.write(DEMreq.content)
    
with open(datafolder + '\\Streams.zip', 'wb') as streamzip:
    streamzip.write(streamreq.content)
    
with open(datafolder + '\\road.zip', 'wb') as roadzip:
    roadzip.write(roadsreq.content)

# Read the created zipfiles
countyzipfile = ZipFile(r'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\County.zip', mode='r')
NLCDzipfile = ZipFile(r'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\NLCD.zip', mode='r')
DEMzipfile = ZipFile(r'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\DEM.zip', mode='r')
streamzipfile = ZipFile(r'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\Streams.zip', mode='r')
roadzipfile = ZipFile(r'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\road.zip', mode='r')

# Extract the zipfile information
countyzipfile.extractall('C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\County')
DEMzipfile.extractall('C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\DEM')
NLCDzipfile.extractall('C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\NLCD')
streamzipfile.extractall('C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\Streams')
roadzipfile.extractall('C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data\\Roads')

# Set current project and map
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.listMaps("Map")[0]

# Retreive unzipped files and add to map
counties = arcpy.MakeFeatureLayer_management(datafolder + '\\County\\mn_county_boundaries.shp','Counties')
streams = arcpy.MakeFeatureLayer_management(datafolder + '\\Streams\\streams_with_strahler_stream_order.shp','Streams')
roads = arcpy.MakeFeatureLayer_management(datafolder + '\\Roads\\MnDOT_Roadway_Routes_in_Minnesota.shp','Roads')
NLCD = arcpy.MakeRasterLayer_management(datafolder + '\\NLCD\\NLCD_2019_Land_Cover.tif','NLCD')
DEM = m.addLayer(datafolder + '\\DEM\\DigitalElevationModel-30mResolution.lyr')

# Create CSV from Coordinates
# Start Coords: 44.127985, -92.148796
# End Coords: 44.054852, -92.045780
locs = [[44.127985, -92.148796],[44.054852, -92.045780]]
with open(newdir + '\\data\\startendloc.csv', 'w', newline='') as s_output:
    csv_output = csv.writer(s_output)
    csv_output.writerow(['lat', 'long'])
    csv_output.writerows(locs)

# Source
# https://stackoverflow.com/questions/70211907/coordinates-output-to-csv-file-python

# Convert CSV Coords to XY Points
arcpy.management.XYTableToPoint(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\startloc.csv", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\lab2 - arc1.gdb\startloc_XYTableToPoint", "long", "lat", None, 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')
arcpy.management.XYTableToPoint(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\picnicloc.csv", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Lab2 - Arc1\lab2 - arc1.gdb\picnicloc_XYTableToPoint", "long", "lat", None, 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')

# Create Study Area Polygon
arcpy.analysis.Select("Counties", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\StudyArea", "CTY_NAME = 'Winona' Or CTY_NAME = 'Olmsted' Or CTY_NAME = 'Wabasha'")

# Dissolve Boundaries of Study Area
arcpy.gapro.DissolveBoundaries("StudyArea", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\StudyExtent", "SINGLE_PART", None, None, None)

# Extract by Mask for NLCD and DEM layers to Study Extent
nlcd_raster = arcpy.sa.ExtractByMask("NLCD", "StudyExtent", "INSIDE", '524966.6376 4853462.8394 637916.1448 4922619.9426 PROJCS["NAD_1983_UTM_Zone_15N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-93.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'); nlcd_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\NLCD_mask")
dem_raster = arcpy.sa.ExtractByMask("digital_elevation_model_30m", "StudyExtent", "INSIDE", '524966.6376 4853462.8394 637916.1448 4922619.9426 PROJCS["NAD_1983_UTM_Zone_15N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-93.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'); dem_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\DEM_extract")

# Clip Roads and Streams to Study Extent
arcpy.analysis.Clip("Streams", "StudyExtent", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Streams_Clip", None)
arcpy.analysis.Clip("Roads", "StudyExtent", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Roads_Clip", None)

# Remove unnecessary map layers
remove = ["StudyArea","Counties","Streams","Roads","NLCD",]
for layer in remove:
    m.RemoveLayer()

# Convert Road and Stream Vector to Raster with 30 m cell size
arcpy.conversion.FeatureToRaster("Roads_Clip", "ROUTE_NAME", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\raster_road", 30)
arcpy.conversion.FeatureToRaster("Streams_Clip", "KITTLE_NAM", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\raster_stream", 30)

# Percent Rise Slope
DEMslop = arcpy.ddd.Slope("dem_raster", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Slope_DEM", "PERCENT_RISE", 1, "PLANAR", "METER")

# Reclassify
slope_reclass = arcpy.ddd.Reclassify("Slope_DEM", "VALUE", "0 53.347980 10;53.347980 106.695959 9;106.695959 160.043939 8;160.043939 213.391919 7;213.391919 266.739899 6;266.739899 320.087878 5;320.087878 373.435858 4;373.435858 426.783838 3;426.783838 480.131818 2;480.131818 533.479797 1", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_Slop", "DATA")
NLCD_reclass = arcpy.sa.Reclassify("nlcd_raster", "NLCD_Land", "'Open Water' 10;'Developed, Open Space' 2;'Developed, Low Intensity' 2;'Developed, Medium Intensity' 2;'Developed, High Intensity' 2;'Barren Land' 4;'Deciduous Forest' 6;'Evergreen Forest' 6;'Mixed Forest' 6;Shrub/Scrub 10;Herbaceous 6;Hay/Pasture 10;'Cultivated Crops' 10;'Woody Wetlands' 10;'Emergent Herbaceous Wetlands' 10", "DATA"); NLCD_reclass.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_NLCD")
stream_reclass = arcpy.sa.Reclassify("raster_stream", "Value", "1 12.555556 1;12.555556 24.111111 2;24.111111 35.666667 3;35.666667 47.222222 4;47.222222 58.777778 5;58.777778 70.333333 6;70.333333 81.888889 7;81.888889 93.444444 8;93.444444 105 9", "DATA"); stream_reclass.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_stream")
roads_reclass = arcpy.sa.Reclassify("raster_road", "Value", "1 1435.666667 1;1435.666667 2870.333333 2;2870.333333 4305 3;4305 5739.666667 4;5739.666667 7174.333333 5;7174.333333 8609 6;8609 10043.666667 7;10043.666667 11478.333333 8;11478.333333 12913 9", "DATA"); roads_reclass.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_roads")

# New Reclassify
stream_reclass = arcpy.ddd.Reclassify("Reclass_stream", "Value", "1 1435.666667 10;1435.666667 2870.333333 10;2870.333333 4305 10;4305 5739.666667 10;5739.666667 7174.333333 10;7174.333333 8609 10;8609 10043.666667 10;10043.666667 11478.333333 10;11478.333333 12913 10;NODATA 0", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_stream1", "DATA")
slope_reclass = arcpy.ddd.Reclassify("Slope_DEM", "Value", "1 11.400000 1;11.400000 21.800000 2;21.800000 32.200000 3;32.200000 42.600000 4;42.600000 53 5;53 63.400000 6;63.400000 73.800000 7;73.800000 84.200000 8;84.200000 94.600000 9;94.600000 105 10", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_slope", "DATA")
road_reclass = arcpy.ddd.Reclassify("raster_road", "Value", "1 11.400000 1;11.400000 21.800000 1;21.800000 32.200000 1;32.200000 42.600000 1;42.600000 53 1;53 63.400000 1;63.400000 73.800000 1;73.800000 84.200000 1;84.200000 94.600000 1;94.600000 105 1", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_road", "DATA")
NLCD_reclass = arcpy.ddd.Reclassify("nlcd_raster", "NLCD_Land", "'Open Water' 10;'Developed, Open Space' 1;'Developed, Low Intensity' 1;'Developed, Medium Intensity' 1;'Developed, High Intensity' 1;'Barren Land' 3;'Deciduous Forest' 6;'Evergreen Forest' 6;'Mixed Forest' 6;Shrub/Scrub 4;Herbaceous 4;Hay/Pasture 6;'Cultivated Crops' 6;'Woody Wetlands' 8;'Emergent Herbaceous Wetlands' 8", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Reclass_NLCD", "DATA")

# Map Algebra Approach
# Equal Weights Scenario
# Use lowest raster cell size for default cell size
output_raster1 = arcpy.ia.RasterCalculator(' "Reclass_stream1" + "Reclass_road1" + "Reclass_NLCD"+ "Reclass_slope"'); output_raster.save(r"c:\Users\eriks\OneDrive\documents\ArcGIS\Projects\Projects\Default.gdb\overlay")

# Cost Distance
out_distance_raster1 = arcpy.sa.CostDistance("startloc_XYTableToPoint", "overlay", None, r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\direction", None, None, None, None, ''); out_distance_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\CostDis")

# Cost Path
cost_path1 = arcpy.sa.CostPath("picnicloc_XYTableToPoint", "cost_dist", "direction", "EACH_CELL", "OBJECTID", "INPUT_RANGE"); out_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\CostPat_picn2")

# Road Access Scenario
output_raster2 = arcpy.ia.RasterCalculator(' .25*("Reclass_stream1") +  .5*("Reclass_road1") +.25*("Reclass_NLCD") +.25*("Reclass_slope")'); output_raster.save(r"c:\Users\eriks\OneDrive\documents\ArcGIS\Projects\Projects\Default.gdb\overlay_roads")

# Cost Distance
out_distance_raster2 = arcpy.sa.CostDistance("startloc_XYTableToPoint", "overlay_roads", None, r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\roads_backlink", None, None, None, None, ''); out_distance_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\CostDis_roads")

# Cost Path
out_raster3 = arcpy.sa.CostPath("picnicloc_XYTableToPoint", "CostDis_roads", "roads_backlink", "EACH_CELL", "OBJECTID", "INPUT_RANGE"); out_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\CostPath_roads")

# Hiking Scenario - Low Slope Importance and no roads input
output_raster3 = arcpy.ia.RasterCalculator(' .5*("Reclass_stream1") +.5*("Reclass_NLCD") +.25*("Reclass_slope")'); output_raster.save(r"c:\Users\eriks\OneDrive\documents\ArcGIS\Projects\Projects\Default.gdb\overlay_hiking")

# Cost Distance
out_distance_raster3 = arcpy.sa.CostDistance("startloc_XYTableToPoint", "overlay_hiking", None, r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\hiking_backlink", None, None, None, None, ''); out_distance_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\CostDis_hiking")

# Cost Path
out_raster3 = arcpy.sa.CostPath("picnicloc_XYTableToPoint", "CostDis_hiking", "hiking_backlink", "EACH_CELL", "OBJECTID", "INPUT_RANGE"); out_raster.save(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\CostPath_hiking")
