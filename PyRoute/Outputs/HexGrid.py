
from PyRoute.Allies.Borders import Borders
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.Colour import Colour
from PyRoute.Outputs.Map import MapOutput
from PyRoute.Position.Hex import Hex


class HexGrid(object):
    """
    HexGrid contains the core processing to draw a grid of hexes.
    There are a number of ways to draw a grid of hexes: Are they stacked vertically or horizontally? Is the first
    column of hexes above or below the second column? Or for the horizontal stack, is the first row to the left or right
    of the second row?

    This draws only a vertical stack of hexes where the first column is above the second. This is the standard way all
    hex grids for Traveller are drawn.

    This will draw a grid of hexes of any size from 1 x 1 to whatever fits on the graphic page.

    This draws the grid by drawing three lines:
     rline  \
             \
              ___ hline
             /
     lline  /


    These are drawn in this pattern, skipping the rline at the top of the column, and the hline at the end of the row.

    Three sets of values determine what is drawn:
    X/Y position of where the hexes are to start
    rows/cols : number of rows and columns of hexes to draw
    size x/y determine the width and height of each hex.
    """
    def __init__(self, doc: MapOutput, start: Cursor, size: Cursor, rows: int, cols: int):
        self.hex_grid_colour: Colour = 'gray'
        self.doc: MapOutput = doc

        self.start = start  # 15,43
        self.size = size   # 6, 9
        self.x_count = rows + 1  # 33
        self.y_count = cols + 1  # 41
        self.borders: Borders = None
        self.sector_dx: int = 0
        self.sector_dy: int = 0

    def hex_grid(self, draw, width: int, colour: Colour):
        hline = HLine(self.doc, self, width, colour)
        lline = LLine(self.doc, self, width, colour)
        rline = RLine(self.doc, self, width, colour)

        for x in range(self.x_count):
            hline.x_plus()
            hline.restart_y(x)
            lline.restart_y(x)
            rline.restart_y(x)

            for y in range(self.y_count):
                hline.y_plus()
                lline.y_plus()
                rline.y_plus()

                draw(x, y, hline, lline, rline)

            lline.x_plus()
            rline.x_plus()

    def draw_all(self, x, y, hline, lline, rline):
        if x < self.x_count - 1:
            hline.draw()
        if self.y_count % 2 == 0 and y == self.y_count - 1:
            pass
        else:
            lline.draw()
        if y > 0:
            rline.draw()

    def set_borders(self, borders: Borders, sector_dx: int, sector_dy: int):
        self.borders = borders
        self.sector_dx = sector_dx
        self.sector_dy = sector_dy

    def draw_borders(self, x: int, y: int, hline, lline, rline) -> None:
        offset = Hex.dy_offset(y, (self.sector_dy // 40))
        q, r = Hex.hex_to_axial(x + (self.sector_dx), offset - 1)

        if self.borders.borders.get((q, r), False):
            border_colours = self.borders.borders[(q, r)]
            if border_colours[0] and x < self.x_count - 1:
                hline.draw_colour(border_colours[0])
            if border_colours[1] and y > 0:
                rline.draw_colour(border_colours[1])
            if border_colours[2]:
                lline.draw_colour(border_colours[2])


class LineDraw (object):
    def __init__(self, doc: MapOutput, grid: HexGrid, width: int, colour: Colour):
        self.doc = doc
        self.width = width
        self.colour = colour
        self.start = Cursor(0, 0)
        self.end = Cursor(0, 0)
        self._start_cursor(grid)

    def _start_cursor(self, grid: HexGrid):
        raise NotImplementedError("Base Class")

    def restart_y(self, x: int):
        raise NotImplementedError("Base Class")

    def y_plus(self):
        self.start.y_plus()
        self.end.y_plus()

    def x_plus(self):
        self.start.x_plus()
        self.end.x_plus()

    def draw(self) -> None:
        self.doc.add_line(self.start, self.end, colour=self.colour, stroke='solid', width=self.width)

    def draw_colour(self, colour: Colour) -> None:
        self.doc.add_line(self.start, self.end, colour=colour, stroke='solid', width=self.width)


class HLine(LineDraw):
    def __init__(self, doc: MapOutput, grid: HexGrid, width: int, colour: Colour):
        super(HLine, self).__init__(doc, grid, width, colour)

    def _start_cursor(self, grid: HexGrid):
        self.start.x = grid.start.x - (grid.size.x * 2)
        self.start.y = grid.start.y - grid.size.y
        self.start.dx = grid.size.x * 3
        self.start.dy = grid.size.y * 2

        self.end.x = grid.start.x
        self.end.y = grid.start.y - grid.size.y
        self.end.dx = grid.size.x * 3
        self.end.dy = grid.size.y * 2

        self.odd_start_y = grid.start.y - grid.size.y
        self.even_start_y = grid.start.y - 2 * grid.size.y

    def restart_y(self, x: int):
        if x & 1:
            self.start.y = self.odd_start_y
            self.end.y = self.odd_start_y
        else:
            self.start.y = self.even_start_y
            self.end.y = self.even_start_y


class LLine(LineDraw):
    def __init__(self, doc: MapOutput, grid: HexGrid, width: int, colour: Colour):
        super(LLine, self).__init__(doc, grid, width, colour)

    def _start_cursor(self, grid: HexGrid):
        self.start.x = grid.start.x
        self.start.dx = grid.size.x * 3
        self.start.dy = grid.size.y * 2

        self.end.x = grid.start.x + grid.size.x
        self.end.dx = grid.size.x * 3
        self.end.dy = grid.size.y * 2

        self.odd_start_y = grid.start.y - 2 * grid.size.y
        self.even_start_y = grid.start.y - grid.size.y

    def restart_y(self, x: int):
        if x & 1:
            self.start.y = self.odd_start_y
            self.end.y = self.even_start_y
        else:
            self.start.y = self.even_start_y
            self.end.y = self.odd_start_y


class RLine(LineDraw):
    def __init__(self, doc: MapOutput, grid: HexGrid, width: int, colour: Colour):
        super(RLine, self).__init__(doc, grid, width, colour)

    def _start_cursor(self, grid: HexGrid):
        self.start.x = grid.start.x + grid.size.x
        self.start.dx = grid.size.x * 3
        self.start.dy = grid.size.y * 2
        self.end.x = grid.start.x
        self.end.dx = grid.size.x * 3
        self.end.dy = grid.size.y * 2
        self.odd_start_y = grid.start.y - 3 * grid.size.y
        self.even_start_y = grid.start.y - 2 * grid.size.y

    def restart_y(self, x: int):
        if x & 1:
            self.start.y = self.odd_start_y
            self.end.y = self.even_start_y
        else:
            self.start.y = self.even_start_y
            self.end.y = self.odd_start_y
