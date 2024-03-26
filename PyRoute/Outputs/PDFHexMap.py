"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
import os
import logging

from pypdflite import PDFCursor, PDFLite
from pypdflite.pdfobjects.pdfellipse import PDFEllipse
from pypdflite.pdfobjects.pdfline import PDFLine
from pypdflite.pdfobjects.pdftext import PDFText

from PyRoute.Outputs.Map import Map
from PyRoute.StatCalculation import StatCalculation


class PDFHexMap(Map):
    def __init__(self, galaxy, routes, min_btn=8):
        super(PDFHexMap, self).__init__(galaxy, routes)
        self.lineStart = PDFCursor(0, 0)
        self.lineEnd = PDFCursor(0, 0)
        self.min_btn = min_btn
        self.writer = None

    def write_sector_pdf_map(self, gal_sector, is_live=True):
        pdf_doc = self.document(gal_sector, is_live)
        self.write_base_map(pdf_doc, gal_sector)
        self.draw_borders(pdf_doc, gal_sector)
        worlds = [item.index for item in gal_sector.worlds]
        comm_routes = [star for star in self.galaxy.stars.edges(worlds, True)
                       if star[2].get('xboat', False) or star[2].get('comm', False)]
        for (star, neighbor, data) in comm_routes:
            srcstar = self.galaxy.star_mapping[star]
            trgstar = self.galaxy.star_mapping[neighbor]
            self.comm_line(pdf_doc, [srcstar, trgstar])
        sector_trade = [star for star in self.galaxy.stars.edges(worlds, True)
                        if star[2]['trade'] > 0 and StatCalculation.trade_to_btn(star[2]['trade']) >= self.min_btn]
        logging.getLogger('PyRoute.HexMap').debug("Worlds with trade: {}".format(len(sector_trade)))
        sector_trade.sort(key=lambda line: line[2]['trade'])
        for (star, neighbor, data) in sector_trade:
            self.galaxy.stars[star][neighbor]['trade btn'] = StatCalculation.trade_to_btn(data['trade'])
            srcstar = self.galaxy.star_mapping[star]
            trgstar = self.galaxy.star_mapping[neighbor]
            self.trade_line(pdf_doc, [srcstar, trgstar], data)

        for star in gal_sector.worlds:
            self.system(pdf_doc, star)
        if gal_sector.coreward:
            self.coreward_sector(pdf_doc, gal_sector.coreward.name)
        if gal_sector.rimward:
            self.rimward_sector(pdf_doc, gal_sector.rimward.name)
        if gal_sector.spinward:
            self.spinward_sector(pdf_doc, gal_sector.spinward.name)
        if gal_sector.trailing:
            self.trailing_sector(pdf_doc, gal_sector.trailing.name)
        return self.writer.close()

    def write_base_map(self, pdf, sector):
        self.sector_name(pdf, sector.name)
        self.subsector_grid(pdf)
        self.hex_grid(pdf, self._draw_all, 0.5)

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

    def subsector_grid(self, pdf):
        color = pdf.get_color()
        color.set_color_by_name('lightgray')
        pdf.set_draw_color(color)
        vlineStart = PDFCursor(0, self.y_start + self.xm)
        vlineEnd = PDFCursor(0, self.y_start + self.xm + (180 * 4))
        for x in range(self.x_start, 595, 144):
            vlineStart.x = x
            vlineEnd.x = x
            pdf.add_line(cursor1=vlineStart, cursor2=vlineEnd)

        hlineStart = PDFCursor(self.x_start, 0)
        hlineEnd = PDFCursor(591, 0)
        for y in range(self.y_start + self.xm, 780, 180):
            hlineStart.y = y
            hlineEnd.y = y
            pdf.add_line(cursor1=hlineStart, cursor2=hlineEnd)

    def _hline(self, pdf, width, colorname):
        hlineStart = PDFCursor(0, 0)
        hlineStart.x = 3
        hlineStart.y = self.y_start - self.ym
        hlineStart.dx = self.xm * 3
        hlineStart.dy = self.ym * 2

        hlineEnd = PDFCursor(0, 0)
        hlineEnd.x = self.xm * 2.5
        hlineEnd.y = self.y_start - self.ym
        hlineEnd.dx = self.xm * 3
        hlineEnd.dy = self.ym * 2

        color = pdf.get_color()
        color.set_color_by_name(colorname)

        hline = PDFLine(pdf.session, pdf.page, hlineStart, hlineEnd, stroke='solid', color=color, size=width)

        return hlineStart, hlineEnd, hline

    def _hline_restart_y(self, x, hlineStart, hlineEnd):
        if x & 1:
            hlineStart.y = self.y_start - self.ym
            hlineEnd.y = self.y_start - self.ym
        else:
            hlineStart.y = self.y_start - 2 * self.ym
            hlineEnd.y = self.y_start - 2 * self.ym

    def _lline(self, pdf, width, colorname):
        llineStart = PDFCursor(-10, 0)
        llineStart.x = self.x_start
        llineStart.dx = self.xm * 3
        llineStart.dy = self.ym * 2

        llineEnd = PDFCursor(-10, 0)
        llineEnd.x = self.x_start + self.xm
        llineEnd.dx = self.xm * 3
        llineEnd.dy = self.ym * 2

        color = pdf.get_color()
        color.set_color_by_name(colorname)

        lline = PDFLine(pdf.session, pdf.page, llineStart, llineEnd, stroke='solid', color=color, size=width)

        return llineStart, llineEnd, lline

    def _lline_restart_y(self, x, llineStart, llineEnd):
        if x & 1:
            llineStart.y = self.y_start - 2 * self.ym
            llineEnd.y = self.y_start - self.ym
        else:
            llineStart.y = self.y_start - self.ym
            llineEnd.y = self.y_start - 2 * self.ym

    def _rline(self, pdf, width, colorname):
        rlineStart = PDFCursor(0, 0)
        rlineStart.x = self.x_start + self.xm
        rlineStart.dx = self.xm * 3
        rlineStart.dy = self.ym * 2
        rlineEnd = PDFCursor(0, 0)
        rlineEnd.x = self.x_start
        rlineEnd.dx = self.xm * 3
        rlineEnd.dy = self.ym * 2

        color = pdf.get_color()
        color.set_color_by_name(colorname)
        rline = PDFLine(pdf.session, pdf.page, rlineStart, rlineEnd, stroke='solid', color=color, size=width)

        return rlineStart, rlineEnd, rline

    def _rline_restart_y(self, x, rlineStart, rlineEnd):
        if x & 1:
            rlineStart.y = self.y_start - 3 * self.ym
            rlineEnd.y = self.y_start - 2 * self.ym
        else:
            rlineStart.y = self.y_start - 2 * self.ym
            rlineEnd.y = self.y_start - 3 * self.ym

    def system(self, pdf, star):
        def_font = pdf.get_font()
        pdf.set_font('times', size=4)

        col = (self.xm * 3 * star.col)
        if star.col & 1:
            row = (self.y_start - self.ym * 2) + (star.row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (star.row * self.ym * 2)

        point = PDFCursor(col, row)
        self.zone(pdf, star, point.copy())

        width = self.string_width(pdf.get_font(), str(star.uwp))
        point.y_plus(7)
        point.x_plus(self.ym - (width // 2))
        pdf.add_text(str(star.uwp), point)

        if len(star.name) > 0:
            for chars in range(len(star.name), 0, -1):
                width = self.string_width(pdf.get_font(), star.name[:chars])
                if width <= self.xm * 3.5:
                    break
            point.y_plus(3.5)
            point.x = col
            point.x_plus(self.ym - (width // 2))
            pdf.add_text(star.name[:chars], point)

        added = star.alg_code
        if star.tradeCode.subsector_capital:
            added += '+'
        elif star.tradeCode.sector_capital or star.tradeCode.other_capital:
            added += '*'
        else:
            added += ' '

        added += '{:d}'.format(star.ggCount)
        point.y_plus(3.5)
        point.x = col
        width = pdf.get_font()._string_width(added)
        point.x_plus(self.ym - (width // 2))
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
        point.x_plus(self.ym - (width // 2))
        pdf.add_text(added, point)

        pdf.set_font(def_font)

    def trade_line(self, pdf, edge, data):

        tradeColors = [(255, 0, 0),  # Red
                       (224, 224, 16),  # yellow - darker
                       (0, 255, 0),  # green
                       (0, 255, 255),  # Cyan
                       (96, 96, 255),  # blue - lighter
                       (128, 0, 128),  # purple
                       (148, 0, 211),  # violet
                       ]

        start = edge[0]
        end = edge[1]

        trade = StatCalculation.trade_to_btn(data['trade']) - self.min_btn
        if trade < 0:
            return
        if trade > 6:
            logging.getLogger('PyRoute.HexMap').warn("trade calculated over %d" % self.min_btn + 6)
            trade = 6

        tradeColor = tradeColors[trade]
        color = pdf.get_color()
        color.set_color_by_number(tradeColor[0], tradeColor[1], tradeColor[2])

        endCircle = end.sector == start.sector
        endx, endy, startx, starty = self._get_line_endpoints(end, start)

        lineStart = PDFCursor(startx, starty)
        lineEnd = PDFCursor(endx, endy)

        line = PDFLine(pdf.session, pdf.page, lineStart, lineEnd, stroke='solid', color=color, size=1)
        line._draw()

        radius = PDFCursor(2, 2)
        circle = PDFEllipse(pdf.session, pdf.page, lineStart, radius, color, size=3)
        circle._draw()

        if endCircle:
            circle = PDFEllipse(pdf.session, pdf.page, lineEnd, radius, color, size=3)
            circle._draw()

    def comm_line(self, pdf, edge):
        start = edge[0]
        end = edge[1]
        color = pdf.get_color()
        color.set_color_by_number(102, 178, 102)

        endx, endy, startx, starty = self._get_line_endpoints(end, start)

        lineStart = PDFCursor(startx, starty)
        lineEnd = PDFCursor(endx, endy)

        line = PDFLine(pdf.session, pdf.page, lineStart, lineEnd, stroke='solid', color=color, size=3)
        line._draw()

    def _get_line_endpoints(self, end, start):
        starty = self.y_start + (self.ym * 2 * start.row) - (self.ym * (1 if start.col & 1 else 0))
        startx = (self.xm * 3 * start.col) + self.ym
        endRow = end.row
        endCol = end.col
        if end.sector != start.sector:
            up = False
            down = False
            if end.sector.x < start.sector.x:
                endCol -= 32
            if end.sector.x > start.sector.x:
                endCol += 32
            if end.sector.y > start.sector.y:
                endRow -= 40
                up = True
            if end.sector.y < start.sector.y:
                endRow += 40
                down = True
            endy = self.y_start + (self.ym * 2 * endRow) - (self.ym * (1 if endCol & 1 else 0))
            endx = (self.xm * 3 * endCol) + self.ym

            (startx, starty), (endx, endy) = self.clipping(startx, starty, endx, endy)
            if up:
                assert starty >= endy, "Misaligned to-coreward trade segment between " + str(start) + " and " + str(end)
            if down:
                assert starty <= endy, "Misaligned to-rimward trade segment between " + str(start) + " and " + str(end)

        else:
            endy = self.y_start + (self.ym * 2 * endRow) - (self.ym * (1 if endCol & 1 else 0))
            endx = (self.xm * 3 * endCol) + self.ym
        return endx, endy, startx, starty

    def document(self, sector, is_live=True):
        """
        Generated by the type of document
        """
        path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.pdf")
        if not is_live:
            path = "string"
        self.writer = PDFLite(path)

        title = "Sector %s" % sector
        subject = "Trade route map generated by PyRoute for Traveller"
        author = None
        keywords = None
        creator = "PyPDFLite"
        self.writer.set_information(title, subject, author, keywords, creator)
        self.writer.set_compression(is_live)
        document = self.writer.get_document()
        document.set_margins(4)
        return document

    def close(self):
        self.writer.close()

    def cursor(self, x=0, y=0):
        return PDFCursor(x, y)

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

        col = (self.xm * 3 * star.col)
        if star.col & 1:
            row = (self.y_start - self.ym * 2) + (star.row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (star.row * self.ym * 2)

        point = PDFCursor(col, row)
        self.zone(pdf, star, point.copy())

        width = self.string_width(pdf.get_font(), str(star.uwp))
        point.y_plus(7)
        point.x_plus(self.ym - (width / 2))
        pdf.add_text(str(star.uwp).encode('ascii', 'replace'), point)

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

    @staticmethod
    def string_width(font, string):
        w = 0
        for i in string:
            w += font.character_widths[i] if i in font.character_widths else 600
        return w * font.font_size / 1000.0

    @property
    def compression(self):
        return self.writer.session.compression
