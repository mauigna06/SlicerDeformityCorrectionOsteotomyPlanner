import os
import unittest
import logging
import vtk, qt, ctk, slicer
import numpy as np
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# DeformityCorrectionOsteotomyPlanner
#

class DeformityCorrectionOsteotomyPlanner(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "DeformityCorrectionOsteotomyPlanner"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Planning"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Mauro I. Dominguez (M3Dical)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is a module to to plan deformity correction osteotomies.
See more information in <a href="https://github.com/mauigna06/SlicerDeformityCorrectionOsteotomyPlanner">module link</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Mauro I. Dominguez (M3Dical)
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # DeformityCorrectionOsteotomyPlanner1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='DeformityCorrectionOsteotomyPlanner',
    sampleName='DeformityCorrectionOsteotomyPlanner1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'DeformityCorrectionOsteotomyPlanner1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='DeformityCorrectionOsteotomyPlanner1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='DeformityCorrectionOsteotomyPlanner1'
  )

  # DeformityCorrectionOsteotomyPlanner2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='DeformityCorrectionOsteotomyPlanner',
    sampleName='DeformityCorrectionOsteotomyPlanner2',
    thumbnailFileName=os.path.join(iconsPath, 'DeformityCorrectionOsteotomyPlanner2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='DeformityCorrectionOsteotomyPlanner2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='DeformityCorrectionOsteotomyPlanner2'
  )

#
# DeformityCorrectionOsteotomyPlannerWidget
#

class DeformityCorrectionOsteotomyPlannerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/DeformityCorrectionOsteotomyPlanner.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = DeformityCorrectionOsteotomyPlannerLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.boneLinearCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.boneModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.numberOfIterationsOfCreateBoneCenterlineSpinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
    
    # Buttons#
    self.ui.addBoneLinearCurveButton.connect('clicked(bool)',self.onAddBoneLinearCurveButton)
    self.ui.createBoneCenterlineButton.connect('clicked(bool)',self.onCreateBoneCenterlineButton)
    self.ui.loadBoneModelButton.connect('clicked(bool)',self.onLoadBoneModelButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.boneLinearCurveSelector.setCurrentNode(self._parameterNode.GetNodeReference("boneLinearCurve"))
    self.ui.boneModelSelector.setCurrentNode(self._parameterNode.GetNodeReference("boneModel"))
    if self._parameterNode.GetParameter("numberOfIterationsOfCreateBoneCenterline") != '':
      self.ui.numberOfIterationsOfCreateBoneCenterlineSpinBox.value = int(self._parameterNode.GetParameter("numberOfIterationsOfCreateBoneCenterline"))

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("boneLinearCurve", self.ui.boneLinearCurveSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("boneModel", self.ui.boneModelSelector.currentNodeID)
    self._parameterNode.SetParameter("numberOfIterationsOfCreateBoneCenterline", str(self.ui.numberOfIterationsOfCreateBoneCenterlineSpinBox.value))
    
    self._parameterNode.EndModify(wasModified)

  def onAddBoneLinearCurveButton(self):
    self.logic.addBoneLinearCurve()

  def onCreateBoneCenterlineButton(self):
    self.logic.createBoneCenterline()

  def onLoadBoneModelButton(self):
    screwPath = os.path.join(os.path.dirname(slicer.modules.deformitycorrectionosteotomyplanner.path), 'Resources/deformedBone.vtk')
    screwPath = screwPath.replace("\\","/")
    screwModel = slicer.modules.models.logic().AddModel(screwPath)
#
# DeformityCorrectionOsteotomyPlannerLogic
#

class DeformityCorrectionOsteotomyPlannerLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def getParentFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sceneItemID = shNode.GetSceneItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("DeformityCorrectionOsteotomyPlanner")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(sceneItemID,"DeformityCorrectionOsteotomyPlanner")
  
  def addBoneLinearCurve(self):
    linearCurveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    linearCurveNode.SetName("temp")
    slicer.mrmlScene.AddNode(linearCurveNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(linearCurveNode)
    linearCurveNode.SetCurveTypeToLinear()
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    linearCurveNodeItemID = shNode.GetItemByDataNode(linearCurveNode)
    shNode.SetItemParent(linearCurveNodeItemID, self.getParentFolderItemID())
    linearCurveNode.SetName(slicer.mrmlScene.GetUniqueNameByString("boneLinearCurve"))

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(linearCurveNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def createBoneCenterline(self):
    import time
    startTime = time.time()
    logging.info('Processing started')

    parameterNode = self.getParameterNode()
    boneLinearCurve = parameterNode.GetNodeReference("boneLinearCurve")
    boneModel = parameterNode.GetNodeReference("boneModel")
    boneCenterline = parameterNode.GetNodeReference("boneCenterline")
    numberOfIterationsOfCreateBoneCenterline = int(parameterNode.GetParameter("numberOfIterationsOfCreateBoneCenterline"))
    
    slicer.mrmlScene.RemoveNode(boneCenterline)
    boneCenterline = self.createStartingCenterline()

    resampleNumberOfPoints = [8,16,32,64,128]

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")

    for i in range(numberOfIterationsOfCreateBoneCenterline):
      sampleDist = boneCenterline.GetCurveLengthWorld()/(resampleNumberOfPoints[i] - 1)
      boneCenterline.ResampleCurveWorld(sampleDist)

      arrayOfPoints = slicer.util.arrayFromMarkupsControlPoints(boneCenterline)

      for j in range(2):

        listOfNewPoints = []

        lineStartPos = arrayOfPoints[0]
        lineEndPos = arrayOfPoints[1]
        origin = lineStartPos
        zDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % 0)
        intersectionModel.CreateDefaultDisplayNodes()
        self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(boneModel, zDirection, origin, intersectionModel)
        intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
        shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)

        listOfNewPoints.append(self.getCentroid(intersectionModel))

        for i in range(1,len(arrayOfPoints)-1):
          lineStartPos = arrayOfPoints[i-1]
          lineEndPos = arrayOfPoints[i+1]
          origin = arrayOfPoints[i]
          zDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

          intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % i)
          intersectionModel.CreateDefaultDisplayNodes()
          self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(boneModel, zDirection, origin, intersectionModel)
          intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
          shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)

          listOfNewPoints.append(self.getCentroid(intersectionModel))
        
        lineStartPos = arrayOfPoints[-2]
        lineEndPos = arrayOfPoints[-1]
        origin = lineEndPos
        zDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % (boneLinearCurve.GetNumberOfControlPoints()-1))
        intersectionModel.CreateDefaultDisplayNodes()
        self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(boneModel, zDirection, origin, intersectionModel)
        intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
        shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)

        listOfNewPoints.append(self.getCentroid(intersectionModel))

        arrayOfPoints = np.array(listOfNewPoints)

      slicer.util.updateMarkupsControlPointsFromArray(boneCenterline, arrayOfPoints)

    shNode.RemoveItem(intersectionsFolder)

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))


  def createStartingCenterline(self):
    parameterNode = self.getParameterNode()
    boneModel = parameterNode.GetNodeReference("boneModel")
    boneLinearCurve = parameterNode.GetNodeReference("boneLinearCurve")

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")

    boneCenterline = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    boneCenterline.SetName("temp")
    slicer.mrmlScene.AddNode(boneCenterline)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(boneCenterline)
    boneCenterline.SetCurveTypeToLinear()
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    boneCenterlineItemID = shNode.GetItemByDataNode(boneCenterline)
    shNode.SetItemParent(boneCenterlineItemID, self.getParentFolderItemID())
    boneCenterline.SetName(slicer.mrmlScene.GetUniqueNameByString("boneCenterline"))
    boneCenterline = parameterNode.SetNodeReferenceID("boneCenterline",boneCenterline.GetID())

    listOfPoints = []

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    boneLinearCurve.GetNthControlPointPositionWorld(0, lineStartPos)
    boneLinearCurve.GetNthControlPointPositionWorld(1, lineEndPos)
    origin = lineStartPos
    zDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % 0)
    intersectionModel.CreateDefaultDisplayNodes()
    self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(boneModel, zDirection, origin, intersectionModel)
    intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
    shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)

    listOfPoints.append(self.getCentroid(intersectionModel))

    for i in range(1,boneLinearCurve.GetNumberOfControlPoints()-1):
      boneLinearCurve.GetNthControlPointPositionWorld(i-1, lineStartPos)
      boneLinearCurve.GetNthControlPointPositionWorld(i+1, lineEndPos)
      boneLinearCurve.GetNthControlPointPositionWorld(i, origin)
      zDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

      intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % i)
      intersectionModel.CreateDefaultDisplayNodes()
      self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(boneModel, zDirection, origin, intersectionModel)
      intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
      shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)

      listOfPoints.append(self.getCentroid(intersectionModel))
    
    boneLinearCurve.GetNthControlPointPositionWorld(boneLinearCurve.GetNumberOfControlPoints()-2, lineStartPos)
    boneLinearCurve.GetNthControlPointPositionWorld(boneLinearCurve.GetNumberOfControlPoints()-1, lineEndPos)
    origin = lineEndPos
    zDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % (boneLinearCurve.GetNumberOfControlPoints()-1))
    intersectionModel.CreateDefaultDisplayNodes()
    self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(boneModel, zDirection, origin, intersectionModel)
    intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
    shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)

    listOfPoints.append(self.getCentroid(intersectionModel))

    shNode.RemoveItem(intersectionsFolder)

    points = vtk.vtkPoints()
    curvePointsArray = np.array(listOfPoints)
    vtkPointsData = vtk.util.numpy_support.numpy_to_vtk(curvePointsArray, deep=1)
    points.SetNumberOfPoints(len(curvePointsArray))
    points.SetData(vtkPointsData)
    boneCenterline.SetControlPointPositionsWorld(points)

    return boneCenterline

  def getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(self,modelNode,normal,origin,intersectionModel):
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)

    cutter = vtk.vtkCutter()
    cutter.SetInputData(modelNode.GetPolyData())
    cutter.SetCutFunction(plane)
    cutter.Update()

    intersectionModel.SetAndObservePolyData(cutter.GetOutput())
  
  def getCentroid(self,model):
    pd = model.GetPolyData().GetPoints().GetData()
    from vtk.util.numpy_support import vtk_to_numpy
    return np.average(vtk_to_numpy(pd), axis=0)
  
  def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Above' if invert else 'Below'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    slicer.mrmlScene.RemoveNode(cliNode)

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# DeformityCorrectionOsteotomyPlannerTest
#

class DeformityCorrectionOsteotomyPlannerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_DeformityCorrectionOsteotomyPlanner1()

  def test_DeformityCorrectionOsteotomyPlanner1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('DeformityCorrectionOsteotomyPlanner1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = DeformityCorrectionOsteotomyPlannerLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
