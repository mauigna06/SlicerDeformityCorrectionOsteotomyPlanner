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
    self.ui.boneCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.boneModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.boneFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.boneSurgicalGuideBasesSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    
    self.ui.normalAsTangentOfCurveCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.originToCurveCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)

    self.ui.miterBoxSlotWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.biggerMiterBoxDistanceToBoneSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.boneScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    #self.ui.clearanceFitPrintingToleranceSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)

    # Buttons#
    self.ui.loadBoneModelButton.connect('clicked(bool)',self.onLoadBoneModelButton)
    self.ui.addBoneCurveButton.connect('clicked(bool)',self.onAddBoneCurveButton)
    self.ui.addCutPlaneButton.connect('clicked(bool)',self.onAddCutPlaneButton)
    self.ui.centerBoneCutPlanesButton.connect('clicked(bool)',self.onCenterBoneCutPlanesButton)
    self.ui.createMiterBoxesFromBoneCutPlanesButton.connect('clicked(bool)',self.onCreateMiterBoxesFromBoneCutPlanesButton)
    self.ui.createBoneCylindersFiducialListButton.connect('clicked(bool)',self.onCreateBoneCylindersFiducialListButton)
    self.ui.createCylindersFromFiducialListAndBoneSurgicalGuideBasesButton.connect('clicked(bool)',self.onCreateCylindersFromFiducialListAndBoneSurgicalGuideBasesButton)
    self.ui.makeBooleanOperationsToBoneSurgicalGuideBasesButton.connect('clicked(bool)',self.onMakeBooleanOperationsToBoneSurgicalGuideBasesButton)

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

    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(self.logic.customLayoutId)

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
    self.ui.boneModelSelector.setCurrentNode(self._parameterNode.GetNodeReference("boneModel"))
    self.ui.boneCurveSelector.setCurrentNode(self._parameterNode.GetNodeReference("boneCurve"))
    self.ui.boneFiducialListSelector.setCurrentNode(self._parameterNode.GetNodeReference("boneFiducialList"))
    self.ui.boneSurgicalGuideBasesSelector.setCurrentNode(self._parameterNode.GetNodeReference("boneSurgicalGuideBases"))
    
    if self._parameterNode.GetParameter("miterBoxSlotWidth") != '':
      self.ui.miterBoxSlotWidthSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotWidth")))
    if self._parameterNode.GetParameter("miterBoxSlotLength") != '':
      self.ui.miterBoxSlotLengthSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotLength")))
    if self._parameterNode.GetParameter("miterBoxSlotHeight") != '':
      self.ui.miterBoxSlotHeightSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotHeight")))
    if self._parameterNode.GetParameter("miterBoxSlotWall") != '':
      self.ui.miterBoxSlotWallSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotWall")))
    if self._parameterNode.GetParameter("biggerMiterBoxDistanceToBone") != '':
      self.ui.biggerMiterBoxDistanceToBoneSpinBox.setValue(float(self._parameterNode.GetParameter("biggerMiterBoxDistanceToBone")))
    if self._parameterNode.GetParameter("boneScrewHoleCylinderRadius") != '':
      self.ui.boneScrewHoleCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("boneScrewHoleCylinderRadius")))
    
    self.ui.normalAsTangentOfCurveCheckBox.checked = self._parameterNode.GetParameter("normalAsTangentOfCurve") == "True"
    self.ui.originToCurveCheckBox.checked = self._parameterNode.GetParameter("originToCurve") == "True"

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

    self._parameterNode.SetNodeReferenceID("boneCurve", self.ui.boneCurveSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("boneModel", self.ui.boneModelSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("boneFiducialList", self.ui.boneFiducialListSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("boneSurgicalGuideBases", self.ui.boneSurgicalGuideBasesSelector.currentNodeID)
    
    self._parameterNode.SetParameter("miterBoxSlotWidth", str(self.ui.miterBoxSlotWidthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotLength", str(self.ui.miterBoxSlotLengthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotHeight", str(self.ui.miterBoxSlotHeightSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWall", str(self.ui.miterBoxSlotWallSpinBox.value))
    self._parameterNode.SetParameter("biggerMiterBoxDistanceToBone", str(self.ui.biggerMiterBoxDistanceToBoneSpinBox.value))
    self._parameterNode.SetParameter("boneScrewHoleCylinderRadius", str(self.ui.boneScrewHoleCylinderRadiusSpinBox.value))

    if self.ui.normalAsTangentOfCurveCheckBox.checked:
      self._parameterNode.SetParameter("normalAsTangentOfCurve","True")
    else:
      self._parameterNode.SetParameter("normalAsTangentOfCurve","False")
    if self.ui.originToCurveCheckBox.checked:
      self._parameterNode.SetParameter("originToCurve","True")
    else:
      self._parameterNode.SetParameter("originToCurve","False")

    self._parameterNode.EndModify(wasModified)

  def onAddBoneCurveButton(self):
    self.logic.addBoneCurve()

  def onLoadBoneModelButton(self):
    screwPath = os.path.join(os.path.dirname(slicer.modules.deformitycorrectionosteotomyplanner.path), 'Resources/deformedBone.vtk')
    screwPath = screwPath.replace("\\","/")
    screwModel = slicer.modules.models.logic().AddModel(screwPath)

  def onAddCutPlaneButton(self):
    self.logic.addCutPlane()

  def onCenterBoneCutPlanesButton(self):
    self.logic.centerBoneCutPlanes()

  def onCreateMiterBoxesFromBoneCutPlanesButton(self):
    self.logic.createMiterBoxesFromBoneCutPlanes()

  def onCreateBoneCylindersFiducialListButton(self):
    self.logic.createBoneCylindersFiducialList()

  def onCreateCylindersFromFiducialListAndBoneSurgicalGuideBasesButton(self):
    self.logic.createCylindersFromFiducialListAndBoneSurgicalGuideBases(self)

  def onMakeBooleanOperationsToBoneSurgicalGuideBasesButton(self):
    self.logic.makeBooleanOperationsToBoneSurgicalGuideBases()

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
    self.boneCutPlaneObserversAndNodeIDList = []
    self.planeModifiedTimer = qt.QTimer()
    self.planeModifiedTimer.setInterval(300)
    self.planeModifiedTimer.setSingleShot(True)
    self.planeModifiedTimer.connect('timeout()', self.onPlaneModifiedTimerTimeout)

    customLayout = """
      <layout type="vertical">
      <item>
        <view class="vtkMRMLViewNode" singletontag="1">
          <property name="viewlabel" action="default">1</property>
        </view>
      </item>
      <item>
        <view class="vtkMRMLViewNode" singletontag="2">
        <property name="viewlabel" action="default">2</property>
        </view>
      </item>
      </layout>
    """
    # Built-in layout IDs are all below 100, so you can choose any large random number
    # for your custom layout ID.
    self.customLayoutId=102

    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(self.customLayoutId, customLayout)

    # Add button to layout selector toolbar for this custom layout
    viewToolBar = slicer.util.mainWindow().findChild('QToolBar', 'ViewToolBar')
    layoutMenu = viewToolBar.widgetForAction(viewToolBar.actions()[0]).menu()
    layoutSwitchActionParent = layoutMenu  # use `layoutMenu` to add inside layout list, use `viewToolBar` to add next the standard layout list
    layoutSwitchAction = layoutSwitchActionParent.addAction("DeformityCorrectionOsteotomyPlanner") # add inside layout list
    layoutSwitchAction.setData(self.customLayoutId)
    layoutSwitchAction.setIcon(qt.QIcon(':Icons/Go.png'))
    layoutSwitchAction.setToolTip('Deformed Bone 3D View, Corrected Bone 3D View')

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
  
  def addBoneCurve(self):
    boneCurveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    boneCurveNode.SetName("temp")
    slicer.mrmlScene.AddNode(boneCurveNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(boneCurveNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    boneCurveNodeItemID = shNode.GetItemByDataNode(boneCurveNode)
    shNode.SetItemParent(boneCurveNodeItemID, self.getParentFolderItemID())
    boneCurveNode.SetName(slicer.mrmlScene.GetUniqueNameByString("boneCurve"))

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(boneCurveNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def addCutPlane(self):
    parameterNode = self.getParameterNode()

    planeNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
    planeNode.SetName("temp")
    slicer.mrmlScene.AddNode(planeNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(planeNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    boneCutPlanesFolder = shNode.GetItemByName("Bone Cut Planes")
    if not boneCutPlanesFolder:
      boneCutPlanesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Bone Cut Planes")
    planeNodeItemID = shNode.GetItemByDataNode(planeNode)
    shNode.SetItemParent(planeNodeItemID, boneCutPlanesFolder)
    planeNode.SetName(slicer.mrmlScene.GetUniqueNameByString("boneCutPlane"))

    #display node of the plane
    displayNode = planeNode.GetDisplayNode()
    displayNode.SetGlyphScale(2.5)

    deformedBoneViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(deformedBoneViewNode.GetID())

    #conections
    self.planeNodeObserver = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,self.onPlanePointAdded)

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(planeNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def onPlanePointAdded(self,planeNode,event):
    parameterNode = self.getParameterNode()
    boneCurve = parameterNode.GetNodeReference("boneCurve")

    temporalOrigin = [0,0,0]
    planeNode.GetNthControlPointPosition(0,temporalOrigin)
    
    closestCurvePoint = [0,0,0]
    closestCurvePointIndex = boneCurve.GetClosestPointPositionAlongCurveWorld(temporalOrigin,closestCurvePoint)
    matrix = vtk.vtkMatrix4x4()
    boneCurve.GetCurvePointToWorldTransformAtPointIndex(closestCurvePointIndex,matrix)
    cutPlaneOrigin = np.array([matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)])
    cutPlaneX = np.array([matrix.GetElement(0,0),matrix.GetElement(1,0),matrix.GetElement(2,0)])
    cutPlaneY = np.array([matrix.GetElement(0,1),matrix.GetElement(1,1),matrix.GetElement(2,1)])
    cutPlaneZ = np.array([matrix.GetElement(0,2),matrix.GetElement(1,2),matrix.GetElement(2,2)])
    dx = 2.5#Numbers choosen so the planes are visible enough
    dy = 2.5
    planeNode.RemoveObserver(self.planeNodeObserver)
    planeNode.SetNormal(cutPlaneZ)
    planeNode.SetNthControlPointPositionFromArray(0,cutPlaneOrigin)
    planeNode.SetNthControlPointPositionFromArray(1,cutPlaneOrigin + cutPlaneX*dx)
    planeNode.SetNthControlPointPositionFromArray(2,cutPlaneOrigin + cutPlaneY*dy)

    displayNode = planeNode.GetDisplayNode()
    displayNode.HandlesInteractiveOn()
    for i in range(3):
      planeNode.SetNthControlPointVisibility(i,False)
    observer = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
    self.boneCutPlaneObserversAndNodeIDList.append([observer,planeNode.GetID()])

  def onPlaneModifiedTimer(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    parameterNode.SetNodeReferenceID("lastMovedCutPlane", sourceNode.GetID())
    self.planeModifiedTimer.start()

  def onPlaneModifiedTimerTimeout(self):
    parameterNode = self.getParameterNode()
    boneCurve = parameterNode.GetNodeReference("boneCurve")
    planeNode = parameterNode.GetNodeReference("lastMovedCutPlane")
    normalAsTangentOfCurveChecked = parameterNode.GetParameter("normalAsTangentOfCurve") == "True"
    originToCurveChecked = parameterNode.GetParameter("originToCurve") == "True"

    if normalAsTangentOfCurveChecked or originToCurveChecked:
      for i in range(len(self.boneCutPlaneObserversAndNodeIDList)):
        if self.boneCutPlaneObserversAndNodeIDList[i][1] == planeNode.GetID():
          observerIndex = i
      planeNode.RemoveObserver(self.boneCutPlaneObserversAndNodeIDList[observerIndex][0])

      originOfCutPlane = [0,0,0]
      planeNode.GetNthControlPointPosition(0,originOfCutPlane)
      
      closestCurvePoint = [0,0,0]
      closestCurvePointIndex = boneCurve.GetClosestPointPositionAlongCurveWorld(originOfCutPlane,closestCurvePoint)
      matrix = vtk.vtkMatrix4x4()
      boneCurve.GetCurvePointToWorldTransformAtPointIndex(closestCurvePointIndex,matrix)
      if originToCurveChecked:
        nearestCurvePointToCutPlaneOrigin = np.array([matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)])
        planeNode.SetOrigin(nearestCurvePointToCutPlaneOrigin)
      if normalAsTangentOfCurveChecked:
        curveZ = np.array([matrix.GetElement(0,2),matrix.GetElement(1,2),matrix.GetElement(2,2)])
        planeNode.SetNormal(curveZ)

      observer = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
      self.boneCutPlaneObserversAndNodeIDList[observerIndex][0] = observer

    #self.createAndUpdateDynamicModelerNodes
    #self.transformBonePieces

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

  def centerBoneCutPlanes(self):
    pass

  def onCreateMiterBoxesFromBoneCutPlanes(self):
    pass

  def onCreateBoneCylindersFiducialList(self):
    pass

  def onCreateCylindersFromFiducialListAndBoneSurgicalGuideBases(self):
    pass

  def onMakeBooleanOperationsToBoneSurgicalGuideBases(self):
    pass
  
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
