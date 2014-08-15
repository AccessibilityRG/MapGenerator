import os, sys
from threading import Thread
import wx
from wx.lib.pubsub import pub
from MapGenerator import MetropAccess_MapGenerator_classes as MGC
import MetropAccess_MG_dialog as MGD


class RunProgram(wx.Dialog):
    #----------------------------------------------------------------------
    def __init__(self, filecount, Parameters, files):
        """Constructor"""
        wx.Dialog.__init__(self, None, size=(400,180), title="Processing files.. Please wait..")

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.count = 0
        self.filerange = filecount

        self.app = wx.GetApp()

        #Progress bar
        self.progress = wx.Gauge(self, range=filecount, size=(400,35), name="Progress")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.progress, 0, wx.EXPAND)
        self.SetSizer(sizer)

        #Set infotexts
        infotext = "Getting ready.. "
        iPosition=(45,45)
        wx.StaticText(self, label=infotext, pos=iPosition)

        #Copyright info
        copyr = "%s MetropAccess project, University of Helsinki, 2014" % (unichr(0xa9)) #"Licensed under a Creative Commons Attribution 4.0 International License"
        cposition =(165,135)
        font = wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        copyrText = wx.StaticText(self, label=copyr, pos=cposition)
        copyrText.SetFont(font)

        #Create pubsub listeners sending information to the progress bar/dialog
        pub.subscribe(self.updateProgress, "update")
        pub.subscribe(self.updateInfo, "info")
        pub.subscribe(self.AfterRun, "exit")

        #Run MapGenerator in a thread
        self.thread = RunMapGenerator(Parameters, files)

        #----------------------------------------------------------------------
    def updateProgress(self, msg):

        #Update the progress bar
        self.count += 1
        self.progress.SetValue(self.count)

    def updateInfo(self, msg):
        #Info texts
        infotext = "File name:           " + msg[0]
        attribtext = "Travel mode:      " + msg[1]
        processed = "Processing file:   " + msg[2]

        #Info positions
        iPosition = (45,45)
        aPosition = (45,70)
        pPosition = (45,95)

        wx.StaticText(self, label=infotext, pos=iPosition)
        wx.StaticText(self, label=attribtext, pos=aPosition)
        wx.StaticText(self, label=processed, pos=pPosition)

    def AfterRun(self, msg):

        #Show a message dialog that gives information about the location on a disk where maps were saved
        infotext = "Maps were successfully generated to: " + msg
        dlg=wx.MessageDialog(None, infotext, 'OK', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

        #Close the app
        self.Destroy()

    def OnClose(self, event):
        #Close the app if user wants and kill the thread
        self.thread.running = False
        self.Destroy()

class AskInputs:

    def __init__(self):
        self.Parameters = tuple
        self.askInputs()

    #------------------------------------------------------
    def askInputs(self):
        #Ask file-paths and parameters
        self.Parameters = MGD.mainDialog()

        #If user closed the file dialog do not proceed
        if self.Parameters == None:
            sys.exit()

    def getParameters(self):
        return self.Parameters

    def parsePaths(self,inputFolder):
        csvFiles = []
        for root,dirs,files in os.walk(inputFolder):
            for filename in files:
                if "time_to" in filename:
                    if filename.endswith(".txt"):
                        csvFiles.append(os.path.join(root,filename))
        return csvFiles


class RunMapGenerator(Thread):

    def __init__(self, tuple, files):
        Thread.__init__(self)
        self.inputF = tuple[0]
        self.Ykr = tuple[1]
        self.Ykr_pop = tuple[2]
        self.Coast = tuple[3]
        self.Roads = tuple[4]
        self.Metro = tuple[5]
        self.outputF = tuple[6]
        self.travelMode = tuple[7]
        self.classifMethod = tuple[8]
        self.Nclasses = tuple[9]
        self.files = files
        self.daemon = True
        self.running = True

        #Start running the thread
        self.start()


    def run(self):
        while self.running:
            self.mapInstance()
            self.genMaps()

    def mapInstance(self):

        #Create matplotlib basemap instance and pandas dataframes that contains the geometries
        Geometries = MGC.MapInstance(self.Ykr, self.Coast, self.Roads, self.Metro)

        #Get geometries as matplotlib basemap instance (B) and pandas dataframes (Y,C,R,M)
        B = Geometries.getBasemap()
        Y = Geometries.getYkr()
        C = Geometries.getCoast()
        R = Geometries.getRoads()
        M = Geometries.getMetro()
        coords = Geometries.getCoords()

        #Create MapGenerator instance
        self.MG = MGC.MapGenerator(B, Y, self.Ykr_pop, C, R, M, self.outputF, self.travelMode, self.classifMethod, coords, self.Nclasses)

        del Geometries, B, Y, C, R, M, coords
        #------------------------------------------------
    def genMaps(self):
        #Iterate over files and create maps
        i = 1
        filecount = str(len(self.files))

        for iFile in self.files:
            basename = os.path.basename(iFile)[:-4]

            #Set info texts
            prosessedFiles = str(i)+'/' + filecount
            wx.CallAfter(pub.sendMessage, "info", msg=(basename, self.travelMode, prosessedFiles))

            print "Processing file: " + basename

            #Run the MapGenerator
            exception = self.MG.GenerateMap(iFile)
            print exception

            #Set progress bar
            wx.CallAfter(pub.sendMessage, "update", msg="")

            i+=1

        self.MG.closeStatistics()
        wx.CallAfter(pub.sendMessage, "exit", msg=self.outputF)
        self.running = False


def main():
    
    Inputs = AskInputs()
    Parameters = Inputs.getParameters()

    #print Parameters
    #sys.exit()

    files = Inputs.parsePaths(Parameters[0])
    filecount = len(files)

    #Create infobar
    app = wx.App(False)
    Run = RunProgram(filecount, Parameters, files)
    Run.Center()
    Run.ShowModal()
    app.MainLoop()

if __name__ == '__main__':
    main()









