################################################################################
#        Global Runoff Data Centre (GRDC) River Discharge Point Data and       #
#        University of New Hampshire-GRDC Composite Global Runoff Fields       #
#               at 1/2 and 1 degree spatial resolutions (1986-1995)            # 
################################################################################
File Description
----------------
The two river discharge files are called "grdc_river_disch1986-1995.dat" and 
"grdc_stations1986-1995.dat" and contain the monthly river discharge for 
appropriate GRDC gauging stations and ancillary information on the stations 
(e.g. location, river basin name, etc.), respectively. The various files of the 
UNH-GRDC composite runoff fields are named using the following naming 
convention:

comp_runoff_xx_19yymm.asc: Gridded ASCII map showing the mean monthly composite 
runoff fields in mm/month, where:
  xx is the spatial resolution ("1d" for 1-degree and "hd" for half-degree in 
     latitude and longitude).
  yy is the year from 1986 to 1995. 
  mm is the month from 01 to 12.

comp_runoff_hd_19yymm.dif: ASCII table "difference" files (with an extension of 
  ".dif") that hold all the points from each runoff map that did not match the 
  ISLSCP II land/water mask, and were removed. These files only exist for each "hd" 
  data file.

wbm_runoff_xx_19yymm.asc: Gridded ASCII map showing the mean monthly water 
  balance model runoff in mm/month.

wbm_runoff_hd_19yymm.dif: Same as "comp_runoff_hd_19yymm.dif" but for the water 
  balance mode runoff.

runoff_hd_changemap.asc: Gridded ASCII map showing the differences between the 
  ISLSCP II land/water mask and the original data set: All points removed ("-1")
  all points left unchanged ("0"), and all points added ("1"). There is only one 
  file for the original "hd" data.

runoff_correction_xx.asc: Gridded ASCII map showing the long-term mean annual 
  correction coefficient based on 660 climatological discharge gauges.

runoff_correction_xx_19yy.asc: Gridded ASCII map showing the annual correction 
  coefficients based on the applicable discharge monitoring stations out of the 
  390 selected gauges.

runoff_subbasins_xx.asc: Gridded ASCII map showing the subbasins of the 390 
  discharge gauging stations with observations in the 1986-95 period.

runoff_subbasins_xx_19yy.asc: Gridded ASCII map showing the subbasins of the 
  time series discharge gauging stations which operated in year 19yy out of the 
  390 selected stations

################################################################################
ASCII File Format
-----------------
All of the files in the ISLSCP Initiative II data collection are in the ASCII, 
text format. The file format consists of numerical fields of varying length, 
which are delimited by a single space and arranged in columns and rows. The 
half-degree files (with "hd" in the file name) are at a resolution of 0.5 x
0.5 degrees and thus have 720 columns by 360 rows. The 1-degree files (with 
"1d" in the file name) are at a resolution of 1.0 x 1.0 degrees and thus have
360 columns by 180 rows (note: the "1d" files were created by the ISLSCP II
Staff through averaging). All values in these files are written as real numbers.
Missing data cells are given the value of -99 over water, and -88 over land 
(mainly Greenland and Antarctica).

The grdc_river_disch1986-1995.dat and grdc_stations1986-1995.dat files are text 
files where each column of data is separated by a "tab" character (i.e. tab-
delimited file). These files can be easily imported into standard spreadsheet 
programs.

The ASCII comp_runoff and wbm_runoff map files (with the extension of ".asc") 
have all had the ISLSCP II land/water mask applied to them. All points removed 
from the original half-degree files are stored in "differences" files (with the 
extension ".dif"). These ASCII files contain the Latitude and Longitude location 
of the cell-center of each removed point, and the data value at that point. 
There is one ".dif" file for each half-degree ASCII map file.

The "change map" file shows the results of applying the land/water mask to the 
comp_runoff and wbm_runoff map files, as a viewable ASCII map: all points added 
("1"), all points unchanged ("0"), and all points removed ("-1"). There is only 
a file for the half-degree data, as the 1-degree data was created through 
averaging.

The "runoff_correction" and "runoff_subbasin" ASCII map files have not been masked, 
thus there are no ".dif" files and no change map associated with them.

The map files are all gridded to a common equal-angle lat/long grid, where the 
coordinates of the upper left corner of the files are located at 180 degrees W, 
90 degrees N and the lower right corner coordinates are located at 180 degrees E,
90 degrees S. Data in the files are ordered from North to South and from West
to East beginning at 180 degrees West and 90 degrees North. 

WARNING: The 1x1 degree map products are recommended for browse use only. These 
data files are averaged from the original 0.5 x 0.5 degree pixels. Thus the data 
values at specific pixels are not exact. Use this data with caution and always 
refer to the original half-degree data files for specific information.

##############################################################################
River Discharge File Contents:
------------------------------
GRDC-ID      Identification number for each discharge gauging station after
             GRDC.
Date         Year and month of discharge measurement.
Discharge    Monthly river discharge measured at a particular station, in cubic
             meters per second.

Discharge Station Attribute File Contents:
------------------------------------------
ID                Station number
GRDC-ID           Identification number for each discharge gauging station 
                  after GRDC.
River Name        Name of river where station is located
Station Name      Name of the discharge station
Country           Two letter country code
Area              Reported catchment area in square kilometers.
StartMonth        Beginning month of observation records.
Start Year        Beginning year of observation record.
End Month         Last month of observation records.
End Year          Last year of observation records
Time Series       Time Series Type (M = Monthly; D = Daily)
Percent Record    Percent of missing values in observation records.
GRDC663           Station used as climatological station ? (0 = No;1 = Yes)
LonDD             Latitude for the center of a cell in decimal degrees. South
                  latitudes are negative.
LatDD             Longitude for the center of a cell in decimal degrees. West
                  longitudes are negative.

###############################################################################
