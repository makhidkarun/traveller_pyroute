"""
Created on May 14, 2016

@author: tjoneslo
"""
import logging
import os
from pypdflite import PDFLite, PDFCursor
from pypdflite.pdfobjects.pdfellipse import PDFEllipse
from pypdflite.pdfobjects.pdfline import PDFLine
from pypdflite.pdfobjects.pdftext import PDFText

from PIL import Image, ImageDraw, ImageColor, ImageFont
from PyRoute.StatCalculation import StatCalculation


class Cursor(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

    def set_deltas(self, dx=2, dy=2):
        self.dx = dx
        self.dy = dy

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value=0):
        # If in left margin, sets to minimum value.
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value=0):
        self._y = value

    # Changes this cursor
    def x_plus(self, dx=None):
        """
        Mutable x addition. Defaults to set delta value.
        """
        if dx is None:
            self.x += self.dx
        else:
            self.x = self.x + dx

    def y_plus(self, dy=None):
        """
        Mutable y addition. Defaults to set delta value.
        """
        if dy is None:
            self.y += self.dy
        else:
            self.y = self.y + dy

    def copy(self):
        new_cursor = self.__class__(self.x, self.y)
        new_cursor.set_deltas(self.dx, self.dy)
        return new_cursor

    def __str__(self):
        return "({:f}, {:f})".format(self.x, self.y)


class GraphicLine(object):
    def __init__(self, image, lineStart, lineEnd, colorname, width):
        self.image = image
        self.lineStart = lineStart
        self.lineEnd = lineEnd
        self.color = ImageColor.getrgb(colorname)
        self.width = max(1, int(width))

    def _draw(self):
        self.image.line([(self.lineStart.x, self.lineStart.y), (self.lineEnd.x, self.lineEnd.y)], self.color,
                        self.width)


class Map(object):
    x_count = 33
    y_count = 41
    y_start = 43
    x_start = 15

    def __init__(self, galaxy, routes):
        self.galaxy = galaxy
        self.routes = routes
        self.ym = 9  # half a hex height
        self.xm = 6  # half the length of one side
        self.colorStart = 0

    def document(self, sector):
        """
        Generated by the type of document
        """
        raise NotImplementedError("Base Class")

    def close(self):
        raise NotImplementedError("Base Class")

    def cursor(self, x, y):
        """
        create a cursor (position) element
        """
        raise NotImplementedError("Base Class")

    def sector_name(self, doc, name):
        """
        Write name at the top of the document
        """
        raise NotImplementedError("Base Class")

    def coreward_sector(self, doc, name):
        raise NotImplementedError("Base Class")

    def rimward_sector(self, doc, name):
        raise NotImplementedError("Base Class")

    def spinward_sector(self, doc, name):
        raise NotImplementedError("Base Class")

    def trailing_sector(self, doc, name):
        raise NotImplementedError("Base Class")

    def add_line(self, doc, start, end, color):
        """
        Add a line to the document, from start to end, in color
        """
        raise NotImplementedError("Base Class")

    def add_circle(self, doc, center, colorname):
        """
        Add a circle to the document, from start to end, in color
        """
        raise NotImplementedError("Base Class")

    def get_line(self, doc, start, end, colorname, width):
        """
        Get a line draw method processor
        """
        raise NotImplementedError("Base Class")
        # color = pdf.get_color()
        # color.set_color_by_name(colorname)
        # hline = PDFLine(pdf.session, pdf.page, hlineStart, hlineEnd, stroke='solid', color=color, size=width)

    def place_system(self, doc, star):
        """
        Write a single world information into the map
        """
        raise NotImplementedError("Base Class")

    def write_maps(self):
        """
        Starting point for writing PDF files.
        Call this to output the trade maps
        """
        logging.getLogger("PyRoute.Map").info("writing {:d} sector maps...".format(len(self.galaxy.sectors)))
        for sector in self.galaxy.sectors.values():
            doc = self.document(sector)
            self.write_base_map(doc, sector)

            self.draw_borders(doc, sector)

            sector_trade = [star for star in self.galaxy.stars.edges(sector.worlds, True) \
                            if star[2]['trade'] > 0 and StatCalculation.trade_to_btn(star[2]['trade']) >= self.min_btn]

            logging.getLogger('PyRoute.Map').debug("Worlds with trade: {}".format(len(sector_trade)))

            sector_trade.sort(key=lambda line: line[2]['trade'])

            for (star, neighbor, data) in sector_trade:
                self.galaxy.stars[star][neighbor]['trade btn'] = StatCalculation.trade_to_btn(data['trade'])
                self.trade_line(doc, [star, neighbor], data)

            # Get all the worlds in this sector
            # for (star, neighbor, data) in self.galaxy.stars.edges(sector.worlds, True):
            #    if star.sector != sector:
            #        continue#
            #    if data['trade'] > 0 and self.trade_to_btn(data['trade']) >= self.min_btn:
            #        self.galaxy.stars[star][neighbor]['trade btn'] = self.trade_to_btn(data['trade'])
            #        self.trade_line(doc, [star, neighbor], data)
            #    elif star.sector != neighbor.sector:
            #        data = self.galaxy.stars.get_edge_data(neighbor, star)
            #        if data is not None and \
            #            data['trade'] > 0 and \
            #            self.trade_to_btn(data['trade']) >= self.min_btn:
            #            self.trade_line(doc, [star, neighbor], data)

            for star in sector.worlds:
                self.place_system(doc, star)

            self.close()

    def write_base_map(self, doc, sector):
        self.sector_name(doc, sector.name)
        self.subsector_grid(doc, sector)
        self.hex_grid(doc, self._draw_all, 2)
        if sector.coreward:
            self.coreward_sector(doc, sector.coreward.name)
        if sector.rimward:
            self.rimward_sector(doc, sector.rimward.name)
        if sector.spinward:
            self.spinward_sector(doc, sector.spinward.name)
        if sector.trailing:
            self.trailing_sector(doc, sector.trailing.name)

    def zone(self, doc, star, point):
        point.x_plus(self.xm)
        point.y_plus(self.ym)

        if star.zone in ['R', 'F']:
            self.add_circle(doc, point, self.xm, 'crimson')
        elif star.zone in ['A', 'U']:
            self.add_circle(doc, point, self.xm, 'goldenrod')
        else:  # no zone -> do nothing
            return

    def subsector_grid(self, doc, sector):
        vlineStart = self.cursor(0, self.y_start)
        vlineEnd = self.cursor(0, self.y_start + (180 * 4))
        for x in range(self.x_start, 598, 144):
            if x >= self.x_start + 144:
                x += 3
            vlineStart.x = x
            vlineEnd.x = x
            self.add_line(doc, vlineStart, vlineEnd, 'darkgray')
        hlineStart = self.cursor(self.x_start, 0)
        hlineEnd = self.cursor(594, 0)
        for y in range(self.y_start, 780, 180):
            hlineStart.y = y
            hlineEnd.y = y
            self.add_line(doc, hlineStart, hlineEnd, 'darkgray')

    def hex_grid(self, doc, draw, width, colorname='gray'):

        hlineStart, hlineEnd, hline = self._hline(doc, width, colorname)
        llineStart, llineEnd, lline = self._lline(doc, width, colorname)
        rlineStart, rlineEnd, rline = self._rline(doc, width, colorname)

        for x in range(self.x_count):
            hlineStart.x_plus()
            hlineEnd.x_plus()
            self._hline_restart_y(x, hlineStart, hlineEnd)
            self._lline_restart_y(x, llineStart, llineEnd)
            self._rline_restart_y(x, rlineStart, rlineEnd)

            for y in range(self.y_count):
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

    def _draw_all(self, x, y, hline, lline, rline):
        if (x < self.x_count - 1):
            hline._draw()
        lline._draw()
        if (y > 0):
            rline._draw()

    def _draw_borders(self, x, y, hline, lline, rline):
        q, r = self.convert_hex_to_axial(x + self.sector.dx, y + self.sector.dy - 1)

        if self.galaxy.borders.borders.get((q, r), False):
            if self.galaxy.borders.borders[(q, r)] & 1:
                hline._draw()

            if self.galaxy.borders.borders[(q, r)] & 2 and y > 0:
                rline._draw()

            if self.galaxy.borders.borders[(q, r)] & 4:
                lline._draw()

    def draw_borders(self, pdf, sector):
        self.hex_grid(pdf, self._draw_borders, 1.5, 'salmon')

    @staticmethod
    def convert_hex_to_axial(row, col):
        x = row
        z = col - (row - (row & 1)) / 2
        return (x, z)

    def _hline(self, doc, width, colorname):
        hlineStart = self.cursor(0, 0)
        hlineStart.x = self.x_start - (self.xm * 2)
        hlineStart.y = self.y_start - self.ym
        hlineStart.dx = self.xm * 3
        hlineStart.dy = self.ym * 2

        hlineEnd = self.cursor(0, 0)
        hlineEnd.x = self.x_start
        hlineEnd.y = self.y_start - self.ym
        hlineEnd.dx = self.xm * 3
        hlineEnd.dy = self.ym * 2

        hline = self.get_line(doc, hlineStart, hlineEnd, colorname, width)
        return (hlineStart, hlineEnd, hline)

    def _lline(self, doc, width, colorname):
        llineStart = self.cursor(-10, 0)
        llineStart.x = self.x_start
        llineStart.dx = self.xm * 3
        llineStart.dy = self.ym * 2

        llineEnd = self.cursor(-10, 0)
        llineEnd.x = self.x_start + self.xm
        llineEnd.dx = self.xm * 3
        llineEnd.dy = self.ym * 2

        lline = self.get_line(doc, llineStart, llineEnd, colorname, width)

        return (llineStart, llineEnd, lline)

    def _rline(self, doc, width, colorname):
        rlineStart = self.cursor(0, 0)
        rlineStart.x = self.x_start + self.xm
        rlineStart.dx = self.xm * 3
        rlineStart.dy = self.ym * 2

        rlineEnd = self.cursor(0, 0)
        rlineEnd.x = self.x_start
        rlineEnd.dx = self.xm * 3
        rlineEnd.dy = self.ym * 2

        rline = self.get_line(doc, rlineStart, rlineEnd, colorname, width)
        return (rlineStart, rlineEnd, rline)

    def _hline_restart_y(self, x, hlineStart, hlineEnd):
        if (x & 1):
            hlineStart.y = self.y_start - self.ym
            hlineEnd.y = self.y_start - self.ym
        else:
            hlineStart.y = self.y_start - 2 * self.ym
            hlineEnd.y = self.y_start - 2 * self.ym

    def _lline_restart_y(self, x, llineStart, llineEnd):
        if (x & 1):
            llineStart.y = self.y_start - 2 * self.ym
            llineEnd.y = self.y_start - self.ym
        else:
            llineStart.y = self.y_start - self.ym
            llineEnd.y = self.y_start - 2 * self.ym

    def _rline_restart_y(self, x, rlineStart, rlineEnd):
        if (x & 1):
            rlineStart.y = self.y_start - 3 * self.ym
            rlineEnd.y = self.y_start - 2 * self.ym
        else:
            rlineStart.y = self.y_start - 2 * self.ym
            rlineEnd.y = self.y_start - 3 * self.ym


class PDFSectorMap(Map):
    def __init__(self, galaxy, routes):
        super(PDFSectorMap, self).__init__(galaxy, routes)
        self.lineStart = PDFCursor(0, 0)
        self.lineEnd = PDFCursor(0, 0)

    def document(self, sector):
        """
        Generated by the type of document
        """
        path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.pdf")
        self.writer = PDFLite(path)

        title = "Sector %s" % sector
        subject = "Trade route map generated by PyRoute for Traveller"
        author = None
        keywords = None
        creator = "PyPDFLite"
        self.writer.set_information(title, subject, author, keywords, creator)
        document = self.writer.get_document()
        document.set_margins(4)
        return document

    def close(self):
        self.writer.close()

    def cursor(self, x=0, y=0):
        return PDFCursor(x, y)

    def sector_name(self, doc, name):
        """
        Write name at the top of the document
        """
        cursor = PDFCursor(5, -5, True)
        def_font = doc.get_font()
        doc.set_font('times', size=30)
        width = doc.get_font()._string_width(name)
        cursor.x = 306 - (width / 2)
        doc.add_text(name, cursor)
        doc.set_font(font=def_font)

    def coreward_sector(self, pdf, name):
        cursor = PDFCursor(5, self.y_start - 15, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        width = pdf.get_font()._string_width(name) / 2
        cursor.x = 306 - width
        pdf.add_text(name, cursor)
        pdf.set_font(font=def_font)

    def rimward_sector(self, pdf, name):
        cursor = PDFCursor(306, 767, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.x_plus(-pdf.get_font()._string_width(name) / 2)
        pdf.add_text(name, cursor)
        pdf.set_font(font=def_font)

    def spinward_sector(self, pdf, name):
        cursor = PDFCursor(self.x_start - 5, 396, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.y_plus(pdf.get_font()._string_width(name) / 2)
        text = PDFText(pdf.session, pdf.page, None, cursor=cursor)
        text.text_rotate(90)
        text._text(name)
        pdf.set_font(font=def_font)

    def trailing_sector(self, pdf, name):
        cursor = PDFCursor(598, 396 - self.y_start, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.y_plus(-(pdf.get_font()._string_width(name) / 2))
        text = PDFText(pdf.session, pdf.page, None, cursor=cursor)
        text.text_rotate(-90)
        text._text(name)
        pdf.set_font(font=def_font)

    def add_line(self, pdf, start, end, colorname):
        """
        Add a line to the document, from start to end, in color
        """
        color = pdf.get_color()
        color.set_color_by_name(colorname)
        pdf.set_draw_color(color)
        pdf.add_line(cursor1=start, cursor2=end)

    def add_circle(self, pdf, center, radius, colorname):
        color = pdf.get_color()
        color.set_color_by_name(colorname)
        radius = PDFCursor(radius, radius)
        circle = PDFEllipse(pdf.session, pdf.page, center, radius, color, size=2)
        circle._draw()

    def get_line(self, doc, start, end, colorname, width):
        """
        Get a line draw method processor
        """
        color = doc.get_color()
        color.set_color_by_name(colorname)
        return PDFLine(doc.session, doc.page, start, end, stroke='solid', color=color, size=width)

    def place_system(self, pdf, star):
        def_font = pdf.get_font()
        pdf.set_font('times', size=4)

        col = (self.xm * 3 * (star.col))
        if (star.col & 1):
            row = (self.y_start - self.ym * 2) + (star.row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (star.row * self.ym * 2)

        point = PDFCursor(col, row)
        self.zone(pdf, star, point.copy())

        width = self.string_width(pdf.get_font(), star.uwp)
        point.y_plus(7)
        point.x_plus(self.ym - (width / 2))
        pdf.add_text(star.uwp.encode('ascii', 'replace'), point)

        if len(star.name) > 0:
            for chars in range(len(star.name), 0, -1):
                width = self.string_width(pdf.get_font(), star.name[:chars])
                if width <= self.xm * 3.5:
                    break
            point.y_plus(3.5)
            point.x = col
            point.x_plus(self.ym - (width / 2))
            pdf.add_text(star.name[:chars].encode('ascii', 'replace'), point)

        added = star.alg
        if 'Cp' in star.tradeCode:
            added += '+'
        elif 'Cx' in star.tradeCode or 'Cs' in star.tradeCode:
            added += '*'
        else:
            added += ' '

        added += '{:d}'.format(star.ggCount)
        point.y_plus(3.5)
        point.x = col
        width = pdf.get_font()._string_width(added)
        point.x_plus(self.ym - (width / 2))
        pdf.add_text(added, point)

        added = ''
        tradeIn = StatCalculation.trade_to_btn(star.tradeIn)
        tradeThrough = StatCalculation.trade_to_btn(star.tradeIn + star.tradeOver)

        if self.routes == 'trade':
            added += "{:X}{:X}{:X}{:d}".format(star.wtn, tradeIn, tradeThrough, star.starportSize)
        elif self.routes == 'comm':
            added += "{}{} {}".format(star.baseCode, star.ggCount, star.importance)
        elif self.routes == 'xroute':
            added += " {}".format(star.importance)
        width = pdf.get_font()._string_width(added)
        point.y_plus(3.5)
        point.x = col
        point.x_plus(self.ym - (width / 2))
        pdf.add_text(added, point)

        pdf.set_font(def_font)


class GraphicMap(Map):
    image_size = (612, 792)
    corePos = (image_size[0] / 2, 40)
    rimPos = (image_size[0] / 2, image_size[1] - 10)
    spinPos = (0, image_size[1] / 2)
    trailPos = (image_size[0] - 14, image_size[1] / 2)
    fillBlack = (0, 0, 0, 255)
    fillWhite = (255, 255, 255, 255)
    fillBlue = (50, 215, 255, 255)
    fillRed = (255, 48, 48, 255)

    def __init__(self, galaxy, routes):
        super(GraphicMap, self).__init__(galaxy, routes)
        self.titleFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 30)
        self.namesFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 10)
        self.textFill = GraphicMap.fillBlack

    def close(self):
        path = os.path.join(self.galaxy.output_path, self.sector.sector_name() + " Sector.png")
        self.image.save(path)

    def cursor(self, x=0, y=0):
        return Cursor(x, y)

    def add_line(self, doc, start, end, colorname):
        color = ImageColor.getrgb(colorname)
        doc.line([(start.x, start.y), (end.x, end.y)], color)

    def add_circle(self, doc, center, radius, colorname):
        color = ImageColor.getrgb(colorname)
        doc.ellipse([(center.x - radius, center.y - radius), (center.x + radius, center.y + radius)], outline=color)

    def get_line(self, doc, start, end, colorname, width):
        return GraphicLine(doc, start, end, colorname, width)

    def coreward_sector(self, doc, name):
        size = self.namesFont.getsize(name)
        pos = (self.corePos[0] - size[0] / 2, self.corePos[1] - size[1])
        doc.text(pos, name, font=self.namesFont, fill=self.textFill)

    def rimward_sector(self, doc, name):
        size = self.namesFont.getsize(name)
        pos = (self.rimPos[0] - size[0] / 2, self.rimPos[1] - size[1])
        doc.text(pos, name, font=self.namesFont, fill=self.textFill)

    def spinward_sector(self, doc, name):
        size = self.namesFont.getsize(name)
        size = (size[0], size[1] + 3)
        txt = Image.new('L', size, 0)
        d = ImageDraw.Draw(txt)
        d.text((0, 0), name, font=self.namesFont, fill=255)
        w = txt.rotate(90, expand=1)
        doc.bitmap((self.spinPos[0], self.spinPos[1] - w.size[1] / 2), w, fill=self.textFill)

    def trailing_sector(self, doc, name):
        size = self.namesFont.getsize(name)
        size = (size[0], size[1] + 3)
        txt = Image.new('L', size, 0)
        d = ImageDraw.Draw(txt)
        d.text((0, 0), name, font=self.namesFont, fill=255)
        w = txt.rotate(-90, expand=1)
        doc.bitmap((self.trailPos[0], self.trailPos[1] - w.size[1] / 2), w, fill=self.textFill)


class GraphicSectorMap(GraphicMap):
    def __init__(self, galaxy, routes):
        super(GraphicSectorMap, self).__init__(galaxy, routes)
        self.image_size = (612, 792)

    def document(self, sector):
        self.sector = sector
        self.image = Image.new("RGB", self.image_size, "white")
        return ImageDraw.Draw(self.image)

    def sector_name(self, doc, name):
        """
        Write name at the top of the document
        """
        # get a font
        size = self.titleFont.getsize(name)
        pos = (306 - size[0] / 2, 0)
        doc.text(pos, name, font=self.titleFont, fill=self.fillBlack)
