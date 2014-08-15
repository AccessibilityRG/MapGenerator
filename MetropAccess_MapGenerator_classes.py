# -*- coding: cp1252 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize, LinearSegmentedColormap
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon, LineString, MultiLineString #Point, MultiPoint, MultiPolygon
from pysal.esda import mapclassify as mc
from pysal.esda.mapclassify import Natural_Breaks as nb
from pysal.esda.mapclassify import Fisher_Jenks as fj
from pysal.esda.mapclassify import Quantiles
from descartes import PolygonPatch
import fiona, sys, time, os
from itertools import chain, imap
import matplotlib.gridspec as gridspec

class MapInstance:
    """Creates and returns Basemap map instance from input shapefiles"""
    def __init__(self, Ykr, Coast, Roads, Metro):
        """Constructor"""
        self.Ykr = Ykr
        self.Coast = Coast
        self.Roads = Roads
        self.Metro = Metro
        self.coords = None

        #Create map-instances
        self.createMapInstances()

    def createMapInstances(self):

        #Import GRID-shapefile
        shp = fiona.open(self.Ykr)

        #Extract map boudaries from GRID
        bds = shp.bounds

        #Close shape
        shp.close()

        #Calculate extent, widthm height
        ll = (bds[0], bds[1])
        ur = (bds[2], bds[3])
        self.coords = list(chain(ll, ur))
        w, h = self.coords[2] - self.coords[0], self.coords[3] - self.coords[1]
        extra = 0.01#0.05 #Set extra space for the geodataframe

        #Create basemap instance
        m = Basemap(
            projection='tmerc',
            lon_0=24.8, #Central longitude
            lat_0=60.25, #Central latitude
            ellps = 'WGS84',
            llcrnrlon=self.coords[0] - extra * w,
            llcrnrlat=self.coords[1] - extra + 0.02 * h,  #Set more empty space under the figure
            urcrnrlon=self.coords[2] + extra * w,
            urcrnrlat=self.coords[3] + extra + 0.01 * h,
            lat_ts=0,
            resolution='l',         #Resolution of boundary database to use. Can be c (crude), l (low), i (intermediate), h (high), f (full) or None.
            suppress_ticks=True)

        #Read GRID-shapefiles in
        m.readshapefile(
            self.Ykr[:-4],
            'Helsinki',
            color='none',
            zorder=2)

        #Read Coastlines
        m.readshapefile(
            self.Coast[:-4],
            'Coast',
            color='none',
            zorder=2)

        #Read Metro-line
        m.readshapefile(
            self.Metro[:-4],
            'Metro',
            color='none',
            zorder=2)

        #Read main-road network
        m.readshapefile(
            self.Roads[:-4],
            'Roads',
            color='none',
            zorder=2)

        self.m = m

        #Set up pandas dataframes containing Shapely objects (Shapely objects and methods: http://toblerity.org/shapely/manual.html)

        #YKR-GRID
        self.grid_map = pd.DataFrame({
            'poly': [Polygon(xy) for xy in m.Helsinki],
            'YKR_ID': [Yid['YKR_ID'] for Yid in m.Helsinki_info]})
        #grid = shapely.prepared.prep(MultiPolygon(list(grid_map['poly'].values))) #Prepared geometries instances have the following methods: contains, contains_properly, covers, and intersects.

        #Coastline
        self.coast_map = pd.DataFrame({
            'poly': [Polygon(xy) for xy in m.Coast]})

        #Metro
        metro_map = pd.DataFrame({
            'line': [LineString(xy) for xy in m.Metro]})
        self.metroLines = MultiLineString(list(metro_map['line'].values)) #Create a MultiLine object from individual lines

        #Main roads
        roads_map = pd.DataFrame({
            'line': [LineString(xy) for xy in m.Roads]})
        self.roads = MultiLineString(list(roads_map['line'].values))

    def getBasemap(self):
        return self.m
    def getYkr(self):
        return self.grid_map
    def getCoast(self):
        return self.coast_map
    def getMetro(self):
        return self.metroLines
    def getRoads(self):
        return self.roads
    def getCoords(self):
        return self.coords

class MapGenerator:
    """Generates the maps with chosen parameters and saves them to disk"""
    def __init__(self, MapInstance , Ykr, Ykr_pop, Coast, Roads, Metro, outputFolder, attribute, classification, coords, numberOfClasses):
        self.B = MapInstance
        self.outputFolder = outputFolder
        self.Y = Ykr
        self.Ypop = Ykr_pop
        self.C = Coast
        self.R = Roads
        self.M = Metro
        self.A = attribute
        self.Cl = classification
        self.Nclasses = numberOfClasses
        self.basename = ""
        self.statistics = self.createStatistics()
        self.coords = coords


    #Convenience functions for working with colour ramps and bars
    def colorbar_index(self,ncolors, cmap, labels=None, **kwargs):
        """
        This is a convenience function to stop you making off-by-one errors
        Takes a standard colourmap, and discretises it,
        then draws a color bar with correctly aligned labels
        """
        cmap = self.my_colormap(cmap,ncolors)
        mappable = cm.ScalarMappable(cmap=cmap)
        mappable.set_array([])
        mappable.set_clim(-0.5, ncolors+0.5)

        colorbar = plt.colorbar(mappable, **kwargs)
        colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
        colorbar.set_ticklabels(range(ncolors))
        
        if labels:
            colorbar.set_ticklabels(labels)
        return colorbar

    def my_colormap(self,cmap, N):

        #Adapted from: http://stackoverflow.com/questions/19199359/modify-discrete-linearsegmentedcolormap
        colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
        colors_rgba = cmap(colors_i)
        indices = np.linspace(0, 1., N+1)

        cdict = {}
        for ki,key in enumerate(('red','green','blue')):
            cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in xrange(N+1) ]

        # "white out" the bands closest to the upper end
        num_end_bands = 1 #Number of classes from the end to white out
        end_band_start_idx = (N - num_end_bands) #Position of the band that will be white (i.e. the last band)

        #"White out" the NoData band
        for end_band_idx in range(end_band_start_idx,
                                     end_band_start_idx + num_end_bands):
            for key in cdict.keys():
                old = cdict[key][end_band_idx]
                cdict[key][end_band_idx] = old[:2] + (1.,)
                old = cdict[key][end_band_idx + 1]
                cdict[key][end_band_idx + 1] = old[:1] + (1.,) + old[2:]
        
        #Return colormap object.
        return LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)

    def reclassify(self, key, value):
        return key[value]

    def createStatistics(self):
        output = self.outputFolder

        #Create outputfile for travel time statistics
        MeanName = "MeanTravelTimes_" + self.A + ".csv"
        meanTimes = os.path.join(output, MeanName)

        if os.path.isfile(meanTimes):
            exists = True
        else:
            exists = False

        self.statistics = open(meanTimes, 'a')

        #Write header if file does not exist already
        if exists == False:
            self.statistics.write("YKR_ID;mean;median;std;min;max\n")

        return self.statistics

    def writeStatistics(self,data):
        self.statistics.write(data)

    def closeStatistics(self):
        self.statistics.close()

    def returnOutPath(self):
        return self.outPath


    ######################
    #GENERATE MAPS
    ######################
    
    def GenerateMap(self, inputFile):

        start = time.time()

        #Create file which hold statistics for each inputFile (containing mean/median travel times, std, min, max etc.)
        self.statistics = self.createStatistics()
        self.basename = os.path.basename(inputFile)[:-4]
        AttributeParameter = self.A
        coords = self.coords

        #Format figure
        plt.clf()
        fig = plt.figure()

        #Picture frame for Map
        gs = gridspec.GridSpec(12, 12)
        ax = plt.subplot(gs[:,:],axisbg='w', frame_on=False)

        try:
            #Read MetropAccess-matka-aikamatriisi data in
            MatrixData = pd.read_csv(inputFile, sep=';')

            #Join data to shapefile (pandas 'merge' function)
            df_map = pd.merge(left=self.Y, right=MatrixData, how='outer', left_on='YKR_ID', right_on='from_id')

            #CLASSIFY MATRIX DATA
            #Replace -1 values
            df_map.replace(to_replace={AttributeParameter: {-1: np.nan}}, inplace=True)

            #Data for histogram
            histData = pd.DataFrame(df_map[df_map[AttributeParameter].notnull()][AttributeParameter].values)

            maxBin = max(df_map[df_map[AttributeParameter].notnull()][AttributeParameter].values) #.AttributeParameter.values)
            NoData = int(maxBin+1)
            NullCount = len(df_map[df_map[AttributeParameter].isnull()])
            NullP = (NullCount/13230.0)*100

            #Fill NoData values with maxBin+1 value
            df_map[AttributeParameter].fillna(NoData, inplace=True)

            #Manual classification
            if not self.Cl in ['Natural Breaks', 'Quantiles', "Fisher's Jenks"]:
                #Create bins for classification based on chosen classification method
                Manual = True

                if "time" in AttributeParameter:
                    measure = "min"
                    measure2 = "minutes" #Another string-form for summary
                    titleMeas = "time"

                    if self.Cl == "10 Minute Equal Intervals":

                        #Calculate the highest class (10 minutes * Number of classes)
                        maxClass = 10*self.Nclasses

                        #Create 'higher than' info for the colorbar
                        maxClassInfo = str(maxClass-10)

                        #Create array of bins from 0 to highest class with increments of 10
                        bins = np.arange(10, maxClass, 10)

                        #Add extra classes for No Data and higher than maxClass values
                        if maxBin < maxClass:
                            bins = list(np.append(bins, [maxClass+1, maxClass+2]))
                        else:
                            bins = list(np.append(bins, [maxBin, maxBin+1]))

                    elif self.Cl == "5 Minute Equal Intervals":

                        #Calculate the highest class (10 minutes * Number of classes)
                        maxClass = 5*self.Nclasses

                        #Create 'higher than' info for the colorbar
                        maxClassInfo = str(maxClass-5)

                        #Create array of bins from 0 to highest class with increments of 5
                        bins = np.arange(5, maxClass, 5)

                        #Add extra classes for No Data and higher than maxClass values
                        if maxBin < maxClass:
                            bins = list(np.append(bins, [maxClass+1, maxClass+2]))
                        else:
                            bins = list(np.append(bins, [maxBin, maxBin+1]))

                elif "dist" in AttributeParameter:

                    measure = "km"
                    measure2 = "kilometers"
                    titleMeas = "distance"

                    if self.Cl == "5 Km Equal Intervals":

                        #Calculate the highest class (5000 meters * Number of classes)
                        maxClass = 5000*self.Nclasses

                        #Create 'higher than' info for the colorbar
                        maxClassInfo = str((maxClass-5000)/1000)

                        #Create array of bins from 0 to highest class with increments of 5000 (meters)
                        bins = np.arange(5000, maxClass, 5000)

                        #Add extra classes for No Data and higher than maxClass values
                        if maxBin < maxClass:
                            bins = list(np.append(bins, [maxClass+1, maxClass+2]))
                        else:
                            bins = list(np.append(bins, [maxBin, maxBin+1]))

                    elif self.Cl == "10 Km Equal Intervals":

                        #Calculate the highest class (5000 meters * Number of classes)
                        maxClass = 10000*self.Nclasses

                        #Create 'higher than' info for the colorbar
                        maxClassInfo = str((maxClass-10000)/1000)

                        #Create array of bins from 0 to highest class with increments of 5000 (meters)
                        bins = np.arange(0, maxClass, 10000)

                        #Add extra classes for No Data and higher than maxClass values
                        if maxBin < maxClass:
                            bins = list(np.append(bins, [maxClass+1, maxClass+2]))
                        else:
                            bins = list(np.append(bins, [maxBin, maxBin+1]))

                #Classify data based on bins
                breaks = mc.User_Defined(df_map[df_map[AttributeParameter].notnull()][AttributeParameter], bins)

            else:
                Manual = False

                if self.Cl == 'Natural Breaks':
                    breaks = nb(df_map[df_map[AttributeParameter].notnull()][AttributeParameter],initial=100, k=self.Nclasses)
                elif self.Cl == 'Quantiles':
                    breaks = Quantiles(df_map[df_map[AttributeParameter].notnull()][AttributeParameter], k=self.Nclasses)
                elif self.Cl == "Fisher's Jenks":
                    breaks = fj(df_map[df_map[AttributeParameter].notnull()][AttributeParameter], k=self.Nclasses)

                bins = list(breaks.bins)

                if "time" in AttributeParameter:
                    measure = "min"
                    measure2 = "minutes" #Another string-form for summary
                    titleMeas = "time"
                    maxClassInfo = str(bins[-2])
                else:
                    measure = "km"
                    measure2 = "kilometers"
                    titleMeas = "distance"
                    maxClassInfo = str(bins[-2]/1000)

                bins.append(maxBin)
                bins.append(maxBin)


            #the notnull method lets us match indices when joining
            jb = pd.DataFrame({'jenks_bins': breaks.yb}, index=df_map[df_map[AttributeParameter].notnull()].index)
            df_map = df_map.join(jb)

            brksBins = bins[:-1]#breaks.bins[:-1] #Do not take into account NoData values

            if measure2 == "kilometers": #Convert meters (in data) to kilometers for legend
                b = [round((x/1000),0) for x in brksBins]
                brksBins = b
                del b

            brksCounts = breaks.counts[:-1] #Do not take into account NoData values

            #Check if brksCounts and brksBins dismatches --> insert 0 values if necessary (to match the counts)
            if len(brksBins) != len(brksCounts):
                dif = len(brksBins)-len(brksCounts)
                brksCounts = np.append(brksCounts,[0 for x in xrange(dif)])
            else:
                dif=0

            #List for measures which will be inserted to class labels
            measureList = [measure for x in xrange(len(brksBins))]

            #Class labels
            jenks_labels = ["%0.0f %s (%0.1f %%)" % (b, msr, (c/13230.0)*100) for b, msr, c in zip(brksBins[:-1],measureList[:-1],brksCounts[:-1])]

            if Manual == True:
                if "dist" in AttributeParameter:
                    jenks_labels.insert(int(maxBin), '>' + maxClassInfo +' km (%0.1f %%)' % ((brksCounts[-1]/13230.0)*100))
                else:
                    jenks_labels.insert(int(maxBin), '>'+ maxClassInfo +' min (%0.1f %%)' % ((brksCounts[-1]/13230.0)*100))

            jenks_labels.insert(NoData, 'NoData (%0.1f %%)' % (NullP))

            #Use modified colormap ('my_colormap') - Choose here the default colormap which is used as a startpoint --> cm.YourColor'sName (eg. cm.Blues) - See available Colormaps: http://matplotlib.org/examples/color/colormaps_reference.html
            cmap = self.my_colormap(cm.RdYlBu, len(bins))

            #Draw grid with grey outlines
            df_map['Grid'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec='#555555', lw=.2, alpha=1., zorder=4)) #RGB color-codes can be found at http://www.rapidtables.com/web/color/RGB_Color.htm
            pc = PatchCollection(df_map['Grid'], match_original=True)

            #-----------------------------
            #Reclassify data to value range 0.0-1.0 (--> colorRange is 0.0-1.0)
            if Manual == True:

                colbins = np.linspace(0.0,1.0, len(bins))
                colbins = colbins-0.001
                colbins[0], colbins[-1] = 0.0001, 1.0

                reclassification = {}
                for index in range(len(bins)):
                    reclassification[index] = colbins[index]

                reclassification['_reclassify'] = self.reclassify

                reclass = []
                dataList = list(df_map['jenks_bins'])

                for value in dataList:
                    reclass.append(self.reclassify(reclassification, value))

                df_map['jenks_binsR'] = reclass
            else:
                norm = Normalize()
                df_map['jenks_binsR'] = norm(df_map['jenks_bins'].values)

            #-----------------------------

            #Impose colour map onto the patch collection
            pc.set_facecolor(cmap(df_map['jenks_binsR'].values))

            #Add colored Grid to map
            ax.add_collection(pc)

            #Add coastline to the map
            self.C['Polys'] = self.C['poly'].map(lambda x: PolygonPatch(x, fc='#606060', ec='#555555', lw=.25, alpha=.88, zorder=4)) #Alpha adjusts transparency, fc='facecolor', ec='edgecolor'
            cpc = PatchCollection(self.C['Polys'], match_original=True)
            ax.add_collection(cpc)

            #Add roads to the map
            for feature in self.R:
                xx,yy=feature.xy
                self.B.plot(xx,yy, linestyle='solid', color='#606060', linewidth=0.7, alpha=.6)

            #Add metro to the map
            for line in self.M: #metroLines is a shapely MultiLineString object consisting of multiple lines (is iterable)
                x,y=line.xy
                self.B.plot(x,y, color='#FF2F2F', linewidth=0.65, alpha=.4)

            #----------------------
            #GENERATE TARGET POINT
            #----------------------
            #Generate YKR_ID from csv name
            ykrID = int(self.basename.split('_')[2])

            #Find index of target YKR_ID
            tIndex = df_map.YKR_ID[df_map.YKR_ID == ykrID].index.tolist()
            trow = df_map[tIndex[0]:tIndex[0]+1]
            targetPolygon = trow.poly
            centroid = targetPolygon.values[0].centroid #Get centroid of the polygon --> Returns shapely polygon point-type object

            self.B.plot(
                centroid.x,centroid.y,
                'go', markersize=3, label="= Destination")

            #-----------------------------
            #LEGEND
            #-----------------------------

            #Draw a map scale
            self.B.drawmapscale(
                coords[0] + 0.47, coords[1] + 0.013, #Etäisyys vasemmalta, etäisyys alhaalta: plussataan koordinaatteihin asteissa
                coords[0], coords[1],
                #10.,
                10.,
                barstyle='fancy', labelstyle='simple',yoffset=200, #yoffset determines the height of the mapscale
                fillcolor1='w', fillcolor2='#909090', fontsize=6,  # black= #000000
                fontcolor='#202020',
                zorder=5)

            #Set up title
            if "PT" in AttributeParameter:
                tMode = "public transportation"
            elif "Car" in AttributeParameter:
                tMode = "car"
            elif "Walk" in AttributeParameter:
                tMode = "walking"

            titleText = "Travel %s to %s (YKR-ID) \n by %s" % (titleMeas,str(ykrID),tMode)
            plt.figtext(.852,.735,
                        titleText, size=9.5)


            #Plot copyright texts
            copyr = "%s MetropAccess project, University of Helsinki, 2014\nLicensed under a Creative Commons Attribution 4.0 International License" % (unichr(0xa9))

            plt.figtext(.24,.078,copyr,fontsize=4.5)

            #----------------
            #Add a colour bar
            #----------------

            #Set arbitary location (and size) for the colorbar
            axColor = plt.axes([.86, .15, .016,.52]) #([DistFromLeft, DistFromBottom, Width, Height])

            cb = self.colorbar_index(ncolors=len(jenks_labels), cmap=cmap, labels=jenks_labels, cax=axColor)#, shrink=0.5)#, orientation="vertical", pad=0.05,aspect=20)#,cax=cbaxes) #This is a function --> see at the beginning of the code. #, cax=cbaxes shrink=0.5,
            cb.ax.tick_params(labelsize=5.5)

            #Inform travel sum of the whole grid (i.e. centrality of the location)
            #Travel time
            if measure2 == "minutes":
                tMean = histData.mean().values[0]
                tMedian=histData.median().values[0]
                tMax = histData.max().values[0]
                tMin = histData.min().values[0]
                tStd=histData.std().values[0]
                travelSummary = "Summary:"
                travelMean = "Mean: %0.0f %s" % (tMean, measure2)
                travelMedian = "Median: %0.0f %s" % (tMedian, measure2)
                travelStd = "Std: %0.0f %s" % (tStd,measure2)
                travelRange = "Range: %0.0f-%0.0f %s" % (tMin,tMax,measure2)

            #Travel distance
            else:
                h = histData.values/1000
                histData = pd.DataFrame(h)
                del h
                tMean = histData.mean().values[0]
                tMedian=histData.median().values[0]
                tMax = histData.max().values[0]
                tMin = histData.min().values[0]
                tStd=histData.std().values[0]
                travelSummary = "Summary:"
                travelMean = "Mean: %0.1f %s" % (tMean, measure2)
                travelMedian = "Median: %0.1f %s" % (tMedian, measure2)
                travelStd = "Std: %0.1f %s" % (tStd,measure2)
                travelRange = "Range: %0.1f-%0.1f %s" % (tMin,tMax,measure2)


            #Write information to a statistics file
            mInfo = "%s;%0.0f;%0.0f;%0.0f;%0.0f;%0.0f\n" % ( str(ykrID), tMean, tMedian, tStd, tMin, tMax)
            self.writeStatistics(mInfo)

            #Helper variables for moving Summary statistic texts
            initialPos = .58 #.15  #.44
            initialXPos = .975 #.20 #.97
            textSize = 5.25
            split = 0.018

            #Plot Travel Summary title
            plt.figtext(initialXPos, initialPos+split*4,
                       travelSummary, ha='left', va='bottom', color='#404040', size=textSize, style='normal',fontweight='bold')

            #Plot Travel Summary mean
            plt.figtext(initialXPos, initialPos+split*3,
                       travelMean,ha='left', va='bottom', size=textSize, color='b')

            #Plot Travel Summary median
            plt.figtext(initialXPos, initialPos+split*2,
                       travelMedian,ha='left', va='bottom', size=textSize, color='r')

            #Plot Travel Summary Standard deviation
            plt.figtext(initialXPos, initialPos+split,
                       travelStd,ha='left', va='bottom', size=textSize)

            #Plot Travel Summary Range
            plt.figtext(initialXPos, initialPos,
                       travelRange,ha='left', va='bottom', size=textSize)

            #Plot Legend symbol
            ax.legend(bbox_to_anchor=(.97, 0.07), fontsize=5.5, frameon=False, numpoints=1) #1.265     bbox_to_anchor=(x,y)  --> arbitary location for legend, more info: http://matplotlib.org/api/legend_api.html

            #--------------------------------------------------------
            #Travel time and population (catchment areas) histograms
            #--------------------------------------------------------

            #New axes for travel time/distance histogram
            ax = plt.axes([.98, .39, .16, .14], axisbg='w') #([DistFromLeft, DistFromBottom, Width, Height])

            #Add histogram
            n, bins, patches = ax.hist(histData.values, 100, normed=False, facecolor='green', alpha=0.75, rwidth=0.5, orientation="vertical")
            ax.axvline(histData.median(), color='r', linestyle='solid', linewidth=1.8)
            ax.axvline(histData.mean(), color='b', linestyle='solid', linewidth=1.0)

            if measure2 == "minutes":
                ax.set_xlabel("t(min)", fontsize=5,labelpad=1.5)
                xupLim = 250 #upper limit for x-axis
            else:
                ax.set_xlabel("km", fontsize=5,labelpad=1.5)
                xupLim = 100 #upper limit for x-axis

            #Set valuelimits for axes
            ax.set_xlim(0,xupLim-30)

            if max(n) < 1000: #ymax will be set to 1000 if count of individual bin is under 1000, else 1500
                yMax = 1000
            else:
                yMax = 1600

            ax.set_ylim(0,yMax)

            #Set histogram title
            plt.figtext(.975, .535,
                        "Travel %s histogram" % titleMeas,ha='left', va='bottom', size=5.7, style='italic')

            #Adjust tick font sizes and set yaxis to right
            ax.tick_params(axis='both', direction="out",labelsize=4.5, pad=1,
                           labelright=True,labelleft=False, top=False, left=False,
                           color='k', length=3, width=.9)

            ax.xaxis.set_ticks(np.arange(0,xupLim-30,30))

            gridlines = ax.get_xgridlines()
            gridlines.extend( ax.get_ygridlines() )

            for line in gridlines:
                line.set_linewidth(.28)
                line.set_linestyle('dotted')

            ax.grid(True)

            #----------------------------------------------------
            #New axes for population diagram

            ax = plt.axes([.98, .17, .16, .14], axisbg='w') #([DistFromLeft, DistFromBottom, Width, Height])

            #Make dataframe from Ykr-population
            pop = pd.read_csv(self.Ypop, sep=';')

            #Use original Matrix without NoData values
            MatrixData.replace(to_replace={AttributeParameter: {-1: np.nan}}, inplace=True)

            #Join population information and time matrix
            join = pd.merge(left=MatrixData, right=pop, how='outer', left_on='from_id', right_on='YKR_ID')

            #Sort data by attribute parameter
            sorted = join.sort(columns=[AttributeParameter])

            #Aggregate data by AttributeParameter
            aggre = pd.DataFrame(sorted.groupby(AttributeParameter).sum().Population)

            #Create attribute from index
            aggre[AttributeParameter] = aggre.index

            #Create cumulative population attribute
            aggre['cumPop'] = aggre['Population'].cumsum()

            #Reset index and determine AttributeParameter as float (matplotlib requires for it to work)
            aggre.reset_index(inplace=True, drop=True)
            aggre[AttributeParameter].astype(float)

            #print aggre[0:10]

            #Create filled curve plot from the cumulative population
            ax.fill_between(aggre.index,aggre['cumPop']/1000,0, interpolate=True, lw=1, facecolor='green', alpha=0.6)

            #Set valuelimits for axes
            ax.set_xlim(0,xupLim-50)
            ax.set_ylim(-10,aggre['cumPop'].max()/1000+50)


            gridlines = ax.get_xgridlines()
            gridlines.extend( ax.get_ygridlines() )

            for line in gridlines:
                line.set_linewidth(.28)
                line.set_linestyle('dotted')

            ax.grid(True)
            ax.tick_params(axis='both', direction="out",labelsize=4.5, pad=1,
                                        labelright=True,labelleft=False, top=False, left=False,
                                        color='k', length=3, width=.9)
            ax.xaxis.set_ticks(np.arange(0,xupLim-30,30))

            if measure2 == "minutes":
                ax.set_xlabel("t(min)", fontsize=5,labelpad=1.5)
                measure3 = 'minutes'
            else:
                measure3 = 'km'
                ax.set_xlabel("km", fontsize=5,labelpad=1.5)

            #Set histogram title
            plt.figtext(.975, .315,
                        "Population (per 1000) reached within (x) %s" % measure3,ha='left', va='bottom', size=5.7, style='italic')

            #-----------------------
            #Save map to disk
            #-----------------------

            fig.set_size_inches(9.22, 6.35) #(Width, Height)

            outputPath = os.path.join(self.outputFolder, self.basename) + AttributeParameter + ".png"

            plt.savefig(outputPath, dpi=300, alpha=True, bbox_inches='tight')
            plt.close() #or plt.close('all') --> closes all figure windows

            end = time.time()
            lasted = int(end-start)
            return lasted

        except Exception as e:
            return e