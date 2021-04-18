p0 = [-4,0,0]
p1 = [-2,0,0]
p2 = [-1,0,0]
a = -0.2928932188
p3 = [a,a,0]
p4 = [0,-1,0]
p5 = [0,-2,0]
p6 = [0,-4,0]
import numpy as np
listOfPoints = np.array([p0,p1,p2,p3,p4,p5,p6])

fiducialNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
fiducialNode.SetName("fiducials")
slicer.mrmlScene.AddNode(fiducialNode)
slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fiducialNode)

points = vtk.vtkPoints()
curvePointsArray = np.array(listOfPoints)
vtkPointsData = vtk.util.numpy_support.numpy_to_vtk(curvePointsArray, deep=1)
points.SetNumberOfPoints(len(curvePointsArray))
points.SetData(vtkPointsData)
fiducialNode.SetControlPointPositionsWorld(points)