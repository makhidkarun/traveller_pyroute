# Map output

This directory contains the map output functionality for the PyRoute process. It has been broken into several pieces 
for testing, development, and design purposes. It seems a little complicated, but is designed for extensibility and 
ease of processing. 

The core process consists of a base class, a set of drawing classes, a set of layout classes, and a set of final
descriptor classes. 

## Base classes
* _Map.py_ : This is the base class of the drawing process. It mostly consists of empty methods. 
* _MapOutput.py_ : A base class for the output/drawing classes. 

## Drawing classes
These classes are the wrappers around the actual output to file. They rely on the consistent interface defined by
the _MapOutput.py_ class to make changing where output is occurring easier to implement. 
* _GraphicMap.py_ : This is a light wrapper around the Pillow Image library, outputs to a PNG image file.
* _PDFMap.py_     : This is a light wrapper around the ReportLab library, outputs to a PDF file.
* _SubsectorMap.py_ : This is a light wrapper around the Pillow Image Library, outputs to a PNG image file.
* _TestMap.py_    : Exists in the Tests/Outputs directory. This doesn't output anything, but simply accumulates the
     calls to the interface for validation.

## Layout classes
These classes do the layout of data from a source. These, using the drawing class interface, put elements onto the output
for the final product. 
* _SectorMap.py_ : Draws a full sector map with some information in the upper left corner and a key in the upper right.
* _SubsectorMap.py_ : Draws a full subsector map with location at the bottom.

## Support classes
These classes are there as support for the main drawing process.
* _HexGrid.py_ : This class has the logic for drawing a hex grid. It relies on the drawing interface to output the correct lines.
    This is used to draw both the full hex grid and the borders.
* _HexSystem.py_ : This class has the logic for laying out the information for a single system within a hex. There are 
    several variations for different sizes of hexes. Relies entirely on the MapOutput functions for placing elements.
* _Colour.py_ : Holds a type alias for "Colour", which is used in many places.
* _Cursor.py_ : A placeholder for a class to hold an x,y location on the image for placement of an item. 
* _FontLayer.py_ : A utility class to look up font classes for the _GraphicMap.py_ classes across different platforms.

## Final classes
These classes combine, via multiple inheritance, a drawing class (for output) and a layout class (for content), along with
some final tweaks for specific circumstances to produce the final map. These classes define the interface into the drawing
process. 
* _DarkModePDFSectorMap.py_ : Draws a sector map with a black background into a PDF document. Good for viewing on the screen. 
* _LightModePDFSectorMap.py_ : Draws a sector map with a white background into a PDF document. Good for printing.
* _LightModeGraphicSectorMap.py_ : Draws a sector map with a white background into a PNG file. Also good for printing.
