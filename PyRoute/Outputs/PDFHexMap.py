"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
import os

from reportlab.pdfgen.canvas import Canvas

from PyRoute.Position.Hex import Hex
from PyRoute.Outputs.SectorHexMap import SectorHexMap


class PDFHexMap(SectorHexMap):

    colourmap = {'gray': (128, 128, 128), 'salmon': (255, 140, 105), 'goldenrod': (218, 165, 32),
                 'crimson': (220, 20, 60)}

    def __init__(self, galaxy, routes, min_btn=8):
        super(PDFHexMap, self).__init__(galaxy, routes, min_btn)

    def write_sector_pdf_map(self, gal_sector, is_live=True):
        comm_routes, pdf_doc, worlds = self._setup_sector_pdf_map(gal_sector, is_live)
        pdf_doc.setLineWidth(1)
        self._sector_map_comm_and_trade_routes(comm_routes, pdf_doc, worlds)

        pdf_doc.setStrokeColorRGB(0, 0, 0)
        self._sector_map_systems_and_sectors(gal_sector, pdf_doc)
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
        # Save out whatever font is currently set
        font_leading, font_name, font_size = self._save_font(doc)
        new_font = 'Times-Roman'
        new_size = 30
        doc.setFont(new_font, size=new_size)
        width = doc.stringWidth(name, new_font, new_size)
        x = 306 - (width / 2)
        textobject = doc.beginText(x, 31)
        textobject.textOut(name)
        textobject.setStrokeColor('black')
        doc.drawText(textobject)
        # Restore saved font
        doc.setFont(font_name, font_size, font_leading)

    def coreward_sector(self, pdf, name):
        # Save out whatever font is currently set
        font_leading, font_name, font_size = self._save_font(pdf)

        new_font = 'Times-Roman'
        new_size = 10
        pdf.setFont(new_font, size=new_size)
        width = pdf.stringWidth(name, new_font, new_size)

        x = 306 - (width / 2)
        textobject = pdf.beginText(x, self.y_start - 3)
        textobject.textOut(name)
        textobject.setStrokeColor('black')
        pdf.drawText(textobject)
        # Restore saved font
        pdf.setFont(font_name, font_size, font_leading)

    def rimward_sector(self, pdf, name):
        # Save out whatever font is currently set
        font_leading, font_name, font_size = self._save_font(pdf)

        new_font = 'Times-Roman'
        new_size = 10
        pdf.setFont(new_font, size=new_size)
        # width = pdf.stringWidth(name, new_font, new_size)
        # x = 328 - (width/2)
        x = 306
        textobject = pdf.beginText(x, 779)
        textobject.textOut(name)
        textobject.setStrokeColor('black')
        pdf.drawText(textobject)
        # Restore saved font
        pdf.setFont(font_name, font_size, font_leading)

    def spinward_sector(self, pdf, name):
        # Save out whatever font is currently set
        font_leading, font_name, font_size = self._save_font(pdf)

        new_font = 'Times-Roman'
        new_size = 10
        pdf.setFont(new_font, size=new_size)
        width = pdf.stringWidth(name, new_font, new_size)
        y = 390 + (width / 2)
        x = self.x_start - 5

        textobject = pdf.beginText(x, y)
        textobject.setTextTransform(0, -1, 1, 0, x, y)
        textobject.textOut(name)
        textobject.setStrokeColor('black')
        pdf.drawText(textobject)

        # Restore saved font
        pdf.setFont(font_name, font_size, font_leading)

    def trailing_sector(self, pdf, name):
        # Save out whatever font is currently set
        font_leading, font_name, font_size = self._save_font(pdf)

        new_font = 'Times-Roman'
        new_size = 10
        pdf.setFont(new_font, size=new_size)
        width = pdf.stringWidth(name, new_font, new_size)
        y = 421 - (width / 2)
        x = 598

        textobject = pdf.beginText(x, y)
        textobject.setTextTransform(0, 1, -1, 0, x, y)
        textobject.textOut(name)
        textobject.setStrokeColor('black')
        pdf.drawText(textobject)

        # Restore saved font
        pdf.setFont(font_name, font_size, font_leading)

    def zone(self, doc, star, point):
        offset = 3
        point[0] += self.xm + offset
        point[1] += self.xm + offset

        if star.zone in ['R', 'F']:
            self.add_circle(doc, point, self.xm, 'crimson')
        elif star.zone in ['A', 'U']:
            self.add_circle(doc, point, self.xm, 'goldenrod')
        else:  # no zone -> do nothing
            return

    def subsector_grid(self, pdf: Canvas):
        pdf.setStrokeColorRGB(211 / 255.0, 211 / 255.0, 211 / 255.0)
        vlineStart = [0, self.y_start + self.xm]
        vlineEnd = [0, self.y_start + self.xm + (180 * 4)]
        for x in range(self.x_start, 595, 144):
            vlineStart[0] = x
            vlineEnd[0] = x
            pdf.line(vlineStart[0], vlineStart[1], vlineEnd[0], vlineEnd[1])

        hlineStart = [self.x_start, 0]
        hlineEnd = [591, 0]
        for y in range(self.y_start + self.xm, 780, 180):
            hlineStart[1] = y
            hlineEnd[1] = y
            pdf.line(hlineStart[0], hlineStart[1], hlineEnd[0], hlineEnd[1])

    def hex_grid(self, doc, draw, width, colorname='gray'):

        hlineStart, hlineEnd, hlineStartStep, hlineEndStep, colour = self._hline(doc, width, colorname)
        llineStart, llineEnd, llineStartStep, llineEndStep, colour = self._lline(doc, width, colorname)
        rlineStart, rlineEnd, rlineStartStep, rlineEndStep, colour = self._rline(doc, width, colorname)
        doc.setStrokeColorRGB(colour[0] / 256.0, colour[1] / 256.0, colour[2] / 256.0)
        doc.setLineWidth(width)

        for x in range(self.x_count):
            hlineStart[0] += hlineStartStep[0]
            hlineEnd[0] += hlineEndStep[0]
            self._hline_restart_y(x, hlineStart, hlineEnd)
            self._lline_restart_y(x, llineStart, llineEnd)
            self._rline_restart_y(x, rlineStart, rlineEnd)

            for y in range(self.y_count):
                hlineStart[1] += hlineStartStep[1]
                hlineEnd[1] += hlineEndStep[1]
                llineStart[1] += llineStartStep[1]
                llineEnd[1] += llineEndStep[1]
                rlineStart[1] += rlineStartStep[1]
                rlineEnd[1] += rlineEndStep[1]
                hline = (hlineStart, hlineEnd)
                lline = (llineStart, llineEnd)
                rline = (rlineStart, rlineEnd)

                draw(x, y, hline, lline, rline, doc, width, colour)

            llineStart[0] += llineStartStep[0]
            llineEnd[0] += llineEndStep[0]
            rlineStart[0] += rlineStartStep[0]
            rlineEnd[0] += rlineEndStep[0]

    def _draw_all(self, x, y, hline, lline, rline, pdf: Canvas, width, colour):
        if (x < self.x_count - 1):
            pdf.line(hline[0][0], hline[0][1], hline[1][0], hline[1][1])
        pdf.line(lline[0][0], lline[0][1], lline[1][0], lline[1][1])
        if (y > 0):
            pdf.line(rline[0][0], rline[0][1], rline[1][0], rline[1][1])

    def _draw_borders(self, x, y, hline, lline, rline, pdf: Canvas, width, colour):
        offset = Hex.dy_offset(y, (self.sector.dy // 40))
        q, r = Hex.hex_to_axial(x + (self.sector.dx), offset)

        border_val = self.galaxy.borders.borders_map.get((q, r), False)

        if border_val is not False:
            if border_val & Hex.BOTTOM:
                pdf.line(hline[0][0], hline[0][1], hline[1][0], hline[1][1])

            if border_val & Hex.BOTTOMRIGHT and y > 0:
                pdf.line(rline[0][0], rline[0][1], rline[1][0], rline[1][1])

            if border_val & Hex.BOTTOMLEFT:
                pdf.line(lline[0][0], lline[0][1], lline[1][0], lline[1][1])

    def _hline(self, pdf, width, colorname):
        hlineStart = [3, self.y_start - self.ym]
        hlineStartStep = (self.xm * 3, self.ym * 2)

        hlineEnd = [self.xm * 2.5, self.y_start - self.ym]
        hlineEndStep = (self.xm * 3, self.ym * 2)

        colour = self.colourmap[colorname]

        return hlineStart, hlineEnd, hlineStartStep, hlineEndStep, colour

    def _hline_restart_y(self, x, hlineStart, hlineEnd):
        if x & 1:
            hlineStart[1] = self.y_start - self.ym
            hlineEnd[1] = self.y_start - self.ym
        else:
            hlineStart[1] = self.y_start - 2 * self.ym
            hlineEnd[1] = self.y_start - 2 * self.ym

    def _lline(self, pdf, width, colorname):
        llineStart = [self.x_start, 0]
        llineStartStep = (self.xm * 3, self.ym * 2)

        llineEnd = [self.x_start + self.xm, 0]
        llineEndStep = (self.xm * 3, self.ym * 2)

        colour = self.colourmap[colorname]

        return llineStart, llineEnd, llineStartStep, llineEndStep, colour

    def _lline_restart_y(self, x, llineStart, llineEnd):
        if x & 1:
            llineStart[1] = self.y_start - 2 * self.ym
            llineEnd[1] = self.y_start - self.ym
        else:
            llineStart[1] = self.y_start - self.ym
            llineEnd[1] = self.y_start - 2 * self.ym

    def _rline(self, pdf, width, colorname):
        rlineStart = [self.x_start + self.xm, 0]
        rlineStartStep = (self.xm * 3, self.ym * 2)

        rlineEnd = [self.x_start, 0]
        rlineEndStep = (self.xm * 3, self.ym * 2)

        colour = self.colourmap[colorname]

        return rlineStart, rlineEnd, rlineStartStep, rlineEndStep, colour

    def _rline_restart_y(self, x, rlineStart, rlineEnd):
        if x & 1:
            rlineStart[1] = self.y_start - 3 * self.ym
            rlineEnd[1] = self.y_start - 2 * self.ym
        else:
            rlineStart[1] = self.y_start - 2 * self.ym
            rlineEnd[1] = self.y_start - 3 * self.ym

    def system(self, pdf, star):
        font_leading, font_name, font_size = self._save_font(pdf)

        new_font = 'Times-Roman'
        new_size = 4
        pdf.setFont(new_font, size=new_size)

        col = (self.xm * 3 * star.col)
        if star.col & 1:
            row = (self.y_start - self.ym * 2) + (star.row * self.ym * 2)
        else:
            row = (self.y_start - self.ym) + (star.row * self.ym * 2)

        point = [col, row]
        self.zone(pdf, star, point)
        rawpoint = [col, row]

        width = pdf.stringWidth(str(star.uwp), new_font, new_size)
        rawpoint[0] += self.ym - (width // 2)
        rawpoint[1] += 7
        textobject = pdf.beginText(rawpoint[0], rawpoint[1])
        textobject.textOut(str(star.uwp))
        pdf.drawText(textobject)

        if len(star.name) > 0:
            for chars in range(len(star.name), 0, -1):
                width = pdf.stringWidth(star.name[:chars], new_font, new_size)
                if width <= self.xm * 3.5:
                    break
            rawpoint[0] = col + self.ym - (width // 2)
            rawpoint[1] += 3.5
            textobject = pdf.beginText(rawpoint[0], rawpoint[1])
            textobject.textOut(star.name[:chars])
            pdf.drawText(textobject)

        added = star.alg_code
        if star.tradeCode.subsector_capital:
            added += '+'
        elif star.tradeCode.sector_capital or star.tradeCode.other_capital:
            added += '*'
        else:
            added += ' '

        added += '{:d}'.format(star.ggCount)
        rawpoint[0] = col
        rawpoint[1] += 3.5
        width = pdf.stringWidth(added)
        rawpoint[0] += self.ym - (width // 2)
        textobject = pdf.beginText(rawpoint[0], rawpoint[1])
        textobject.textOut(added)
        pdf.drawText(textobject)

        added = self._system_write_additional_data(star)
        width = pdf.stringWidth(added)
        rawpoint[0] = col + self.ym - (width // 2)
        rawpoint[1] += 3.5
        textobject = pdf.beginText(rawpoint[0], rawpoint[1])
        textobject.textOut(added)
        pdf.drawText(textobject)

        # Restore saved font
        pdf.setFont(font_name, font_size, font_leading)

    def trade_line(self, pdf, edge, data):

        end, start, tradeColor = self._trade_line_setup(data, edge)
        if tradeColor is None:
            return
        pdf.setStrokeColorRGB(tradeColor[0] / 255.0, tradeColor[1] / 255.0, tradeColor[2] / 255.0)
        pdf.setFillColorRGB(tradeColor[0] / 255.0, tradeColor[1] / 255.0, tradeColor[2] / 255.0)

        endCircle = end.sector == start.sector
        endx, endy, startx, starty = self._get_line_endpoints(end, start)

        pdf.line(startx, starty, endx, endy)

        pdf.ellipse(startx - 3, starty - 3, startx + 3, starty + 3, fill=1)

        if endCircle:
            pdf.ellipse(endx - 3, endy - 3, endx + 3, endy + 3, fill=1)
        pdf.setFillColorRGB(0, 0, 0)

    def comm_line(self, pdf, edge):
        start = edge[0]
        end = edge[1]

        pdf.setStrokeColorRGB(102 / 255.0, 178 / 255.0, 102 / 255.0)
        pdf.setLineWidth(3)

        endx, endy, startx, starty = self._get_line_endpoints(end, start)

        pdf.line(startx, starty, endx, endy)

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
        creator = "ReportLab"
        self.writer.setTitle(title)
        self.writer.setAuthor(author)
        self.writer.setSubject(subject)
        self.writer.setKeywords(keywords)
        self.writer.setCreator(creator)
        return self.writer

    def close(self):
        self.writer.showPage()
        self.writer.save()

    def cursor(self, x=0, y=0):
        raise NotImplementedError

    def add_line(self, pdf, start, end, colorname):
        """
        Add a line to the document, from start to end, in color
        """
        raise NotImplementedError

    def add_circle(self, pdf, center, radius, colorname):
        colour = PDFHexMap.colourmap[colorname]
        pdf.setStrokeColorRGB(colour[0] / 255.0, colour[1] / 255.0, colour[2] / 255.0)
        pdf.setLineWidth(2)

        startx = center[0]
        starty = center[1]
        pdf.ellipse(startx - radius, starty - radius, startx + radius, starty + radius, fill=0)

    def get_line(self, doc, start, end, colorname, width):
        """
        Get a line draw method processor
        """
        raise NotImplementedError

    def place_system(self, pdf, star):
        raise NotImplementedError

    @staticmethod
    def string_width(font, string):
        w = 0
        for i in string:
            w += font.character_widths.get(i, 600)
        return w * font.font_size / 1000.0

    @property
    def compression(self):
        if self.writer is None:
            return True
        return 'string' != self.writer._filename

    def _save_font(self, pdf):
        font_name = pdf._fontname
        font_size = pdf._fontsize
        font_leading = pdf._leading
        return font_leading, font_name, font_size
