cmake_minimum_required(VERSION 3.13.4)

project(DeformityCorrectionOsteotomyPlanner)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/DeformityCorrectionOsteotomyPlanner")
set(EXTENSION_CATEGORY "Planning")
set(EXTENSION_CONTRIBUTORS "Mauro I. Dominguez (M3Dical)")
set(EXTENSION_DESCRIPTION "This is a module to plan deformity correction osteotomies.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/DeformityCorrectionOsteotomyPlanner.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/DeformityCorrectionOsteotomyPlanner/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(DeformityCorrectionOsteotomyPlanner)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
