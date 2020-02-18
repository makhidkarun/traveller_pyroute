"""
Created on Aug 7, 2016

@author: tjoneslo
"""
import os
import logging
from .Map import GraphicMap
from .Galaxy import Galaxy
from .AllyGen import AllyGen
from PIL import Image, ImageDraw, ImageColor, ImageFont


class GraphicSubsectorMap(GraphicMap):
    positions = {'A': (0, 0), 'B': (-8, 0), 'C': (-16, 0), 'D': (-24, 0),
                 'E': (0, -10), 'F': (-8, -10), 'G': (-16, -10), 'H': (-24, -10),
                 'I': (0, -20), 'J': (-8, -20), 'K': (-16, -20), 'L': (-24, -20),
                 'M': (0, -30), 'N': (-8, -30), 'O': (-16, -30), 'P': (-24, -30)}

    image_size = (413, 636)
    corePos = (image_size[0] / 2, 20)
    rimPos = (image_size[0] / 2, 558)
    spinPos = (0, 554 / 2)
    trailPos = (392, 554 / 2)
    x_count = 9
    y_count = 11

    def __init__(self, galaxy, routes):
        super(GraphicSubsectorMap, self).__init__(galaxy, routes)
        self.x_start = 28
        self.y_start = 28
        self.ym = 24  # half a hex height
        self.xm = 14  # half the length of one side
        self.textFill = self.fillWhite
        self.namesFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 16)
        self.titleFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 24)
        self.hexFont = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 8)
        self.worldFont = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 11)
        self.hexFont2 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 12)
        self.hexFont3 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 18)
        self.hexFont4 = ImageFont.truetype("/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf", 22)
        self.hexFont5 = ImageFont.truetype("/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf", 36)
        self.logger = logging.getLogger('PyRoute.GraphicSubsectorMap')

    def document(self, sector):
        self.sector = sector
        self.image = Image.new("RGB", self.image_size, "black")
        return ImageDraw.Draw(self.image)

    def close(self, subsector_name):
        path = os.path.join(self.galaxy.output_path, subsector_name + ".png")
        self.image.save(path)

    def write_maps(self):
        maps = len(self.galaxy.sectors) * 16
        logging.getLogger("PyRoute.SubsectorMap").info("writing {:d} subsector maps...".format(maps))

        for sector in self.galaxy.sectors.values():
            for subsector in sector.subsectors.values():
                self.subsector = subsector
                img = self.document(sector)
                self.write_base_map(img, subsector)
                for star in subsector.worlds:
                    self.place_system(img, star)
                for star in subsector.worlds:
                    self.write_name(img, star)
                self.close(subsector.name)

    def sector_name(self, doc, name):
        pass

    def subsector_grid(self, doc, sector):
        pos = (10, 570)
        name = sector.name + " / " + sector.sector.name
        size = doc.textsize(name, self.titleFont)
        if size[0] > 340:
            name = sector.name + " /"
            doc.text(pos, name, font=self.titleFont, fill=self.fillBlue)
            pos = (pos[0], pos[1] + size[1] + 4)
            doc.text(pos, sector.sector.name, font=self.titleFont, fill=self.fillBlue)
        else:
            doc.text(pos, name, font=self.titleFont, fill=self.fillBlue)

        # Draw inner line around hex grid
        start = self.cursor(25, 25)
        end = self.cursor(385, 538)
        color = "white"

        doc.rectangle([(start.x - 1, start.y - 1), (end.x + 1, end.y + 1)], outline=color, fill=None)
        doc.rectangle([(start.x, start.y), (end.x, end.y)], outline=color, fill=None)
        doc.rectangle([(start.x + 1, start.y + 1), (end.x - 1, end.y - 1)], outline=color, fill=None)
        doc.rectangle([(start.x + 2, start.y + 2), (end.x - 2, end.y - 2)], outline=color, fill=None)

        start.x = 15
        start.y = 15
        end.x = 396
        end.y = 548
        doc.rectangle([(start.x - 1, start.y - 1), (end.x + 1, end.y + 1)], outline=color, fill=None)
        doc.rectangle([(start.x, start.y), (end.x, end.y)], outline=color, fill=None)
        doc.rectangle([(start.x + 1, start.y + 1), (end.x - 1, end.y - 1)], outline=color, fill=None)
        doc.rectangle([(start.x + 2, start.y + 2), (end.x - 2, end.y - 2)], outline=color, fill=None)

        radius = 3
        line = self.get_line(doc, start, end, color, radius * 2)

        # Draw holes in outer line for names
        line.color = ImageColor.getrgb("black")
        start.y = 15
        end.y = 15
        start.x = 127
        end.x = 284
        line._draw()
        start.y = 548
        end.y = 548
        line._draw()
        start.x = 15
        end.x = 15
        start.y = 200
        end.y = 361
        line._draw()
        start.x = 396
        end.x = 396
        line._draw()

        # Draw small grid
        line.color = ImageColor.getrgb("grey")
        line.width = 1
        # vertical lines

        start.x = 396
        start.y = 560
        start.set_deltas(-11, 17)
        end.x = 396
        end.y = 628
        end.set_deltas(-11, 17)

        line._draw()
        for _ in range(1, 5, 1):
            start.x_plus()
            end.x_plus()
            line._draw()

        # Horizontal lines
        start.x = 396
        start.y = 560
        start.set_deltas(11, 17)
        end.x = 352
        end.y = 560
        end.set_deltas(11, 17)
        line._draw()
        for _ in range(1, 5, 1):
            start.y_plus()
            end.y_plus()
            line._draw()

        pos = self.positions[sector.position]
        start.x = 352 + ((-pos[0] / 8) * 11)
        start.y = 560 + ((-pos[1] / 10) * 17)
        doc.rectangle([(start.x, start.y), (start.x + 11, start.y + 17)], outline=line.color, fill=line.color)

    def _set_pos(self, x, y):
        location = (-self.positions[self.subsector.position][0] + x,
                    -self.positions[self.subsector.position][1] + y)

        q, r = self.convert_hex_to_axial(location[0] + self.sector.dx - 1,
                                         location[1] + self.sector.dy - 1)

        pos = (q, r)
        col = self.xm * 3 * x
        if (x & 1):
            row = (self.y_start - self.ym * 2) + (y * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (y * self.ym * 2)
        point = self.cursor(col, row)
        point.x_plus(self.xm)
        point.y_plus(self.ym)
        return pos, point, location

    def hex_grid(self, doc, draw, width, colorname='gray'):

        # Fill each hex with color (if needed)

        for x in range(1, self.x_count, 1):
            for y in range(1, self.y_count, 1):
                pos, point, _ = self._set_pos(x, y)
                self.fill_aleg_hex(doc, pos, point)

        # Draw the base hexes
        super(GraphicSubsectorMap, self).hex_grid(doc, draw, width, colorname)

        # Draw the borders and add the hex numbers
        for x in range(1, self.x_count, 1):
            for y in range(1, self.y_count, 1):
                pos, point, location = self._set_pos(x, y)
                self.draw_border(doc, pos, point)

                name = "{0:02d}{1:02d}".format(location[0], location[1])
                point.y_plus(-self.ym + 1)
                size = self.hexFont.getsize(name)
                pos = (point.x - size[0] / 2, point.y)

                doc.text(pos, name, font=self.hexFont, fill=self.fillWhite)

    alegColor = {"Na": "#000000", "Im": "#401312", "Zh": "#26314e",
                 "CsZh": "#000000", "CsIm": "#000000", "CsRe": "#000000",
                 "ReDe": "#401312", "FeAr": "#3E1D2C",
                 "SwCf": "#003C4A", "DaCf": "#222222",
                 "VAsP": "#11470C", "VDeG": "#11470C", "VInL": "#11470C", "VOpA": "#11470C"}
    borderColor = {"Na": "#000000", "Im": "#FF7978", "Zh": "#818ded",
                   "CsZh": "#000000", "CsIm": "#000000", "CsRe": "#000000",
                   "ReDe": "#FF7978", "FeAr": "#cc849f",
                   "SwCf": "#33b2c0", "DaCf": "#d7d7d7",
                   "VAsP": "#238E18", "VDeG": "#238E18", "VInL": "#238E18", "VOpA": "#238E18"}

    def fill_aleg_hex(self, doc, pos, point):
        if pos in self.galaxy.borders.allyMap:
            aleg = self.galaxy.borders.allyMap[pos]
            color = self.alegColor.get(aleg, '#000000')
            doc.polygon([(point.x - self.xm, point.y - self.ym),
                         (point.x + self.xm, point.y - self.ym),
                         (point.x + self.xm * 2, point.y),
                         (point.x + self.xm, point.y + self.ym),
                         (point.x - self.xm, point.y + self.ym),
                         (point.x - self.xm * 2, point.y)],
                        outline=None, fill=color)

    def draw_border(self, doc, pos, point):
        start = self.cursor(25, 25)
        end = self.cursor(385, 538)
        if pos in self.galaxy.borders.allyMap:
            aleg = self.galaxy.borders.allyMap[pos]
            bColor = self.borderColor.get(aleg, '#f2f2f2')
            line = self.get_line(doc, start, end, bColor, 3)

            if AllyGen.is_nonaligned(aleg):
                return
            for n in range(6):
                next_hex = AllyGen._get_neighbor(pos, n)
                next_aleg = self.galaxy.borders.allyMap[next_hex] \
                    if next_hex in self.galaxy.borders.allyMap \
                    else AllyGen.noOne[0]
                if not AllyGen.are_allies(aleg, next_aleg):
                    if n == 1:
                        start.x = point.x + self.xm * 2
                        start.y = point.y
                        end.x = point.x + self.xm
                        end.y = point.y - self.ym
                        line._draw()
                    elif n == 2:
                        start.x = point.x - self.xm
                        start.y = point.y - self.ym
                        end.x = point.x + self.xm
                        end.y = point.y - self.ym
                        line._draw()
                    elif n == 3:
                        start.x = point.x - self.xm
                        start.y = point.y - self.ym
                        end.x = point.x - self.xm * 2
                        end.y = point.y
                        line._draw()
                    elif n == 4:
                        start.x = point.x - self.xm * 2
                        start.y = point.y
                        end.x = point.x - self.xm
                        end.y = point.y + self.ym
                        line._draw()
                    elif n == 5:
                        start.x = point.x - self.xm
                        start.y = point.y + self.ym
                        end.x = point.x + self.xm
                        end.y = point.y + self.ym
                        line._draw()
                    elif n == 0:
                        start.x = point.x + self.xm
                        start.y = point.y + self.ym
                        end.x = point.x + self.xm * 2
                        end.y = point.y
                        line._draw()

    def place_system(self, doc, star):
        point = self.get_world_centerpoint(star)
        self.zone(doc, star, point.copy())

        # Put the point in the center of the hex
        point.x_plus(self.xm)
        point.y_plus(self.ym)

        # Draw the center dot colored to reflect the world type.
        radius = self.xm / 2
        radius -= 1
        pcolor = {'As': '#8E9397', 'De': '#EDC9AF', 'Fl': '#FFB0B0', 'He': '#FF8D3F', 'Ic': '#A5F2F3',
                  'Oc': '#0094ED', 'Po': '#C4D6C4', 'Va': '#F0F0F0', 'Wa': '#7ACFF7'}
        if star.pcode and star.pcode in pcolor:
            color = ImageColor.getrgb(pcolor[star.pcode])
        else:
            color = ImageColor.getrgb('#C0FFC0')

        if star.pcode == 'As':
            worldCharacter = '\\u2059'
            size = self.hexFont3.getsize(worldCharacter)
            pos = (point.x - size[0] / 2, point.y - size[1] * 0.6)
            doc.text(pos, worldCharacter, font=self.hexFont3, fill=self.textFill)

        else:
            doc.ellipse([(point.x - radius, point.y - radius), (point.x + radius, point.y + radius)], fill=color,
                        outline=color)

        # Write Port code        
        size = self.worldFont.getsize(star.port)
        pos = (point.x - (size[0] / 2) + 1, point.y - (2 * size[1]) + 1)
        doc.text(pos, star.port, font=self.worldFont, fill=self.textFill)

        if star.ggCount:
            self.print_base_char('\u25CF', self.worldFont, point, (1.75, -2), doc)

        if 'N' in star.baseCode or 'K' in star.baseCode:
            self.print_base_char('\u066D', self.hexFont3, point, (-1.25, -1.5), doc)
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'S' in star.baseCode:
            self.print_base_char('\u25B2', self.hexFont4, point, (-2.25, -1.5), doc)
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'D' in star.baseCode:
            self.print_base_char('\u25A0', self.hexFont4, point, (-2, -0.5), doc)
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'W' in star.baseCode:
            self.print_base_char('\u25B2', self.hexFont4, point, (-2.25, -1.5), doc, GraphicMap.fillRed)
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        if 'I' in star.baseCode:
            self.print_base_char('\u2316', self.hexFont5, point, (-2.5, -0.5), doc)
            self.logger.debug("Base for {} : {}".format(star.name, star.baseCode))

        research = {'RsA': '\u0391', 'RsB': '\u0392', 'RsG': '\u0393',
                    'RsD': '\u0394', 'RdE': '\u0395', 'RsZ': '\u0396',
                    'RsT': '\u0398', 'RsI': '\u0399', 'RsK': '\u039A'}
        keys = set(research.keys()).intersection(star.tradeCode)
        if len(keys) == 1:
            station = next(iter(keys))
            self.print_base_char(research[station], self.hexFont4, point, (-2, -0.5), doc, GraphicMap.fillRed)
            self.logger.debug("Research station for {} : {}".format(star.name, " ".join(star.tradeCode)))

    # Write the name of the world on the map (last).
    def write_name(self, doc, star):
        point = self.get_world_centerpoint(star)
        # Put the point in the center of the hex
        point.x_plus(self.xm)
        point.y_plus(self.ym)

        name = star.name
        if 'Hi' in star.tradeCode:
            name = name.upper()
        elif 'Lo' in star.tradeCode:
            name = name.lower()
        size = self.worldFont.getsize(name)
        pos = (point.x - (size[0] / 2) + 1, point.y + size[1])
        if star.capital:
            doc.text(pos, name, font=self.worldFont, fill=self.fillRed)
        else:
            doc.text(pos, name, font=self.worldFont, fill=self.textFill)

    # Get the center of the hex for writing a world
    def get_world_centerpoint(self, star):
        col = star.col + self.positions[star.subsector()][0]
        row = star.row + self.positions[star.subsector()][1]

        col = self.xm * 3 * col
        if (star.col & 1):
            row = (self.y_start - self.ym * 2) + (row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (row * self.ym * 2)

        return self.cursor(col, row)

    def print_base_char(self, baseCharacter, font, point, multiplier, doc, fill=GraphicMap.fillWhite):
        size = font.getsize(baseCharacter)
        pos = (point.x + (multiplier[0] * size[0]), point.y + (multiplier[1] * size[1]))
        doc.text(pos, baseCharacter, font=font, fill=fill)

    # if len(star.name) > 0:
    #    for chars in xrange(len(star.name), 0, -1):
    #        width = self.string_width(pdf.get_font(), star.name[:chars])
    #        if width <= self.xm * 3.5:
    #            break
    #    point.y_plus(3.5)
    #   point.x = col
    #    point.x_plus(self.ym - (width/2))
    #    pdf.add_text(star.name[:chars].encode('ascii', 'replace'), point)
    #
    # added = star.alg
    # if 'Cp' in star.tradeCode:
    #    added += '+'
    # elif 'Cx' in star.tradeCode or 'Cs' in star.tradeCode:
    #    added += '*'
    # else:
    #    added += ' '
    #
    # added += '{:d}'.format (star.ggCount)
    # point.y_plus(3.5)
    # point.x = col
    # width = pdf.get_font()._string_width(added)
    # point.x_plus(self.ym - (width/2))
    # pdf.add_text(added, point)

    # added = ''
    # tradeIn = StatCalculation.trade_to_btn(star.tradeIn)
    # tradeThrough = StatCalculation.trade_to_btn(star.tradeIn + star.tradeOver)

    # if self.routes == 'trade':
    #    added += "{:X}{:X}{:X}{:d}".format(star.wtn, tradeIn, tradeThrough, star.starportSize)
    # elif self.routes == 'comm':
    #    added += "{}{} {}".format(star.baseCode,star.ggCount,star.importance)
    # elif self.routes == 'xroute':
    #    added += " {}".format(star.importance)
    # width = pdf.get_font()._string_width(added)
    # point.y_plus(3.5)
    # point.x = col
    # point.x_plus(self.ym - (width/2))
    # pdf.add_text(added, point)

    # pdf.set_font(def_font)


if __name__ == '__main__':
    # route.set_logging('DEBUG')
    galaxy = Galaxy(15, 4, 8)
    galaxy.output_path = '.'
    galaxy.read_sectors(['../sectors_tne/SpinwardMarches.sec'], 'fixed', 'collapse')
    galaxy.set_borders('erode', 'collapse')

    graphMap = GraphicSubsectorMap(galaxy, None)
    graphMap.write_maps()

    # img = graphMap.document(galaxy.sectors['Spinward Marches'])
    # subsector = galaxy.sectors['Spinward Marches'].subsectors['I']

    # graphMap.write_base_map(img, subsector)
    # graphMap.draw_borders(img, subsector)
    # for star in subsector.worlds:
    #    graphMap.place_system(img, star)

    # graphMap.close()
