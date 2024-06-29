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
from reportlab.pdfgen.canvas import Canvas

from PyRoute.Outputs.Map import Map
from PyRoute.StatCalculation import StatCalculation


class PDFHexMap(Map):

    colourmap = {'gray': (128, 128, 128), 'salmon': (255, 140, 105)}

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

        pdf_doc.setStrokeColorRGB(0, 0, 0)
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
        if is_live:
            return self.writer.save()
        return self.writer.getpdfdata()

    def write_base_map(self, pdf, sector):
        self.sector_name(pdf, sector.name)
        self.subsector_grid(pdf)
        self.hex_grid(pdf, self._draw_all, 0.5)

    def sector_name(self, doc: Canvas, name: str):
        """
        Write name at the top of the document
        """
        # cursor = PDFCursor(5, -5, True)
        # Save out whatever font is currently set
        font_name = doc._fontname
        font_size = doc._fontsize
        font_leading = doc._leading
        new_font = 'Times-Roman'
        new_size = 30
        doc.setFont(new_font, size=new_size)
        width = doc.stringWidth(name, new_font, new_size)
        x = 306 - (width / 2)
        textobject = doc.beginText(x, -5)
        textobject.textOut(name)
        textobject.setStrokeColor('black')
        doc.drawText(textobject)
        # Restore saved font
        doc.setFont(font_name, font_size, font_leading)

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

    def subsector_grid(self, pdf: Canvas):
        pdf.setStrokeColorRGB(211/255.0, 211/255.0, 211/255.0)
        #vlineStart = PDFCursor(0, self.y_start + self.xm)
        #vlineEnd = PDFCursor(0, self.y_start + self.xm + (180 * 4))
        vlineStart = [0, self.y_start + self.xm]
        vlineEnd = [0, self.y_start + self.xm + (180 * 4)]
        for x in range(self.x_start, 595, 144):
            vlineStart[0] = x
            vlineEnd[0] = x
            #pdf.add_line(cursor1=vlineStart, cursor2=vlineEnd)
            pdf.line(vlineStart[0], vlineStart[1], vlineEnd[0], vlineEnd[1])

        #hlineStart = PDFCursor(self.x_start, 0)
        #hlineEnd = PDFCursor(591, 0)
        hlineStart = [self.x_start, 0]
        hlineEnd = [591, 0]
        for y in range(self.y_start + self.xm, 780, 180):
            hlineStart[1] = y
            hlineEnd[1] = y
            #pdf.add_line(cursor1=hlineStart, cursor2=hlineEnd)
            pdf.line(hlineStart[0], hlineStart[1], hlineEnd[0], hlineEnd[1])

    def hex_grid(self, doc, draw, width, colorname='gray'):

        hlineStart, hlineEnd, hlineStartStep, hlineEndStep, colour = self._hline(doc, width, colorname)
        llineStart, llineEnd, llineStartStep, llineEndStep, colour = self._lline(doc, width, colorname)
        rlineStart, rlineEnd, rlineStartStep, rlineEndStep, colour = self._rline(doc, width, colorname)
        doc.setStrokeColorRGB(colour[0]/256.0, colour[1]/256.0, colour[2]/256.0)
        doc.setLineWidth(width)

        for x in range(self.x_count):
            #hlineStart.x_plus()
            hlineStart[0] += hlineStartStep[0]
            #hlineEnd.x_plus()
            hlineEnd[0] += hlineEndStep[0]
            self._hline_restart_y(x, hlineStart, hlineEnd)
            self._lline_restart_y(x, llineStart, llineEnd)
            self._rline_restart_y(x, rlineStart, rlineEnd)

            for y in range(self.y_count):
                #hlineStart.y_plus()
                hlineStart[1] += hlineStartStep[1]
                #hlineEnd.y_plus()
                hlineEnd[1] += hlineEndStep[1]
                #llineStart.y_plus()
                llineStart[1] += llineStartStep[1]
                #llineEnd.y_plus()
                llineEnd[1] += llineEndStep[1]
                #rlineStart.y_plus()
                rlineStart[1] += rlineStartStep[1]
                #rlineEnd.y_plus()
                rlineEnd[1] += rlineEndStep[1]
                hline = (hlineStart, hlineEnd)
                lline = (llineStart, llineEnd)
                rline = (rlineStart, rlineEnd)

                draw(x, y, hline, lline, rline, doc, width, colour)

            #llineStart.x_plus()
            llineStart[0] += llineStartStep[0]
            #llineEnd.x_plus()
            llineEnd[0] += llineEndStep[0]
            #rlineStart.x_plus()
            rlineStart[0] += rlineStartStep[0]
            #rlineEnd.x_plus()
            rlineEnd[0] += rlineEndStep[0]

    def _draw_all(self, x, y, hline, lline, rline, pdf: Canvas, width, colour):
        if (x < self.x_count - 1):
            #hline._draw()
            pdf.line(hline[0][0], hline[0][1], hline[1][0], hline[1][1])
        #lline._draw()
        pdf.line(lline[0][0], lline[0][1], lline[1][0], lline[1][1])
        if (y > 0):
            #rline._draw()
            pdf.line(rline[0][0], rline[0][1], rline[1][0], rline[1][1])

    def _draw_borders(self, x, y, hline, lline, rline, pdf: Canvas, width, colour):
        q, r = self.convert_hex_to_axial(x + self.sector.dx, y + self.sector.dy - 1)

        if self.galaxy.borders.borders.get((q, r), False):
            if self.galaxy.borders.borders[(q, r)] & 1:
                # hline._draw()
                pdf.line(hline[0][0], hline[0][1], hline[1][0], hline[1][1])

            if self.galaxy.borders.borders[(q, r)] & 2 and y > 0:
                # rline._draw()
                pdf.line(rline[0][0], rline[0][1], rline[1][0], rline[1][1])

            if self.galaxy.borders.borders[(q, r)] & 4:
                # lline._draw()
                pdf.line(lline[0][0], lline[0][1], lline[1][0], lline[1][1])

    def _hline(self, pdf, width, colorname):
        # dx/y are step sizen
        #hlineStart = PDFCursor(0, 0)
        #hlineStart.x = 3
        #hlineStart.y = self.y_start - self.ym
        #hlineStart.dx = self.xm * 3
        #hlineStart.dy = self.ym * 2

        hlineStart = [3, self.y_start - self.ym]
        hlineStartStep = (self.xm * 3, self.ym * 2)

        #hlineEnd = PDFCursor(0, 0)
        #hlineEnd.x = self.xm * 2.5
        #hlineEnd.y = self.y_start - self.ym
        #hlineEnd.dx = self.xm * 3
        #hlineEnd.dy = self.ym * 2

        hlineEnd = [self.xm * 2.5, self.y_start - self.ym]
        hlineEndStep = (self.xm * 3, self.ym * 2)

        colour = self.colourmap[colorname]
        #pdf.setStrokeColorRGB(colour[0], colour[1], colour[2])

        #hline = PDFLine(pdf.session, pdf.page, hlineStart, hlineEnd, stroke='solid', color=color, size=width)

        return hlineStart, hlineEnd, hlineStartStep, hlineEndStep, colour

    def _hline_restart_y(self, x, hlineStart, hlineEnd):
        if x & 1:
            hlineStart[1] = self.y_start - self.ym
            hlineEnd[1] = self.y_start - self.ym
        else:
            hlineStart[1] = self.y_start - 2 * self.ym
            hlineEnd[1] = self.y_start - 2 * self.ym

    def _lline(self, pdf, width, colorname):
        #llineStart = PDFCursor(-10, 0)
        #llineStart.x = self.x_start
        #llineStart.dx = self.xm * 3
        #llineStart.dy = self.ym * 2

        llineStart = [self.x_start, 0]
        llineStartStep = (self.xm * 3, self.ym * 2)

        #llineEnd = PDFCursor(-10, 0)
        #llineEnd.x = self.x_start + self.xm
        #llineEnd.dx = self.xm * 3
        #llineEnd.dy = self.ym * 2
        llineEnd = [self.x_start + self.xm, 0]
        llineEndStep = (self.xm * 3, self.ym * 2)

        #color = pdf.get_color()
        #color.set_color_by_name(colorname)
        colour = self.colourmap[colorname]

        #lline = PDFLine(pdf.session, pdf.page, llineStart, llineEnd, stroke='solid', color=color, size=width)

        return llineStart, llineEnd, llineStartStep, llineEndStep, colour

    def _lline_restart_y(self, x, llineStart, llineEnd):
        if x & 1:
            llineStart[1] = self.y_start - 2 * self.ym
            llineEnd[1] = self.y_start - self.ym
        else:
            llineStart[1] = self.y_start - self.ym
            llineEnd[1] = self.y_start - 2 * self.ym

    def _rline(self, pdf, width, colorname):
        rlineStart = PDFCursor(0, 0)
        rlineStart.x = self.x_start + self.xm
        rlineStart.dx = self.xm * 3
        rlineStart.dy = self.ym * 2

        rlineStart = [self.x_start + self.xm, 0]
        rlineStartStep = (self.xm * 3, self.ym * 2)

        rlineEnd = PDFCursor(0, 0)
        rlineEnd.x = self.x_start
        rlineEnd.dx = self.xm * 3
        rlineEnd.dy = self.ym * 2
        rlineEnd = [self.x_start, 0]
        rlineEndStep = (self.xm * 3, self.ym * 2)

        #color = pdf.get_color()
        #color.set_color_by_name(colorname)
        colour = self.colourmap[colorname]
        #rline = PDFLine(pdf.session, pdf.page, rlineStart, rlineEnd, stroke='solid', color=color, size=width)

        return rlineStart, rlineEnd, rlineStartStep, rlineEndStep, colour

    def _rline_restart_y(self, x, rlineStart, rlineEnd):
        if x & 1:
            rlineStart[1] = self.y_start - 3 * self.ym
            rlineEnd[1] = self.y_start - 2 * self.ym
        else:
            rlineStart[1] = self.y_start - 2 * self.ym
            rlineEnd[1] = self.y_start - 3 * self.ym

    def system(self, pdf, star):
        #def_font = pdf.get_font()
        font_name = pdf._fontname
        font_size = pdf._fontsize
        font_leading = pdf._leading

        new_font = 'Times-Roman'
        new_size = 4
        pdf.setFont(new_font, size=new_size)

        col = (self.xm * 3 * star.col)
        if star.col & 1:
            row = (self.y_start - self.ym * 2) + (star.row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (star.row * self.ym * 2)

        point = PDFCursor(col, row)
        self.zone(pdf, star, point.copy())
        rawpoint = [col, row]

        #width = self.string_width(pdf.get_font(), str(star.uwp))
        width = pdf.stringWidth(str(star.uwp), new_font, new_size)
        ##point.y_plus(7)
        #point.x_plus(self.ym - (width // 2))
        rawpoint[0] += self.ym - (width // 2)
        rawpoint[1] += 7
        textobject = pdf.beginText(rawpoint[0], rawpoint[1])
        textobject.textOut(str(star.uwp))
        pdf.drawText(textobject)
        #pdf.add_text(str(star.uwp), point)

        if len(star.name) > 0:
            for chars in range(len(star.name), 0, -1):
                #width = self.string_width(pdf.get_font(), star.name[:chars])
                width = pdf.stringWidth(star.name[:chars], new_font, new_size)
                if width <= self.xm * 3.5:
                    break
            #point.y_plus(3.5)
            #point.x = col
            #point.x_plus(self.ym - (width // 2))
            rawpoint[0] = col + self.ym - (width // 2)
            rawpoint[1] += 3.5
            textobject = pdf.beginText(rawpoint[0], rawpoint[1])
            textobject.textOut(star.name[:chars])
            pdf.drawText(textobject)
            #pdf.add_text(star.name[:chars], point)

        added = star.alg_code
        if star.tradeCode.subsector_capital:
            added += '+'
        elif star.tradeCode.sector_capital or star.tradeCode.other_capital:
            added += '*'
        else:
            added += ' '

        added += '{:d}'.format(star.ggCount)
        #point.y_plus(3.5)
        #point.x = col
        rawpoint[0] = col
        rawpoint[1] += 3.5
        #width = pdf.get_font()._string_width(added)
        width = pdf.stringWidth(added)
        # point.x_plus(self.ym - (width // 2))
        rawpoint[0] += self.ym - (width // 2)
        #pdf.add_text(added, point)
        textobject = pdf.beginText(rawpoint[0], rawpoint[1])
        textobject.textOut(added)
        pdf.drawText(textobject)

        added = ''
        tradeIn = StatCalculation.trade_to_btn(star.tradeIn)
        tradeThrough = StatCalculation.trade_to_btn(star.tradeIn + star.tradeOver)

        if self.routes == 'trade':
            added += "{:X}{:X}{:X}{:d}".format(star.wtn, tradeIn, tradeThrough, star.starportSize)
        elif self.routes == 'comm':
            added += "{}{} {}".format(star.baseCode, star.ggCount, star.importance)
        elif self.routes == 'xroute':
            added += " {}".format(star.importance)
        #width = pdf.get_font()._string_width(added)
        width = pdf.stringWidth(added)
        #point.y_plus(3.5)
        #point.x = col
        #point.x_plus(self.ym - (width // 2))
        rawpoint[0] = col + self.ym - (width // 2)
        rawpoint[1] += 3.5
        #pdf.add_text(added, point)
        textobject = pdf.beginText(rawpoint[0], rawpoint[1])
        textobject.textOut(added)
        pdf.drawText(textobject)

        #pdf.set_font(def_font)
        # Restore saved font
        pdf.setFont(font_name, font_size, font_leading)

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
        #color = pdf.get_color()
        #color.set_color_by_number(tradeColor[0], tradeColor[1], tradeColor[2])
        pdf.setStrokeColorRGB(tradeColor[0]/255.0, tradeColor[1]/255.0, tradeColor[2]/255.0)

        endCircle = end.sector == start.sector
        endx, endy, startx, starty = self._get_line_endpoints(end, start)

        lineStart = PDFCursor(startx, starty)
        lineEnd = PDFCursor(endx, endy)

        pdf.line(startx, starty, endx, endy)

        #line = PDFLine(pdf.session, pdf.page, lineStart, lineEnd, stroke='solid', color=color, size=1)
        #line._draw()

        #radius = PDFCursor(2, 2)
        #circle = PDFEllipse(pdf.session, pdf.page, lineStart, radius, color, size=3)
        #circle._draw()
        pdf.ellipse(startx - 2, starty - 2, startx + 2, starty + 2)

        if endCircle:
            #circle = PDFEllipse(pdf.session, pdf.page, lineEnd, radius, color, size=3)
            #circle._draw()
            pdf.ellipse(endx - 2, endy - 2, endx + 2, endy + 2)

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

    def document(self, sector, is_live: bool = True):
        """
        Generated by the type of document
        """
        path = os.path.join(self.galaxy.output_path, sector.sector_name() + " Sector.pdf")
        if not is_live:
            path = "string"
        self.writer = Canvas(path, pageCompression=(is_live is True), pdfVersion=(1, 7), bottomup=0, pagesize=[612, 792])

        title = "Sector %s" % sector
        subject = "Trade route map generated by PyRoute for Traveller"
        author = None
        keywords = None
        creator = "PyPDFLite"
        self.writer.setTitle(title)
        self.writer.setAuthor(author)
        self.writer.setSubject(subject)
        self.writer.setKeywords(keywords)
        self.writer.setCreator(creator)
        #document = self.writer.get_document()
        #document.set_margins(4)
        return self.writer

    def close(self):
        self.writer.showPage()
        self.writer.save()

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
