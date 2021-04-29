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
    self.ui.boneModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onBoneModelChanged)
    self.ui.boneFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.boneSurgicalGuideBasesSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    
    self.ui.normalAsTangentOfCurveCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.originToCurveCheckBox.connect('stateChanged(int)', self.onOriginToCurveCheckBox)
    self.ui.originToCenterCheckBox.connect('stateChanged(int)', self.onOriginToCenterCheckBox)

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

    deformedBoneViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    correctedBoneViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")

    deformedBoneViewNode.SetLinkedControl(True)
    correctedBoneViewNode.SetLinkedControl(True)

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

    self._parameterNode.EndModify(wasModified)

  def onBoneModelChanged(self, caller=None, event=None):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
    self._parameterNode.SetNodeReferenceID("boneModel", self.ui.boneModelSelector.currentNodeID)
    self._parameterNode.EndModify(wasModified)
    
    displayNode = self.ui.boneModelSelector.currentNode().GetDisplayNode()
    deformedBoneViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(deformedBoneViewNode.GetID())

  def onOriginToCurveCheckBox(self):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
    
    if self.ui.originToCurveCheckBox.checked:
      self._parameterNode.SetParameter("originToCurve","True")
      self.ui.originToCenterCheckBox.checked = False
      self._parameterNode.SetParameter("originToCenter","False")
    else:
      self._parameterNode.SetParameter("originToCurve","False")
    
    self._parameterNode.EndModify(wasModified)

  def onOriginToCenterCheckBox(self):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return
    
    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
    
    if self.ui.originToCenterCheckBox.checked:
      self._parameterNode.SetParameter("originToCenter","True")
      self.ui.originToCurveCheckBox.checked = False
      self._parameterNode.SetParameter("originToCurve","False")
    else:
      self._parameterNode.SetParameter("originToCenter","False")
    
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

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    boneCutPlanesFolder = shNode.GetItemByName("Bone Cut Planes")
    boneCutPlanesList = createListFromFolderID(boneCutPlanesFolder)

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


    boneCutPlaneAndCurvePointIndexList = []
    for i in range(len(boneCutPlanesList)):
      origin = [0,0,0]
      boneCutPlanesList[i].GetNthControlPointPosition(0,origin)
      closestCurvePoint = [0,0,0]
      closestCurvePointIndex = boneCurve.GetClosestPointPositionAlongCurveWorld(origin,closestCurvePoint)
      boneCutPlaneAndCurvePointIndexList.append([boneCutPlanesList[i],closestCurvePointIndex])
    
    boneCutPlaneAndCurvePointIndexList.sort(key = lambda item : item[1])

    boneCutPlanesFolder2 = shNode.CreateFolderItem(self.getParentFolderItemID(),"Bone Cut Planes 2")
    
    for i in range(len(boneCutPlaneAndCurvePointIndexList)):
      boneCutPlane = boneCutPlaneAndCurvePointIndexList[i][0]
      boneCutPlaneItemID = shNode.GetItemByDataNode(boneCutPlane)
      shNode.SetItemParent(boneCutPlaneItemID, boneCutPlanesFolder2)

    shNode.RemoveItem(boneCutPlanesFolder)
    shNode.SetItemName(boneCutPlanesFolder2,"Bone Cut Planes")


  def onPlaneModifiedTimer(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    parameterNode.SetNodeReferenceID("lastMovedCutPlane", sourceNode.GetID())
    self.planeModifiedTimer.start()

  def onPlaneModifiedTimerTimeout(self):
    parameterNode = self.getParameterNode()
    boneCurve = parameterNode.GetNodeReference("boneCurve")
    boneModel = parameterNode.GetNodeReference("boneModel")
    planeNode = parameterNode.GetNodeReference("lastMovedCutPlane")
    normalAsTangentOfCurveChecked = parameterNode.GetParameter("normalAsTangentOfCurve") == "True"
    originToCurveChecked = parameterNode.GetParameter("originToCurve") == "True"
    originToCenterChecked = parameterNode.GetParameter("originToCenter") == "True"

    if normalAsTangentOfCurveChecked or originToCurveChecked or originToCenterChecked:
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
      elif originToCenterChecked:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection')
        intersectionModel.CreateDefaultDisplayNodes()
        self.getIntersectionBetweenModelAnd1Plane(boneModel,planeNode,intersectionModel)
        intersectionModelCentroid = self.getCentroid(intersectionModel)
        slicer.mrmlScene.RemoveNode(intersectionModel)
        planeNode.SetOrigin(intersectionModelCentroid)
      if normalAsTangentOfCurveChecked:
        curveZ = np.array([matrix.GetElement(0,2),matrix.GetElement(1,2),matrix.GetElement(2,2)])
        planeNode.SetNormal(curveZ)

      observer = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
      self.boneCutPlaneObserversAndNodeIDList[observerIndex][0] = observer

    self.createAndUpdateDynamicModelerNodes()
    self.transformBonePiecesToCorrectedPosition()

  def createAndUpdateDynamicModelerNodes(self):
    parameterNode = self.getParameterNode()
    #useNonDecimatedBoneModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"
    boneCurve = parameterNode.GetNodeReference("boneCurve")
    nonDecimatedBoneModelNode = parameterNode.GetNodeReference("boneModel")
    #decimatedFibulaModelNode = parameterNode.GetNodeReference("decimatedFibulaModelNode")
     
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    boneCutPlanesFolder = shNode.GetItemByName("Bone Cut Planes")
    boneCutPlanesList = createListFromFolderID(boneCutPlanesFolder)

    boneModelNode = nonDecimatedBoneModelNode

    planeCutsFolder = shNode.GetItemByName("Plane Cuts")
    shNode.RemoveItem(planeCutsFolder)
    cutBonePiecesFolder = shNode.GetItemByName("Cut Bone Pieces")
    shNode.RemoveItem(cutBonePiecesFolder)
    planeCutsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Plane Cuts")
    cutBonePiecesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Cut Bone Pieces")

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    nColors = colorTable.GetNumberOfColors()

    for i in range(0,len(boneCutPlanesList)):
      if i==0:
        modelName = "Bone Segment %d" % 0
        indColor = 0
      elif i!=(len(boneCutPlanesList)-1):
        #Only one execution per bone segment between two planes
        if i%2 == 0:
          continue
        modelName = "Bone Segment %d" % (i//2 +1)
        indColor = (i//2 +1)%(nColors-1)
      else:
        modelName = "Bone Segment %d" % (len(boneCutPlanesList)-1)
        indColor = (i//2 +1)%(nColors-1)

      modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      modelNode.SetName(modelName)
      slicer.mrmlScene.AddNode(modelNode)
      modelNode.CreateDefaultDisplayNodes()
      modelDisplayNode = modelNode.GetDisplayNode()
      correctedBoneViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
      modelDisplayNode.AddViewNodeID(correctedBoneViewNode.GetID())

      #Set color of the model
      colorwithalpha = colorTable.GetTableValue(indColor)
      color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
      modelDisplayNode.SetColor(color)

      dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
      dynamicModelerNode.SetToolName("Plane cut")
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", boneModelNode.GetID())
      if i==0:
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", boneCutPlanesList[0].GetID()) 
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelNode.GetID())
      elif i!=(len(boneCutPlanesList)-1):
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", boneCutPlanesList[i+1].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", boneCutPlanesList[i].GetID())  
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelNode.GetID())
      else:
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", boneCutPlanesList[len(boneCutPlanesList)-1].GetID()) 
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel", modelNode.GetID())
      dynamicModelerNode.SetAttribute("OperationType", "Difference")
        
      dynamicModelerNodeItemID = shNode.GetItemByDataNode(dynamicModelerNode)
      shNode.SetItemParent(dynamicModelerNodeItemID, planeCutsFolder)
      modelNodeItemID = shNode.GetItemByDataNode(modelNode)
      shNode.SetItemParent(modelNodeItemID, cutBonePiecesFolder)
  
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)

  def transformBonePiecesToCorrectedPosition(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    bonePiecesTransformFolder = shNode.GetItemByName("Bone Pieces Transforms")
    shNode.RemoveItem(bonePiecesTransformFolder)
    bonePiecesTransformFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Bone Pieces Transforms")
 
    boneCutPlanesFolder = shNode.GetItemByName("Bone Cut Planes")
    cutBonePiecesFolder = shNode.GetItemByName("Cut Bone Pieces")
    boneCutPlanesList = createListFromFolderID(boneCutPlanesFolder)
    cutBonePiecesList = createListFromFolderID(cutBonePiecesFolder)

    boneCutPlane1ToBoneCutPlane0TransformList = []

    #for i in range(len(boneCutPlanesList)-1,-1,-2):
    for i in range(0,len(boneCutPlanesList),2):
      boneCutPlane0matrix = vtk.vtkMatrix4x4()
      boneCutPlane1matrix = vtk.vtkMatrix4x4()
      boneCutPlanesList[i].GetPlaneToWorldMatrix(boneCutPlane0matrix)
      boneCutPlanesList[i+1].GetPlaneToWorldMatrix(boneCutPlane1matrix)
      boneCutPlane0X = np.array([boneCutPlane0matrix.GetElement(0,0),boneCutPlane0matrix.GetElement(1,0),boneCutPlane0matrix.GetElement(2,0)])
      boneCutPlane0Y = np.array([boneCutPlane0matrix.GetElement(0,1),boneCutPlane0matrix.GetElement(1,1),boneCutPlane0matrix.GetElement(2,1)])
      boneCutPlane0Z = np.array([boneCutPlane0matrix.GetElement(0,2),boneCutPlane0matrix.GetElement(1,2),boneCutPlane0matrix.GetElement(2,2)])
      boneCutPlane0Origin = np.array([boneCutPlane0matrix.GetElement(0,3),boneCutPlane0matrix.GetElement(1,3),boneCutPlane0matrix.GetElement(2,3)])
      boneCutPlane1X = np.array([boneCutPlane1matrix.GetElement(0,0),boneCutPlane1matrix.GetElement(1,0),boneCutPlane1matrix.GetElement(2,0)])
      boneCutPlane1Y = np.array([boneCutPlane1matrix.GetElement(0,1),boneCutPlane1matrix.GetElement(1,1),boneCutPlane1matrix.GetElement(2,1)])
      boneCutPlane1Z = np.array([boneCutPlane1matrix.GetElement(0,2),boneCutPlane1matrix.GetElement(1,2),boneCutPlane1matrix.GetElement(2,2)])
      boneCutPlane1Origin = np.array([boneCutPlane1matrix.GetElement(0,3),boneCutPlane1matrix.GetElement(1,3),boneCutPlane1matrix.GetElement(2,3)])

      epsilon = 0.0001
      if not (vtk.vtkMath.Dot(boneCutPlane1Z, boneCutPlane0Z) >= 1.0 - epsilon):
        angleRadians = vtk.vtkMath.AngleBetweenVectors(boneCutPlane1Z, boneCutPlane0Z)
        rotationAxis = [0,0,0]
        vtk.vtkMath.Cross(boneCutPlane0Z, boneCutPlane1Z, rotationAxis)
        if (vtk.vtkMath.Norm(rotationAxis) < epsilon):
          #New + old normals are facing opposite directions.
          #Find a perpendicular axis to flip around.
          vtk.vtkMath.Perpendiculars(boneCutPlane0Z, rotationAxis, None, 0)
        rotationAxis = rotationAxis/np.linalg.norm(rotationAxis)
        finalTransform = vtk.vtkTransform()
        finalTransform.PostMultiply()
        finalTransform.RotateWXYZ(vtk.vtkMath.DegreesFromRadians(angleRadians), rotationAxis)

        finalTransform.TransformVector(boneCutPlane0X, boneCutPlane1X)
        finalTransform.TransformVector(boneCutPlane0Y, boneCutPlane1Y)

      boneCutPlane0ToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(boneCutPlane0X,boneCutPlane0Y,boneCutPlane0Z)
      boneCutPlane1ToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(boneCutPlane1X,boneCutPlane1Y,boneCutPlane1Z)

      boneCutPlane1ToboneCutPlane0RotationMatrix = self.getAxes1ToAxes2RotationMatrix(boneCutPlane1ToWorldRotationMatrix,boneCutPlane0ToWorldRotationMatrix)

      boneCutPlane1ToboneCutPlane0Transform = vtk.vtkTransform()
      boneCutPlane1ToboneCutPlane0Transform.PostMultiply()
      boneCutPlane1ToboneCutPlane0Transform.Translate(-boneCutPlane1Origin)
      boneCutPlane1ToboneCutPlane0Transform.Concatenate(boneCutPlane1ToboneCutPlane0RotationMatrix)
      boneCutPlane1ToboneCutPlane0Transform.Translate(boneCutPlane0Origin)

      boneCutPlane1ToBoneCutPlane0TransformList.append(boneCutPlane1ToboneCutPlane0Transform)

    for i in range(len(cutBonePiecesList)-1,0,-1):
      connectSegmentToPreviousSegmentTransformNode = slicer.vtkMRMLLinearTransformNode()
      connectSegmentToPreviousSegmentTransformNode.SetName(f"ConnectSegment{i}ToSegment{i-1} Transform")
      slicer.mrmlScene.AddNode(connectSegmentToPreviousSegmentTransformNode)

      connectSegmentToPreviousSegmentTransform = vtk.vtkTransform()
      connectSegmentToPreviousSegmentTransform.PostMultiply()
      for j in range(0,i):
        connectSegmentToPreviousSegmentTransform.Concatenate(boneCutPlane1ToBoneCutPlane0TransformList[i-j-1].GetMatrix())

      connectSegmentToPreviousSegmentTransformNode.SetMatrixTransformToParent(connectSegmentToPreviousSegmentTransform.GetMatrix())

      cutBonePiecesList[i].SetAndObserveTransformNodeID(connectSegmentToPreviousSegmentTransformNode.GetID())

      connectSegmentToPreviousSegmentTransformNodeItemID = shNode.GetItemByDataNode(connectSegmentToPreviousSegmentTransformNode)
      shNode.SetItemParent(connectSegmentToPreviousSegmentTransformNodeItemID, bonePiecesTransformFolder)


  def getIntersectionBetweenModelAnd1Plane(self,modelNode,planeNode,intersectionModel):
    plane = vtk.vtkPlane()
    origin = [0,0,0]
    normal = [0,0,0]
    planeNode.GetOrigin(origin)
    planeNode.GetNormal(normal)
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

  def getAxes1ToWorldRotationMatrix(self,axis1X,axis1Y,axis1Z):
    axes1ToWorldRotationMatrix = vtk.vtkMatrix4x4()
    axes1ToWorldRotationMatrix.DeepCopy((1, 0, 0, 0,
                                         0, 1, 0, 0,
                                         0, 0, 1, 0,
                                         0, 0, 0, 1))
    
    axes1ToWorldRotationMatrix.SetElement(0,0,axis1X[0])
    axes1ToWorldRotationMatrix.SetElement(0,1,axis1X[1])
    axes1ToWorldRotationMatrix.SetElement(0,2,axis1X[2])
    axes1ToWorldRotationMatrix.SetElement(1,0,axis1Y[0])
    axes1ToWorldRotationMatrix.SetElement(1,1,axis1Y[1])
    axes1ToWorldRotationMatrix.SetElement(1,2,axis1Y[2])
    axes1ToWorldRotationMatrix.SetElement(2,0,axis1Z[0])
    axes1ToWorldRotationMatrix.SetElement(2,1,axis1Z[1])
    axes1ToWorldRotationMatrix.SetElement(2,2,axis1Z[2])

    return axes1ToWorldRotationMatrix
  
  def getAxes1ToAxes2RotationMatrix(self,axes1ToWorldRotationMatrix,axes2ToWorldRotationMatrix):
    worldToAxes2RotationMatrix = vtk.vtkMatrix4x4()
    worldToAxes2RotationMatrix.DeepCopy(axes2ToWorldRotationMatrix)
    worldToAxes2RotationMatrix.Invert()
    
    axes1ToAxes2RotationMatrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(worldToAxes2RotationMatrix, axes1ToWorldRotationMatrix, axes1ToAxes2RotationMatrix)

    return axes1ToAxes2RotationMatrix

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

def createListFromFolderID(folderID):
  createdList = []
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  myList = vtk.vtkIdList()
  shNode.GetItemChildren(folderID,myList)
  for i in range(myList.GetNumberOfIds()):
    createdList.append(shNode.GetItemDataNode(myList.GetId(i)))
  return createdList
