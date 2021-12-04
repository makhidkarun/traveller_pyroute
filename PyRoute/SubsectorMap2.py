"""
Created on Aug 7, 2016

@author: tjoneslo
"""
import os
import logging
import math
from Map import GraphicMap
from Galaxy import Galaxy
from AllyGen import AllyGen
from PyRoute.FontLayer import FontLayer
from PIL import Image, ImageDraw, ImageColor, ImageFont


class GraphicSubsectorMap(GraphicMap):
    positions = {'A': (0, 0), 'B': (-8, 0), 'C': (-16, 0), 'D': (-24, 0),
                 'E': (0, -10), 'F': (-8, -10), 'G': (-16, -10), 'H': (-24, -10),
                 'I': (0, -20), 'J': (-8, -20), 'K': (-16, -20), 'L': (-24, -20),
                 'M': (0, -30), 'N': (-8, -30), 'O': (-16, -30), 'P': (-24, -30)}

    image_size = (826, 1272)  # (413,636)
    corePos = (image_size[0] / 2, 40)
    rimPos = (image_size[0] / 2, 1116)
    spinPos = (0, 1108 / 2)
    trailPos = (784, 1108 / 2)
    x_count = 9
    y_count = 11
    font_layer = None

    def __init__(self, galaxy, routes, trade_version):
        super(GraphicSubsectorMap, self).__init__(galaxy, routes)
        self.x_start = 56
        self.y_start = 56
        self.ym = 48  # half a hex height
        self.xm = 28  # half the length of one side
        self.textFill = self.fillWhite
        self.font_layer = FontLayer()
        self.namesFont = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 32)
        self.titleFont = ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed.ttf'), 48)
        self.hexFont = ImageFont.truetype(self.font_layer.getpath('LiberationMono-Bold.ttf'), 15)
        self.worldFont = ImageFont.truetype(self.font_layer.getpath('LiberationMono-Bold.ttf'), 22)
        self.hexFont2 = ImageFont.truetype(self.font_layer.getpath('FreeMono.ttf'), 22)
        self.hexFont3 = ImageFont.truetype(self.font_layer.getpath('FreeMono.ttf'), 36)
        self.hexFont4 = ImageFont.truetype(self.font_layer.getpath('Symbola-hint.ttf'), 22)
        self.hexFont5 = ImageFont.truetype(self.font_layer.getpath('Symbola-hint.ttf'), 36)
        self.logger = logging.getLogger('PyRoute.GraphicSubsectorMap')
        self.trade_version = trade_version

    def document(self, sector):
        self.sector = sector
        self.image = Image.new("RGB", self.image_size, "black")
        return ImageDraw.Draw(self.image)

    def close(self, subsector_name):
        path = os.path.join(self.galaxy.output_path, subsector_name + ".png")
        self.image = self.image.resize((413, 636), Image.BICUBIC)
        self.image.save(path)

    def write_maps(self):
        maps = len(self.galaxy.sectors) * 16
        logging.getLogger("PyRoute.SubsectorMap").info("writing {:d} subsector maps...".format(maps))

        for sector in self.galaxy.sectors.values():
            for subsector in sector.subsectors.values():
                self.subsector = subsector
                img = self.document(sector)
                self.write_base_map(img, subsector)
                if self.trade_version != 'None':
                    img = self.trade_lines(img, subsector)
                for star in subsector.worlds:
                    self.place_system(img, star)
                for star in subsector.worlds:
                    self.write_name(img, star)
                self.close(subsector.name)

    def sector_name(self, doc, name):
        pass

    def add_circle(self, doc, center, radius, colorname):
        color = ImageColor.getrgb(colorname)
        for offset in range(-3, 3):
            band = radius + offset
            doc.ellipse([(center.x - band, center.y - band), (center.x + band, center.y + band)], outline=color)

    def subsector_grid(self, doc, sector):
        pos = (20, 1140)
        name = sector.name + " / " + sector.sector.name
        size = doc.textsize(name, self.titleFont)
        if size[0] > 680:
            name = sector.name + " /"
            doc.text(pos, name, font=self.titleFont, fill=self.fillBlue)
            pos = (pos[0], pos[1] + size[1] + 4)
            doc.text(pos, sector.sector.name, font=self.titleFont, fill=self.fillBlue)
        else:
            doc.text(pos, name, font=self.titleFont, fill=self.fillBlue)

        # Draw inner line around hex grid
        start = self.cursor(53, 53)
        end = self.cursor(760, 1067)
        color = "white"

        for offset in range(-3, +3):
            doc.rectangle([(start.x + offset, start.y + offset), (end.x - offset, end.y - offset)], outline=color,
                          fill=None)

        start.x = 30
        start.y = 30
        end.x = 786
        end.y = 1096

        for offset in range(-3, +3):
            doc.rectangle([(start.x + offset, start.y + offset), (end.x - offset, end.y - offset)], outline=color,
                          fill=None)

        radius = 3
        line = self.get_line(doc, start, end, color, radius * 2)

        # Draw holes in outer line for names
        line.color = ImageColor.getrgb("black")
        # top line 
        start.y = 29
        end.y = 29
        start.x = 254
        end.x = 568
        line._draw()
        # bottom line 
        start.y = 1096
        end.y = 1096
        line._draw()
        # Left Side
        start.x = 29
        end.x = 29
        start.y = 400
        end.y = 722
        line._draw()
        # Right Side
        start.x = 786
        end.x = 786
        line._draw()

        # Draw small grid
        line.color = ImageColor.getrgb("white")
        line.width = 2
        # vertical lines

        start.x = 792
        start.y = 1120
        start.set_deltas(-22, 34)
        end.x = 792
        end.y = 1256
        end.set_deltas(-22, 34)

        line._draw()
        for _ in range(1, 5, 1):
            start.x_plus()
            end.x_plus()
            line._draw()

        # Horizontal lines
        start.x = 792
        start.y = 1120
        start.set_deltas(22, 34)
        end.x = 704
        end.y = 1120
        end.set_deltas(22, 34)
        line._draw()
        for _ in range(1, 5, 1):
            start.y_plus()
            end.y_plus()
            line._draw()

        pos = self.positions[sector.position]
        start.x = 704 + ((-pos[0] / 8) * 22)
        start.y = 1120 + ((-pos[1] / 10) * 34)
        doc.rectangle([(start.x, start.y), (start.x + 22, start.y + 34)], outline=line.color, fill=line.color)

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
        radius = (self.xm / 2) - 1

        if star.tradeCode.asteroid:
            worldCharacter = '\u2059'
            size = self.hexFont3.getsize(worldCharacter)
            pos = (point.x - size[0] / 2, point.y - size[1] * 0.6)
            doc.text(pos, worldCharacter, font=self.hexFont3, fill=self.textFill)

        else:
            color = ImageColor.getrgb(star.tradeCode.pcode_color)
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

        station_code = star.tradeCode.research_station_char
        if station_code:
            self.print_base_char(station_code, self.hexFont4, point, (-2.4, -0.5), doc, GraphicMap.fillRed)
            self.logger.debug("Research station for {} : {}".format(star.name, star.tradeCode))

    # Write the name of the world on the map (last).
    def write_name(self, doc, star):
        point = self.get_world_centerpoint(star)
        # Put the point in the center of the hex
        point.x_plus(self.xm)
        point.y_plus(self.ym)

        name = star.name
        if star.tradeCode.high:
            name = name.upper()
        elif star.tradeCode.low:
            name = name.lower()
        size = self.worldFont.getsize(name)
        pos = (point.x - (size[0] / 2) + 1, point.y + size[1])
        if star.tradeCode.capital:
            doc.text(pos, name, font=self.worldFont, fill=self.fillRed)
        else:
            doc.text(pos, name, font=self.worldFont, fill=self.textFill)

    def _world_point(self, hex_row, hex_col):
        col = self.xm * 3 * hex_col
        if (hex_col & 1):
            row = (self.y_start - self.ym * 2) + (hex_row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (hex_row * self.ym * 2)
        return self.cursor(col, row)

    # Get the center of the hex for writing a world
    def get_world_centerpoint(self, star):
        col = star.col + self.positions[star.subsector()][0]
        row = star.row + self.positions[star.subsector()][1]
        return self._world_point(row, col)

    def other_subsector_point(self, star, position):
        col_out = star.col + self.positions[position][0]
        row_out = star.row + self.positions[position][1]
        return self._world_point(row_out, col_out)

    def print_base_char(self, baseCharacter, font, point, multiplier, doc, fill=GraphicMap.fillWhite):
        size = font.getsize(baseCharacter)
        pos = (point.x + (multiplier[0] * size[0]), point.y + (multiplier[1] * size[1]))
        doc.text(pos, baseCharacter, font=font, fill=fill)

    def trade_lines(self, doc, subsector):
        self.image = self.image.convert("RGBA")
        img = Image.new("RGBA", self.image_size, 0)
        draw = ImageDraw.Draw(img)

        trade = [pair for pair in self.galaxy.stars.edges(subsector.worlds, True) \
                 if pair[2]['distance'] < 3 and \
                 (pair[2]['SourceMarketPrice'] > 0 or pair[2]['TargetMarketPrice'] > 0)]

        self.logger.info("Generating routes in {} for {} worlds".format(subsector.name, len(trade)))
        for (star, neighbor, data) in trade:
            self.trade_line(draw, star, neighbor, data, subsector.position)

        cropped = img.crop((53, 53, 760, 1067))
        cropped = cropped.crop((-53, -53, 760 + (826 - 760 - 53), 1067 + (1272 - 1067 - 53)))
        self.image = Image.alpha_composite(self.image, cropped)
        self.logger.debug("Completed trade_lines for {}".format(subsector.name))
        return ImageDraw.Draw(self.image)

    def trade_color(self, trade):
        tcolor = {0: "#0500ff", 1: "#0012ff", 2: "#0094ff", 3: "#00ffa8",
                  4: "#8aff00", 5: "#FFd200", 6: "#FF8200", 7: "#FF3200",
                  9: "#FF0030", 9: "#FF00B0", 10: "#FF04F0", 11: "#FF0CF0"}
        return tcolor.get(trade, "#000000")

    def centerpoint(self, star):
        point = self.get_world_centerpoint(star)
        point.x_plus(self.xm)
        point.y_plus(self.ym)
        return point

    def other_centerpoint(self, star, position):
        point = self.other_subsector_point(star, position)
        point.x_plus(self.xm)
        point.y_plus(self.ym)
        return point

    def trade_line(self, doc, star, neighbor, data, position):
        if star.subsector() == neighbor.subsector():
            star_start = self.centerpoint(star)
            star_end = self.centerpoint(neighbor)
        elif star.subsector() == position:
            star_start = self.centerpoint(star)
            star_end = self.other_centerpoint(neighbor, position)
            pass
        elif neighbor.subsector() == position:
            star_start = self.other_centerpoint(star, position)
            star_end = self.centerpoint(neighbor)

            # self.logger.info ("trade to different subsector: {} - {}".format(star, neighbor))
        #    return 
        if data['SourceMarketPrice'] > 0:
            trade = data['SourceMarketPrice'] - 1000 - (star.trade_cost * 1000)
            if trade > 0:
                color = self.trade_color(int(round(trade / 1000)))
                self.draw_one_arc(doc, star_start, star_end, color)
        if data['TargetMarketPrice'] > 0:
            trade = data['TargetMarketPrice'] - 1000 - (neighbor.trade_cost * 1000)
            if trade > 0:
                color = self.trade_color(int(round(trade / 1000)))
                self.draw_one_arc(doc, star_end, star_start, color)

    def draw_one_arc(self, doc, start, end, color):
        center = self.circle_center(start, end)
        self.draw_arc(doc, center, start, end, color)

    def circle_center(self, start, end):
        # Calculate the center of an equilateral triangle from start and end
        # root3 = math.sqrt(3)
        root3 = 2
        xm = 0.5 * (start.x + end.x)
        ym = 0.5 * (start.y + end.y)

        xslope = (xm - start.x)
        yslope = (ym - start.y)

        slope = xslope / yslope if yslope != 0 else 0

        cx = xm + (root3 * slope)
        cy = ym + (root3 * slope)

        return self.cursor(round(cx), round(cy))

    def draw_arc(self, doc, center, start, end, color):
        r = math.sqrt((start.x - center.x) ** 2 + (start.y - center.y) ** 2)
        x1 = center.x - r
        y1 = center.y - r
        x2 = center.x + r
        y2 = center.y + r
        startAngle = (180 / math.pi) * math.atan2(start.y - center.y, start.x - center.x)
        endAngle = (180 / math.pi) * math.atan2(end.y - center.y, end.x - center.x)

        for i in range(-2, 2):
            doc.arc([x1 + i, y1, x2 + i, y2], startAngle, endAngle, color)
            doc.arc([x1, y1 + i, x2, y2 + i], startAngle, endAngle, color)

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
