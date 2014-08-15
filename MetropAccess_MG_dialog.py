# -*- coding: cp1252 -*-

#---------------------------------------------
# METROPACCESS-MAPGENERATOR
# Accessibility Research Group
# University of Helsinki
# Authored by Henrikki Tenkanen
# Licenced with GNU General Public License v3.
#---------------------------------------------

import os, wx

#Inspired from: http://wiki.wxpython.org/AnotherTutorial, http://www.blog.pythonlibrary.org/2010/05/15/manipulating-pdfs-with-python-and-pypdf/
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
 
    def OnDropFiles(self, x, y, filenames):
        self.window.SetInsertionPointEnd()
 
        for file in filenames:
            self.window.WriteText(file)
 
########################################################################
class DialogPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent) #wx.Panel inherits from wx.Frame (DialogFrame class)

        #Close event - Not necessary when running this in a separate thread
        #self.Bind(wx.EVT_CLOSE, self.OnClose)

        #Get app so it is possible to send input paths to it
        self.app = wx.GetApp()

        #Get frame so it is possible to 'destroy' the frame after user has pushed 'Run MapGenerator' button
        self.frame = parent #Another way to get parent: self.GetParent()

        #Set space for info-texts
        lblSize = (210, -1)

        #Ask Input Folder by creating an browse button (wx.Button --> onBrowseFolder method)
        InputFolder = wx.StaticText(self, label="Input folder (travel time matrices):", size=lblSize)
        self.InputFold = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.InputFold)
        self.InputFold.SetDropTarget(dt)
        InputsBtn = wx.Button(self, label="Browse", name="InputFiles")
        InputsBtn.Bind(wx.EVT_BUTTON, self.onBrowseFolder) #onBrowse sets the filetypes to search for

        #Ask Ykr-grid path by creating an browse button (wx.Button --> onBrowseShape method)
        YkrLbl = wx.StaticText(self, label="MetropAccess-YKR-grid (.shp):", size=lblSize)
        self.YkrPath = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.YkrPath)
        self.YkrPath.SetDropTarget(dt)
        YkrBtn = wx.Button(self, label="Browse", name="YKR-grid")
        YkrBtn.Bind(wx.EVT_BUTTON, self.onBrowseShape)

        #Ask Ykr-population path by creating an browse button (wx.Button --> onBrowseShape method)
        YkrPopLbl = wx.StaticText(self, label="YKR-population (.txt):", size=lblSize)
        self.YkrPopPath = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.YkrPopPath)
        self.YkrPopPath.SetDropTarget(dt)
        YkrPopBtn = wx.Button(self, label="Browse", name="YKR-pop")
        YkrPopBtn.Bind(wx.EVT_BUTTON, self.onBrowseText)

        #Ask Coastline path by creating an browse button (wx.Button --> onBrowseShape method)
        CoastLbl = wx.StaticText(self, label="MetropAccess-Coastline (.shp):", size=lblSize)
        self.CoastPath = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.CoastPath)
        self.CoastPath.SetDropTarget(dt)
        CoastBtn = wx.Button(self, label="Browse", name="Coastline")
        CoastBtn.Bind(wx.EVT_BUTTON, self.onBrowseShape)

        #Ask Road path by creating an browse button (wx.Button --> onBrowseShape method)
        RoadLbl = wx.StaticText(self, label="MetropAccess-Roads (.shp):", size=lblSize)
        self.roadPath = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.roadPath)
        self.roadPath.SetDropTarget(dt)
        roadBtn = wx.Button(self, label="Browse", name="Roads")
        roadBtn.Bind(wx.EVT_BUTTON, self.onBrowseShape)

        #Ask Metro path by creating an browse button (wx.Button --> onBrowseShape method)
        metroLbl = wx.StaticText(self, label="MetropAccess-Metro (.shp):", size=lblSize)
        self.metroPath = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.metroPath)
        self.metroPath.SetDropTarget(dt)
        metroBtn = wx.Button(self, label="Browse", name="Metro")
        metroBtn.Bind(wx.EVT_BUTTON, self.onBrowseShape)

        #Ask Output Folder by creating an browse button (wx.Button --> onBrowseFolder method)
        outputLbl = wx.StaticText(self, label="Output folder:", size=lblSize)
        self.outputPath = wx.TextCtrl(self)
        dt = MyFileDropTarget(self.outputPath)
        self.outputPath.SetDropTarget(dt)
        outputBtn = wx.Button(self, label="Browse", name="Output")
        outputBtn.Bind(wx.EVT_BUTTON, self.onBrowseFolder)

        #Ask Attribute that will be used for generating the maps by creating an ComboBox 'pull-down' menu (wx.Button --> OnSelect method)
        attributeLbl = wx.StaticText(self, label="Travel mode:", size=lblSize)
        attributes = ['Walk_time', 'Walk_dist', 'PT_total_time', 'PT_time', 'PT_dist', 'Car_time', 'Car_dist']
        attributeCB = wx.ComboBox(self, choices=attributes, pos=(50,80), style=wx.CB_READONLY, name="Attribute")
        attributeCB.SetSelection(0)
        attributeCB.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        self.attributeParameter = "Walk_time"

        #Ask classification method that will be used for generating the maps by creating an ComboBox 'pull-down' menu (wx.Button --> OnSelect method)
        classifLbl = wx.StaticText(self, label="Classification method:", size=lblSize)
        classification = ['5 Minute Equal Intervals', '10 Minute Equal Intervals', '5 Km Equal Intervals', '10 Km Equal Intervals', 'Natural Breaks', 'Quantiles', "Fisher's Jenks"]
        classificationCB = wx.ComboBox(self, choices=classification, pos=(50,80), style=wx.CB_READONLY, name="Classification")
        classificationCB.SetSelection(1)
        classificationCB.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        self.classifMethod = "10 Minute Equal Intervals" #Set default value

        #Ask the number of classes that will be used for classification
        wx.StaticText(self, -1, 'N. classes', (397, 266))
        self.Nclasses = wx.SpinCtrl(self, -1, '10', (70, 80), (60, -1), min=2, max=30)

        GenerateBtn = wx.Button(self, label="           Run MapGenerator        ")
        GenerateBtn.Bind(wx.EVT_BUTTON, self.CheckPaths)        #This runs method that checks  valid paths and returns them to the MetropAccess_MapGenerator_main

        #Widgets builds the rows to the dialog
        widgets = [(InputFolder, self.InputFold, InputsBtn),
                   (YkrLbl, self.YkrPath, YkrBtn),
                   (YkrPopLbl, self.YkrPopPath, YkrPopBtn),
                   (CoastLbl, self.CoastPath, CoastBtn),
                   (RoadLbl, self.roadPath, roadBtn),
                   (metroLbl, self.metroPath, metroBtn),
                   (outputLbl, self.outputPath, outputBtn),
                   (attributeLbl, attributeCB),
                    (classifLbl, classificationCB, self.Nclasses)]

 
        #Create rows from the widgets with 'buildRows' method
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        for widget in widgets:
            self.buildRows(widget)

        #Set placement for 'Run MapGenerator' button separately
        self.mainSizer.Add(GenerateBtn, 1, wx.ALL|wx.CENTER, 5)
        self.SetSizer(self.mainSizer)
 
    #----------------------------------------------------------------------
    def buildRows(self, widgets):
        """"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for widget in widgets:
            if isinstance(widget, wx.StaticText):
                sizer.Add(widget, 0, wx.ALL|wx.CENTER, 5)
            elif isinstance(widget, wx.TextCtrl):
                sizer.Add(widget, 1, wx.ALL|wx.EXPAND, 5)
            else:
                sizer.Add(widget, 0, wx.ALL, 5)
        self.mainSizer.Add(sizer, 0, wx.EXPAND)
 
    #----------------------------------------------------------------------

    def OnClose(self, event):
        #Close the app if user wants
        self.frame.Destroy()

    #----------------------------------------------------------------------
    def onBrowseText(self, event):
        """
        Browse for shapes
        """
        widget = event.GetEventObject()
        name = widget.GetName()


        if name == "YKR-pop":
            infomessage = "Choose YKR-population file (.txt)"

        if not "self.currentPath" in locals():
                self.currentPath = ""

        wildcard = ".TXT (*.txt)|*.txt"
        dlg = wx.FileDialog(
            self, message=infomessage,
            defaultDir=self.currentPath,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if name == "YKR-pop":
                self.YkrPopPath.SetValue(path)

            if "self.currentPath" in locals():
                self.currentPath = os.path.dirname(path)
        dlg.Destroy()

    def onBrowseShape(self, event):
        """
        Browse for shapes
        """
        widget = event.GetEventObject()
        name = widget.GetName()

        if name == "YKR-grid":
            infomessage = "Choose YKR-grid (.shp):"
        elif name == "YKR-pop":
            infomessage = "Choose YKR-population file (.txt)"
        elif name == "Coastline":
            infomessage = "Choose Coastline (.shp):"
        elif name == "Roads":
            infomessage = "Choose Roads (.shp):"
        elif name == "Metro":
            infomessage = "Choose Metro (.shp):"

        if not "self.currentPath" in locals():
                self.currentPath = ""
 
        wildcard = ".SHP (*.shp)|*.shp"
        dlg = wx.FileDialog(
            self, message=infomessage,
            defaultDir=self.currentPath, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if name == "YKR-grid":
                self.YkrPath.SetValue(path)
            elif name == "Coastline":
                self.CoastPath.SetValue(path)
            elif name == "Roads":
                self.roadPath.SetValue(path)
            elif name == "Metro":
                self.metroPath.SetValue(path)
            
            if "self.currentPath" in locals():
                self.currentPath = os.path.dirname(path)
        dlg.Destroy()
 
    #----------------------------------------------------------------------

    def onBrowseFolder(self, event):
        """
        Browse for folders
        """
        widget = event.GetEventObject()
        name = widget.GetName()

        if name == "InputFiles":
            infomessage = "Choose a folder containing the data:"
        else:
            infomessage = "Choose an output folder for the maps:"
 
        dlg = wx.DirDialog(
            self, message=infomessage,
            style=wx.DD_DEFAULT_STYLE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if name == "InputFiles":
                self.InputFold.SetValue(path)
            else:
                self.outputPath.SetValue(path)
                
            if "self.currentPath" in locals():
                self.currentPath = os.path.dirname(path)
        dlg.Destroy()
 
    #----------------------------------------------------------------------
    def OnSelect(self, event):
        widget = event.GetEventObject()
        name = widget.GetName()

        if name == "Attribute":
            self.attributeParameter = event.GetString()
        elif name == "Classification":
            self.classifMethod = event.GetString()

    #----------------------------------------------------------------------
    def CheckPaths(self, event):
        """
        Join the two PDFs together and save the result to the desktop
        """
        inputs = self.InputFold.GetValue()
        Ykr = self.YkrPath.GetValue()
        Ykr_pop = self.YkrPopPath.GetValue()
        Coasts = self.CoastPath.GetValue()
        Roads = self.roadPath.GetValue()
        Metro = self.metroPath.GetValue()
        outputF = self.outputPath.GetValue()
        attribute = self.attributeParameter
        classification = self.classifMethod
        NumberOfClasses = self.Nclasses.GetValue()
        
        if not os.path.isdir(inputs):
            msg = "The input folder %s does not exist!" % inputs
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if not os.path.exists(Ykr):
            msg = "The Ykr file %s does not exist!" % Ykr
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(Ykr_pop):
            msg = "The Ykr-population file %s does not exist!" % Ykr_pop
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(Coasts):
            msg = "The Coast file %s does not exist!" % Coasts
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(Roads):
            msg = "The Roads file %s does not exist!" % Roads
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(Metro):
            msg = "The Metro file %s does not exist!" % Metro
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.isdir(outputF):
            msg = "The output folder %s does not exist!" % outputF
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        #Raise error if classification method does not match with chosen attribute
        if "Minute Equal Intervals" in classification and "dist" in attribute:
            msg = "Travel mode '%s' does not match with classification method '%s'.\n\nSelect correct classification method (e.g. '5 Km Equal Intervals')" % (attribute,classification)
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        #Raise error if classification method does not match with chosen attribute
        if "Km Equal Intervals" in classification and "time" in attribute:
            msg = "Travel mode '%s' does not match with classification method '%s'.\n\nSelect correct classification method (e.g. '5 Minute Equal Intervals')" % (attribute,classification)
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


        Paths = inputs,Ykr,Ykr_pop,Coasts,Roads,Metro, outputF, attribute, classification, NumberOfClasses
        self.app.SetValue(Paths)
         
        #Reset dialog values
        self.InputFold.SetValue("")
        self.YkrPath.SetValue("")
        self.YkrPopPath.SetValue("")
        self.CoastPath.SetValue("")
        self.roadPath.SetValue("")
        self.metroPath.SetValue("")
        self.outputPath.SetValue("")

        self.frame.doExit() #Call DialogFrame class to do the exit

#----------------------------------------------------------------------
class DialogFrame(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 
                          "MetropAccess-MapGenerator", size=(630, 430))
        panel = DialogPanel(self)

    def doExit(self):
        self.Destroy()

#----------------------------------------------------------------------
class CustomApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.value = None
    def SetValue(self, tuple):
        self.value = tuple
    def GetValue(self):
        return self.value

#----------------------------------------------------------------------
# Run the program

def mainDialog():
    app = CustomApp()
    frame = DialogFrame()
    frame.Center() #Placement of the frame to the center of computer screen. --> Arbitary placement: frame.SetPosition(wx.Point(300,350))
    frame.Show()
    app.MainLoop()
    parameters = app.GetValue()
    return parameters

if __name__ == "__main__":
    mainDialog()
    #mainInfo()

