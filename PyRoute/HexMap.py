"""
Created on Mar 8, 2014

@author: tjoneslo
"""
import os
import logging
from pypdflite import PDFLite
from pypdflite import PDFCursor
from pypdflite.pdfobjects.pdfline import PDFLine
from pypdflite.pdfobjects.pdfellipse import PDFEllipse
from pypdflite.pdfobjects.pdftext import PDFText
from Galaxy import Sector, Galaxy
from Star import Star
from StatCalculation import StatCalculation


class HexMap(object):
    """
    Draw the trade routes as calculated, sector by sector onto PDF files.
    Used pypdflite to directly generate the PDF files.
    """

    def __init__(self, galaxy, routes, min_btn=8):
        self.galaxy = galaxy
        self.routes = routes
        self.ym = 9  # half a hex height
        self.xm = 6  # half the length of one side
        self.colorStart = 0
        self.min_btn = min_btn
        self.y_start = 43
        self.x_start = 15

    def write_maps(self):
        """
        Starting point for writing PDF files.
        Call this to output the trade maps
        """
        logging.getLogger("PyRoute.HexMap").info("writing {:d} sector maps...".format(len(self.galaxy.sectors)))
        for sector in self.galaxy.sectors.values():
            pdf = self.document(sector)
            self.write_base_map(pdf, sector)

            self.draw_borders(pdf, sector)

            comm_routes = [star for star in self.galaxy.stars.edges(sector.worlds, True) \
                           if star[2].get('xboat', False) or star[2].get('comm', False)]
            for (star, neighbor, data) in comm_routes:
                self.comm_line(pdf, [star, neighbor])

            sector_trade = [star for star in self.galaxy.stars.edges(sector.worlds, True) \
                            if star[2]['trade'] > 0 and StatCalculation.trade_to_btn(star[2]['trade']) >= self.min_btn]

            logging.getLogger('PyRoute.HexMap').debug("Worlds with trade: {}".format(len(sector_trade)))

            sector_trade.sort(key=lambda line: line[2]['trade'])

            for (star, neighbor, data) in sector_trade:
                self.galaxy.stars[star][neighbor]['trade btn'] = StatCalculation.trade_to_btn(data['trade'])
                self.trade_line(pdf, [star, neighbor], data)

            # Get all the worlds in this sector
            # for (star, neighbor, data) in self.galaxy.stars.edges(sector.worlds, True):
            #    if star.sector != sector:
            #        continue#
            #    if data['trade'] > 0 and self.trade_to_btn(data['trade']) >= self.min_btn:
            #        self.galaxy.stars[star][neighbor]['trade btn'] = self.trade_to_btn(data['trade'])
            #        self.trade_line(pdf, [star, neighbor], data)
            #    elif star.sector != neighbor.sector:
            #        data = self.galaxy.stars.get_edge_data(neighbor, star)
            #        if data is not None and \
            #            data['trade'] > 0 and \
            #            self.trade_to_btn(data['trade']) >= self.min_btn:
            #            self.trade_line(pdf, [star, neighbor], data)

            for star in sector.worlds:
                self.system(pdf, star)
            if sector.coreward:
                self.coreward_sector(pdf, sector.coreward.name)
            if sector.rimward:
                self.rimward_sector(pdf, sector.rimward.name)
            if sector.spinward:
                self.spinward_sector(pdf, sector.spinward.name)
            if sector.trailing:
                self.trailing_sector(pdf, sector.trailing.name)

            self.writer.close()

    def write_base_map(self, pdf, sector):
        self.sector_name(pdf, sector.name)
        self.subsector_grid(pdf)
        self.hex_grid(pdf, self._draw_all, 0.5)

    def sector_name(self, pdf, name):
        cursor = PDFCursor(5, -5, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=30)
        width = pdf.get_font()._string_width(name)
        cursor.x = 306 - (width / 2)
        pdf.add_text(name, cursor)
        pdf.set_font(font=def_font)

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
        cursor = PDFCursor(self.x_start - 5, 390, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.y_plus(pdf.get_font()._string_width(name) / 2)
        text = PDFText(pdf.session, pdf.page, None, cursor=cursor)
        text.text_rotate(90)
        text._text(name)
        pdf.set_font(font=def_font)

    def trailing_sector(self, pdf, name):
        cursor = PDFCursor(598, 390, True)
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

        return (hlineStart, hlineEnd, hline)

    def _hline_restart_y(self, x, hlineStart, hlineEnd):
        if (x & 1):
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

        return (llineStart, llineEnd, lline)

    def _lline_restart_y(self, x, llineStart, llineEnd):
        if (x & 1):
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

        return (rlineStart, rlineEnd, rline)

    def _rline_restart_y(self, x, rlineStart, rlineEnd):
        if (x & 1):
            rlineStart.y = self.y_start - 3 * self.ym
            rlineEnd.y = self.y_start - 2 * self.ym
        else:
            rlineStart.y = self.y_start - 2 * self.ym
            rlineEnd.y = self.y_start - 3 * self.ym

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

    def _draw_all(self, x, y, hline, lline, rline):
        if (x < 32):
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
        self.sector = sector
        self.hex_grid(pdf, self._draw_borders, 1.5, 'salmon')

    @staticmethod
    def convert_hex_to_axial(row, col):
        x = row
        z = col - (row - (row & 1)) / 2
        return (x, z)

    def system(self, pdf, star):
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
        point.x_plus(self.ym - (width // 2))
        pdf.add_text(star.uwp, point)

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

        starty = self.y_start + (self.ym * 2 * (start.row)) - (self.ym * (1 if start.col & 1 else 0))
        startx = (self.xm * 3 * (start.col)) + self.ym

        endRow = end.row
        endCol = end.col
        endCircle = True
        if (end.sector != start.sector):
            endCircle = False
            if end.sector.x < start.sector.x:
                endCol -= 32
            if end.sector.x > start.sector.x:
                endCol += 32
            if end.sector.y < start.sector.y:
                endRow -= 40
            if end.sector.y > start.sector.y:
                endRow += 40
            endy = self.y_start + (self.ym * 2 * (endRow)) - (self.ym * (1 if endCol & 1 else 0))
            endx = (self.xm * 3 * endCol) + self.ym

            (startx, starty), (endx, endy) = self.clipping(startx, starty, endx, endy)

        else:
            endy = self.y_start + (self.ym * 2 * (endRow)) - (self.ym * (1 if endCol & 1 else 0))
            endx = (self.xm * 3 * endCol) + self.ym

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

        starty = self.y_start + (self.ym * 2 * (start.row)) - (self.ym * (1 if start.col & 1 else 0))
        startx = (self.xm * 3 * (start.col)) + self.ym

        endRow = end.row
        endCol = end.col
        if (end.sector != start.sector):
            if end.sector.x < start.sector.x:
                endCol -= 32
            if end.sector.x > start.sector.x:
                endCol += 32
            if end.sector.y < start.sector.y:
                endRow -= 40
            if end.sector.y > start.sector.y:
                endRow += 40
            endy = self.y_start + (self.ym * 2 * (endRow)) - (self.ym * (1 if endCol & 1 else 0))
            endx = (self.xm * 3 * endCol) + self.ym

            (startx, starty), (endx, endy) = self.clipping(startx, starty, endx, endy)

        else:
            endy = self.y_start + (self.ym * 2 * (endRow)) - (self.ym * (1 if endCol & 1 else 0))
            endx = (self.xm * 3 * endCol) + self.ym

        lineStart = PDFCursor(startx, starty)
        lineEnd = PDFCursor(endx, endy)

        line = PDFLine(pdf.session, pdf.page, lineStart, lineEnd, stroke='solid', color=color, size=3)
        line._draw()

    def zone(self, pdf, star, point):
        point.x_plus(self.ym)
        point.y_plus(self.ym)
        color = pdf.get_color()
        if star.zone in ['R', 'F']:
            color.set_color_by_name('crimson')
        elif star.zone in ['A', 'U']:
            color.set_color_by_name('goldenrod')
        else:  # no zone -> do nothing
            return

        radius = PDFCursor(self.xm, self.xm)

        circle = PDFEllipse(pdf.session, pdf.page, point, radius, color, size=2)
        circle._draw()

    def document(self, sector):
        path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.pdf")
        self.writer = PDFLite(path)

        title = "Sector %s" % sector
        subject = "Trade route map generated by PyRoute for Traveller"
        author = None
        keywords = None
        creator = "PyPDFLite"
        self.writer.set_information(title, subject, author, keywords, creator)
        self.writer.set_compression(True)
        document = self.writer.get_document()
        document.set_margins(4)
        return document

    @staticmethod
    def string_width(font, string):
        w = 0
        for i in string:
            w += font.character_widths[i] if i in font.character_widths else 600
        return w * font.font_size / 1000.0

    def clipping(self, startx, starty, endx, endy):
        points_t = [0.0, 1.0]
        line_pt_1 = [startx, starty]
        line_pt_2 = [endx, endy]

        if startx == endx:
            if starty > endy:
                return ((startx, min(max(starty, endy), 780)),
                        (startx, max(min(starty, endy), 42)))
            else:
                return ((startx, max(min(starty, endy), 42)),
                        (startx, min(max(starty, endy), 780)))

        if starty == endy:
            if startx > endx:
                return ((min(max(startx, endx), 600), starty),
                        (max(min(startx, endx), 15), starty))
            else:
                return ((max(min(startx, endx), 15), starty),
                        (min(max(startx, endx), 600), starty))

        points_t.append(float(15 - startx) / (endx - startx))
        points_t.append(float(600 - startx) / (endx - startx))
        points_t.append(float(780 - starty) / (endy - starty))
        points_t.append(float(42 - starty) / (endy - starty))

        points_t.sort()
        result = [(pt_1 + t * (pt_2 - pt_1)) for t in (points_t[2], points_t[3]) for (pt_1, pt_2) in
                  zip(line_pt_1, line_pt_2)]
        logging.getLogger("PyRoute.HexMap").debug(result)
        return (result[0], result[1]), (result[2], result[3])


if __name__ == '__main__':
    sector = Sector('# Core', '# 0,0')
    hexMap = HexMap(None)
    pdf = hexMap.document(sector)
    hexMap.write_base_map(pdf, sector)

    galaxy = Galaxy(0, 0)

    star1 = Star(
        "0102 Shana Ma             E551112-7 Lo Po                { -3 } (300-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
        galaxy.starline, 0, 0)
    star2 = Star(
        "0405 Azimuth              B847427-B Ni Pa                { 1 }  (634+1) [455B] Bc    N - 200 13 Im M2 V M7 V      ",
        galaxy.starline, 0, 0)
    hexMap.trade_line(pdf, [star1, star2])
    hexMap.system(pdf, star1)
    hexMap.system(pdf, star2)

    hexMap.writer.close()
