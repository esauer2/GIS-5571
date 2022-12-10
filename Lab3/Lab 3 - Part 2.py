# Import necessary packages
import requests
import csv
import arcpy

# Request url
csv_url= "https://ndawn.ndsu.nodak.edu/table.csv?station=78&station=111&station=98&station=174&station=142&station=138&station=161&station=9&station=10&station=118&station=56&station=11&station=12&station=58&station=13&station=84&station=55&station=7&station=87&station=14&station=15&station=96&station=16&station=137&station=124&station=143&station=17&station=85&station=140&station=134&station=18&station=136&station=65&station=104&station=99&station=19&station=129&station=20&station=101&station=81&station=21&station=97&station=22&station=75&station=2&station=172&station=139&station=23&station=62&station=86&station=24&station=89&station=126&station=93&station=90&station=25&station=83&station=107&station=156&station=77&station=26&station=70&station=127&station=27&station=132&station=28&station=29&station=30&station=31&station=102&station=32&station=119&station=4&station=80&station=33&station=59&station=105&station=82&station=34&station=72&station=135&station=35&station=76&station=120&station=141&station=109&station=36&station=79&station=71&station=37&station=38&station=39&station=130&station=73&station=40&station=41&station=54&station=69&station=113&station=128&station=42&station=43&station=103&station=116&station=88&station=114&station=3&station=163&station=64&station=115&station=67&station=44&station=133&station=106&station=100&station=121&station=45&station=46&station=61&station=66&station=74&station=60&station=125&station=8&station=47&station=122&station=108&station=5&station=152&station=48&station=68&station=49&station=50&station=91&station=117&station=63&station=150&station=51&station=6&station=52&station=92&station=112&station=131&station=123&station=95&station=53&station=57&station=149&station=148&station=110&variable=mdavt&year=2022&ttype=monthly&quick_pick=1_m&begin_date=2021-12&count=12"
tablereq = requests.get(csv_url, verify=True)

# Set destination directory and save CSV
newdir = 'C:\\Users\\eriks\\OneDrive\\Documents\\ArcGIS\\Projects\\data'
with open(newdir + '\\ndawn.csv', 'wb') as ndawn:
    ndawn.write(tablereq.content)

# Set working map/project
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.listMaps("Map1")[0]

# Add Table to Map as XY points
arcpy.management.XYTableToPoint(r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\data\ndawn.csv", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\ndawn_XYTableToPoint1", "Longitude", "Latitude", None, 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')

# IDW Interpolation
arcpy.ddd.Idw("ndawn_XYTableToPoint2", "Avg_Temp", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Idw_ndawn", 0.0144790399999999, 2, "VARIABLE 12", None)

# Ordinary Kriging
arcpy.ddd.Kriging("ndawn_XYTableToPoint2", "Avg_Temp", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\Projects\Default.gdb\Kriging_ndawn", "Spherical # # # #", 0.0144790399999999, "VARIABLE 12", None)

# Global Polynomial Interpolation
arcpy.ga.GlobalPolynomialInterpolation("ndawn_XYTableToPoint2", "Avg_Temp", "GPI_cross", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\data\GPI.tif", 0.0144790399999999, 3, None)

# GPI Cross Validation
arcpy.ga.CrossValidation("GPI_cross", r"C:\Users\eriks\OneDrive\Documents\ArcGIS\Projects\data\GPI_cross.shp")
