#MapGenerator

MetropAccess-MapGenerator is a simple GIS-tool for automatic visualization of travel time/distance maps (i.e. accessibility) for Helsinki Region (Finland) based on public transportation, private car or walking. 
Tool makes it easy to create multiple (hundreds) of accessibility surface maps and it is designed to be used with 
MetropAccess-Travel Time Matrix datasets that are publicly available [here](http://blogs.helsinki.fi/accessibility/data/metropaccess-travel-time-matrix/).


#Dependencies
MetropAccess-MapGenerator is written in Python (tested with version 2.7.6) and has several dependencies. Following Python modules (and their dependencies) need to be properly installed:

- [wxPython](http://downloads.sourceforge.net/wxpython/wxPython3.0-win64-3.0.0.0-py27.exe)
- [pandas](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas)
- [numpy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
- [shapely](http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely)
- [pysal](http://sourceforge.net/projects/pysal/files/PySAL-1.7.0.win-amd64.exe/download)
- [fiona](http://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona)
- [descartes](https://pypi.python.org/packages/source/d/descartes/descartes-1.0.1.tar.gz#md5=fcacfa88674032891666d833bdab9b6d)
- [matplotlib](https://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.3.1/matplotlib-1.3.1.win-amd64-py2.7.exe)
- [mpl-toolkits.basemap](http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.win-amd64-py2.7.exe/download)

#Installation
1. Make sure that all the dependencies are properly installed.

2. [Download](https://github.com/AccessibilityRG/MapGenerator/archive/master.zip) the source code

3. Extract the zip-file

4. Execute the tool by double clicking the ```MetropAccess-MapGenerator_main.py``` file.

#Usage

The tool has a simple graphical user interface that asks input files (available [here](http://blogs.helsinki.fi/accessibility/data/metropaccess-travel-time-matrix/) and
  [here](http://www.helsinki.fi/science/accessibility/data/MetropAccess-MapGenerator/MetropAccess-MapGenerator_VisFiles.zip)) and different parameters for running the tool:

<img src="http://www.helsinki.fi/science/accessibility/maintenance/Kuvia/DialogLarge.PNG" alt="MetropAccess-MapGenerator User Interface" width="448px" height="306px" />

- Input folder (travel time matrices): A folder containing all the [MetropAccess-Travel Time Matrices](http://blogs.helsinki.fi/accessibility/data/metropaccess-travel-time-matrix/) that will be visualized
- Output folder: A destination folder for the generated maps
- MetropAccess-YKR-grid (.shp) (required): A grid that will used for visualizing the travel times/distances in ESRI Shapefile format
- MetropAccess-Coastline (.shp) (optional): A shapefile for visualizing coastline of Helsinki Region
- MetropAccess-Roads (.shp) (optional): A shapefile for visualizing major roads of Helsinki Region
- MetropAccess-Metro (.shp) (optional): A shapefile for visualizing metro lines of Helsinki Region
- Population info (.txt) (optional): A text file [(see example)](http://www.helsinki.fi/science/accessibility/maintenance/Kuvia/PopulationFileExample.PNG) containing population information for each YKR-grid cell (--> need to have following attributes separated with semicolon: YKR-ID; Population)
- Travel mode: time/distance by Public transportation, Private Car or Walking
- Classification method: 5 minutes equal intervals, 10 minutes equal intervals, Natural Breaks, Quantiles, Fisher Jenks
- N. classes: Determines how many classes will be used to classify the data in visualization.

#Examples
The tool generates following kind of accessibility maps (measures: travel time/distance) with additional diagrams (optional) about population and travel times/distances:
<img src="http://www.helsinki.fi/science/accessibility/maintenance/Kuvia/Pks_PublicTransport_Dance_with_Accessibility.png" alt="MetropAccess-MapGenerator results animation" width="448px" height="306px" />




