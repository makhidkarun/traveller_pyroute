from itertools import product
import logging
from PIL import Image, ImageDraw
from PyRoute.Galaxy import Galaxy
from PyRoute.HexMap import HexMap
from PyRoute.route import route


class GraphMap(object):

    def __init__(self, galaxy, routes, min_btn=8):
        self.logger = logging.getLogger('PyRoute.GraphMap')
        self.galaxy = galaxy
        self.routes = routes
        self.min_btn = min_btn
        minx = miny = 20
        maxx = maxy = -20
        for sector in self.galaxy.sectors.values():
            if sector.x < minx:
                self.dx = sector.x
                self.gx = sector.dx
            if sector.y < miny:
                self.dy = sector.y
                self.gy = sector.dy
            minx = min(minx, sector.x)
            miny = min(miny, sector.y)
            maxx = max(maxx, sector.x)
            maxy = max(maxy, sector.y)
        self.minx = minx
        self.miny = miny
        self.sx = maxx - minx + 1
        self.sy = maxy - miny + 1

        self.logger.info("output size: {} x {}".format(self.sx, self.sy))
        self.image = Image.new("RGB", (64 * self.sx + 1, 80 * self.sy + 1), "black")

    def write_dot_map(self):

        draw = ImageDraw.Draw(self.image)
        for x, y in product(list(range(self.sx)), list(range(self.sy))):
            sx = x * 64
            sy = y * 80

            draw.line([(sx, 0), (sx, self.image.size[1])], fill=(0, 0, 192))
            draw.line([(sx + 16, 0), (sx + 16, self.image.size[1])], fill=(0, 0, 128))
            draw.line([(sx + 32, 0), (sx + 32, self.image.size[1])], fill=(0, 0, 128))
            draw.line([(sx + 48, 0), (sx + 48, self.image.size[1])], fill=(0, 0, 128))
            draw.line([(sx + 64, 0), (sx + 64, self.image.size[1])], fill=(0, 0, 192))

            draw.line([(0, sy), (self.image.size[0], sy)], fill=(0, 0, 192))
            draw.line([(0, sy + 20), (self.image.size[0], sy + 20)], fill=(0, 0, 128))
            draw.line([(0, sy + 40), (self.image.size[0], sy + 40)], fill=(0, 0, 128))
            draw.line([(0, sy + 60), (self.image.size[0], sy + 60)], fill=(0, 0, 128))
            draw.line([(0, sy + 80), (self.image.size[0], sy + 80)], fill=(0, 0, 192))

            # for x,y in product (range(65), range(81)):
        #    if x % 64 == 0 or y % 80 == 0:
        #        self.image.putpixel((x, y), (0, 0, 192))
        #    elif x % 16 == 0 or y % 20 == 0:
        #        self.image.putpixel((x,y), (0,0,128))

        for x, y in product(list(range(self.sx * 32)), list(range(self.sy * 40))):
            px = (x + 1) * 2 - 1
            py = (y + 1) * 2 - ((x + 1) & 1)
            self.image.putpixel((px, py), (0, 50, 0))
            wx = x + self.gx
            wy = y + self.gy - 1
            self._draw_borders(wx, wy, px, py)
            # self._draw_borders(sector, world.col, world.row, x, y)

        for sector in self.galaxy.sectors.values():
            sx = (sector.x - self.dx) * 64
            sy = (sector.y - self.dy) * 80

            for world in sector.worlds:
                x = sx + (world.col * 2 - 1)
                y = sy + (world.row * 2 - (world.col & 1))
                self.image.putpixel((x, y), (0, 160, 0))

        self.image.save("Core.gif", None)

    def _draw_borders(self, wx, wy, lx, ly):
        # q, r = HexMap.convert_hex_to_axial(wx + sector.dx, wy + sector.dy - 1)
        q, r = HexMap.convert_hex_to_axial(wx, wy)
        if self.galaxy.borders.borders.get((q, r), False):
            if self.galaxy.borders.borders[(q, r)] & 1:  # TOP
                self.image.putpixel((lx, ly - 1), (160, 0, 0))
                self.image.putpixel((lx - 1, ly - 1), (160, 0, 0))
                self.image.putpixel((lx + 1, ly - 1), (160, 0, 0))
            if self.galaxy.borders.borders[(q, r)] & 2:  # Rline
                self.logger.info('Hex location rline: {} : {} -> {}, {}'.format(wx, wy, lx, ly))
                if wy & 1:
                    self.image.putpixel((lx - 1, ly), (0, 255, 160))
                else:
                    self.image.putpixel((lx + 1, ly), (0, 160, 160))
            if self.galaxy.borders.borders[(q, r)] & 4:  # Lline
                if wy & 1:
                    self.image.putpixel((lx + 1, ly), (160, 0, 160))
                else:
                    self.image.putpixel((lx - 1, ly), (160, 0, 255))

    def write_sector_map(self, sector):
        self.image = Image.new("RGB", (612, 792), "white")

        pass

    def hex_grid(self, pdf, draw, width, colorname='gray'):

        hlineStart, hlineEnd, hline = self._hline(pdf, width, colorname)
        llineStart, llineEnd, lline = self._lline(pdf, width, colorname)
        rlineStart, rlineEnd, rline = self._rline(pdf, width, colorname)

        for x in range(33):
            hlineStart.x_plus()
            hlineEnd.x_plus()
            self._hline_restart_y(x, hlineStart, hlineEnd)
            self._lline_restart_y(x, llineStart, llineEnd)
            self._rline_restart_y(x, rlineStart, rlineEnd)

            for y in range(41):
                hlineStart.y_plus()
                hlineEnd.y_plus()
                llineStart.y_plus()
                llineEnd.y_plus()
                rlineStart.y_plus()
                rlineEnd.y_plus()

                draw(x, y, hline, lline, rline)

            llineStart.x_plus()
            llineEnd.x_plus()
            rlineStart.x_plus()
            rlineEnd.x_plus()


if __name__ == '__main__':
    route.set_logging('INFO')
    galaxy = Galaxy(8)
    galaxy.output_path = '.'
    galaxy.read_sectors(['../sectors_review/Spica.sec'],
                        'fixed', 'collapse')
    galaxy.set_borders('range', 'collapse')
    hexMap = GraphMap(galaxy, None)
    hexMap.write_dot_map()

    pdfmap = HexMap(galaxy, 'none', '8')
    pdfmap.write_maps()
