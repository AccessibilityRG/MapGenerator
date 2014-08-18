#MapGenerator

MetropAccess-MapGenerator is a simple GIS-tool for automatic visualization of travel time/distance maps (i.e. accessibility) for Helsinki Region (Finland) based on public transportation, private car or walking. 
Tool makes it easy to create multiple (hundreds) of accessibility surface maps and it is designed to be used with 
MetropAccess-Travel Time Matrix datasets that are publicly available [here](http://blogs.helsinki.fi/accessibility/data/metropaccess-travel-time-matrix/).


#Dependencies

MetropAccess-MapGenerator is written in Python (tested with version 2.7.6) and has several dependencies. Following Python modules (and their dependencies) are required:

- [wxPython](http://downloads.sourceforge.net/wxpython/wxPython3.0-win64-3.0.0.0-py27.exe)
- [pandas](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas)
- [numpy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
- [shapely](http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely)
- [pysal](http://sourceforge.net/projects/pysal/files/PySAL-1.7.0.win-amd64.exe/download)
- [fiona](http://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona)
- [descartes](https://pypi.python.org/packages/source/d/descartes/descartes-1.0.1.tar.gz#md5=fcacfa88674032891666d833bdab9b6d)
- [matplotlib](https://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.3.1/matplotlib-1.3.1.win-amd64-py2.7.exe)
- [mpl-toolkits.basemap](http://sourceforge.net/projects/matplotlib/files/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.win-amd64-py2.7.exe/download)

#Usage

MetropAccess-MapGenerator has a simple graphical user interface that asks input files (available here) and different parameters for running the tool:

<img src="http://www.helsinki.fi/science/accessibility/maintenance/Kuvia/DialogLarge.PNG" alt="MetropAccess-MapGenerator User Interface" width="200px" height="200px" />


- Travel mode: time/distance by Public transportation, Private Car or Walking

- Classification method: 5 minutes equal intervals, 10 minutes equal intervals, Natural Breaks, Fisher Jenks ...

- N. classes: Determines how many classes will be used to classify the data in visualization.






