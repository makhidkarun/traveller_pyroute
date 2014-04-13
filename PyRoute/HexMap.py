'''
Created on Mar 8, 2014

@author: tjoneslo
'''
import math
import os
import logging
from pypdflite import PDFLite
from pypdflite import PDFCursor
from pypdflite.pdfobjects.pdfline import PDFLine
from pypdflite.pdfobjects.pdfellipse import PDFEllipse
from pypdflite.pdfobjects.pdftext import PDFText
from Galaxy import Sector
from Galaxy import Galaxy
from Star import Star


class HexMap(object):
    '''
    classdocs
    '''

    def __init__(self, galaxy, min_btn = 8):
        '''
        Constructor
        '''
        self.galaxy = galaxy
        self.ym = 9     # half a hex height
        self.xm = 6     # half the length of one side
        self.colorStart = 0
        self.min_btn = min_btn
        self.y_start = 43
        self.x_start = 15

    def write_maps(self):
        for sector in self.galaxy.sectors:
            if sector is None: continue
            pdf = self.document(sector)
            self.write_base_map(pdf, sector)
            
            self.draw_borders(pdf, sector)
            
            for (star, neighbor, data) in self.galaxy.stars.edges_iter(sector.worlds, True):
                if star.sector != sector:
                    continue
                # skip the longer routed edges added to speed up the A* Route
                if data.get('route', False): 
                    continue

                if data['trade'] > 0 and self.trade_to_btn(data['trade']) >= self.min_btn:
                    self.galaxy.stars[star][neighbor]['trade btn'] = self.trade_to_btn(data['trade'])
                    self.trade_line(pdf, [star, neighbor], data)
                elif star.sector != neighbor.sector:
                    data = self.galaxy.stars.get_edge_data(neighbor, star)
                    if data is not None and \
                        data['trade'] > 0 and \
                        self.trade_to_btn(data['trade']) >= self.min_btn:
                        self.trade_line(pdf, [star, neighbor], data)

            for star in sector.worlds:
                self.system(pdf, star)
            self.writer.close()
    
    def write_base_map(self, pdf, sector):
        self.sector_name(pdf, sector.name)
        if sector.coreward:
            self.coreward_sector(pdf, sector.coreward.name)
        if sector.rimward:
            self.rimward_sector(pdf, sector.rimward.name)
        if sector.spinward:
            self.spinward_sector(pdf, sector.spinward.name)
        if sector.trailing:
            self.trailing_sector(pdf, sector.trailing.name)
        self.subsector_grid(pdf)
        self.hex_grid(pdf, self._draw_all, 0.5)
        
    def sector_name(self,pdf,name):
        cursor = PDFCursor(5, 25, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=30)
        width = pdf.get_font()._string_width(name)
        cursor.x = 306-(width/2)
        pdf.add_text (name, cursor)
        pdf.set_font(font=def_font)


    def coreward_sector(self, pdf, name):
        cursor = PDFCursor(306, self.y_start - self.xm, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.x_plus(-pdf.get_font()._string_width(name)/2)
        pdf.add_text(name, cursor)
        pdf.set_font (font=def_font)

    def rimward_sector(self, pdf, name):
        cursor = PDFCursor(306 ,779, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.x_plus(-pdf.get_font()._string_width(name)/2)
        pdf.add_text(name, cursor)
        pdf.set_font (font=def_font)
        
    def spinward_sector(self, pdf, name):
        cursor = PDFCursor(self.x_start - 5, 390, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.y_plus(pdf.get_font()._string_width(name)/2)
        text = PDFText (pdf.session, pdf.page, None, cursor=cursor)
        text.text_rotate(90)
        text._text(name)
        pdf.set_font (font=def_font)
        
    def trailing_sector(self, pdf, name):
        cursor = PDFCursor(596, 390, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=10)
        cursor.y_plus(-(pdf.get_font()._string_width(name)/2))
        text = PDFText (pdf.session, pdf.page, None, cursor=cursor)
        text.text_rotate(-90)
        text._text(name)
        pdf.set_font (font=def_font)
        

    def subsector_grid(self, pdf):
        color = pdf.get_color()
        color.set_color_by_name('lightgray')
        pdf.set_draw_color(color)
        vlineStart = PDFCursor (0, self.y_start + self.xm)
        vlineEnd = PDFCursor (0, self.y_start + self.xm + (180 * 4))
        for x in xrange(self.x_start, 595, 144):
            vlineStart.x = x
            vlineEnd.x = x
            pdf.add_line(cursor1=vlineStart, cursor2=vlineEnd)
            
        hlineStart = PDFCursor(self.x_start,0)
        hlineEnd   = PDFCursor(591,0)
        for y in xrange(self.y_start + self.xm, 780, 180):
            hlineStart.y = y
            hlineEnd.y = y
            pdf.add_line(cursor1=hlineStart, cursor2=hlineEnd)


    def _hline(self, pdf, width, colorname):
        hlineStart = PDFCursor(0,0)
        hlineStart.x = 3
        hlineStart.y = self.y_start - self.ym
        hlineStart.dx = self.xm * 3
        hlineStart.dy = self.ym * 2

        hlineEnd   = PDFCursor(0,0)
        hlineEnd.x = self.xm * 2.5
        hlineEnd.y = self.y_start - self.ym
        hlineEnd.dx = self.xm * 3
        hlineEnd.dy = self.ym * 2

        color = pdf.get_color()
        color.set_color_by_name(colorname)
        
        hline = PDFLine(pdf.session, pdf.page, hlineStart, hlineEnd, style='solid', color=color, size=width)

        return (hlineStart, hlineEnd, hline)
    
    def _hline_restart_y(self, x,  hlineStart, hlineEnd):
        if (x & 1) :
            hlineStart.y = self.y_start - self.ym
            hlineEnd.y = self.y_start - self.ym
        else:
            hlineStart.y = self.y_start - 2 * self.ym
            hlineEnd.y = self.y_start - 2 * self.ym
            
    def _lline(self, pdf, width, colorname):
        llineStart = PDFCursor(-10,0)
        llineStart.x = self.x_start
        llineStart.dx = self.xm * 3
        llineStart.dy = self.ym * 2

        llineEnd   = PDFCursor(-10,0)
        llineEnd.x  = self.x_start + self.xm
        llineEnd.dx = self.xm * 3
        llineEnd.dy = self.ym * 2

        color = pdf.get_color()
        color.set_color_by_name(colorname)
        
        lline = PDFLine(pdf.session, pdf.page, llineStart, llineEnd, style='solid', color=color, size=width)
       
        return (llineStart, llineEnd, lline)

    def _lline_restart_y (self, x, llineStart, llineEnd):
        if (x & 1) :
            llineStart.y = self.y_start - 2 * self.ym
            llineEnd.y = self.y_start - self.ym
        else:
            llineStart.y = self.y_start - self.ym
            llineEnd.y = self.y_start - 2 * self.ym

    def _rline(self, pdf, width, colorname):
        rlineStart  = PDFCursor(0,0)
        rlineStart.x = self.x_start + self.xm
        rlineStart.dx = self.xm * 3
        rlineStart.dy = self.ym * 2
        rlineEnd    = PDFCursor(0,0)
        rlineEnd.x=self.x_start
        rlineEnd.dx = self.xm * 3
        rlineEnd.dy = self.ym * 2
        
        color = pdf.get_color()
        color.set_color_by_name(colorname)
        rline = PDFLine(pdf.session, pdf.page, rlineStart, rlineEnd, style='solid', color=color, size=width)

        return (rlineStart, rlineEnd, rline)

    def _rline_restart_y (self, x, rlineStart, rlineEnd):
        if (x & 1) :
            rlineStart.y = self.y_start - 3 *self.ym
            rlineEnd.y = self.y_start - 2 * self.ym
        else:
            rlineStart.y = self.y_start - 2 * self.ym
            rlineEnd.y = self.y_start - 3 * self.ym
    
    def hex_grid(self, pdf, draw, width, colorname = 'gray'):
        
        hlineStart, hlineEnd, hline = self._hline(pdf, width, colorname)
        llineStart, llineEnd, lline = self._lline(pdf, width, colorname)
        rlineStart, rlineEnd, rline = self._rline(pdf, width, colorname)
        
        for x in xrange (33):
            hlineStart.x_plus()
            hlineEnd.x_plus()
            self._hline_restart_y(x, hlineStart, hlineEnd)
            self._lline_restart_y(x, llineStart, llineEnd)
            self._rline_restart_y(x, rlineStart, rlineEnd)
            
            for y in xrange(41):
                hlineStart.y_plus()
                hlineEnd.y_plus()
                llineStart.y_plus()
                llineEnd.y_plus()
                rlineStart.y_plus()
                rlineEnd.y_plus()
                
                draw(x, y, hline, lline, rline)
                
            llineStart.x_plus()
            llineEnd.x_plus ()
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
        
        if self.galaxy.borders.borders.get((q,r), False):
            if self.galaxy.borders.borders[(q,r)] & 1:
                hline._draw()
                
            if self.galaxy.borders.borders[(q,r)] & 2 and y > 0:
                rline._draw()
                
            if self.galaxy.borders.borders[(q,r)] & 4:
                lline._draw()
           
    def draw_borders(self, pdf, sector):
        self.sector = sector
        self.hex_grid(pdf, self._draw_borders, 1.5, 'salmon')
        
    def convert_hex_to_axial(self, row, col):
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
            row = (self.y_start - self.ym) +  (star.row * self.ym * 2)
             
        point = PDFCursor(col, row)
        self.zone(pdf, star, point.copy())
        
        width = self.string_width(pdf.get_font(), star.uwp)
        point.y_plus(4)
        point.x_plus(self.ym -(width/2))
        pdf.add_text (star.uwp.encode('ascii', 'replace'), point)
        
        width = self.string_width(pdf.get_font(), star.name)
        point.y_plus(6)
        point.x = col
        point.x_plus(self.ym - (width/2))
        pdf.add_text(star.name.encode('ascii', 'replace'), point)
        
        added = star.alg
        if ('Cp' in star.tradeCode):
            added += '+'
        elif ('Cx' in star.tradeCode):
            added += '*'
        else:
            added += ' '
            
        tradeIn = self.trade_to_btn(star.tradeIn)
        tradeOver = self.trade_to_btn(star.tradeOver)
        added += "{0}{1:d}{2:X}{3:X}{4:X}".format(star.baseCode, star.ggCount, star.wtn, tradeIn, tradeOver)

        width = pdf.get_font()._string_width(added)
        point.y_plus(6)
        point.x = col
        point.x_plus(self.ym - (width/2))
        pdf.add_text(added, point)
        
        pdf.set_font(def_font)
        
    def trade_line(self, pdf, edge, data):
        
        tradeColors = ['red','yellow', 'green', 'cyan', 'blue', 'purple', 'violet' ]
        start = edge[0]
        end = edge[1]

        trade = self.trade_to_btn(data['trade']) - self.min_btn
        if trade < 0: 
            continue
        if trade > 6:
            logging.getLogger('PyRoute.HexMap').warn("trade calculated over %d" % self.min_btn + 6)
            trade = 6
            
        tradeColor = tradeColors[trade]

        starty = self.y_start + ( self.ym * 2 * (start.row)) - (self.ym * (1 if start.col & 1 else 0))
        lineStart = PDFCursor ((self.xm * 3 * (start.col)) + self.ym, starty)

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
            
        endy   = self.y_start + ( self.ym * 2 * (endRow)) - (self.ym * (1 if endCol & 1 else 0))
        lineEnd = PDFCursor ((self.xm * 3 * (endCol)) + self.ym, endy)
        color = pdf.get_color()
        color.set_color_by_name(tradeColor)
        line = PDFLine(pdf.session, pdf.page, lineStart, lineEnd, style='solid', color=color, size=1)
        line._draw()
                        
    def zone(self,pdf, star, point):
        point.x_plus(self.ym)
        point.y_plus(self.ym)
        color = pdf.get_color()
        if star.zone in ['R', 'F']:
            color.set_color_by_name('crimson')
        elif star.zone in ['A', 'U'] :
            color.set_color_by_name('goldenrod')
        else: # no zone -> do nothing
            return
        
        radius = PDFCursor(self.xm, self.xm)
        
        circle = PDFEllipse(pdf.session, pdf.page, point, radius, color, size=2)
        circle._draw()
        
    
    def document(self, sector):
        path = os.path.join(self.galaxy.output_path, sector.name+".pdf")
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
        
    def string_width(self, font, string):
        #pdf.get_font()._string_width(star.uwp)
        w = 0
        for i in string:
            w += font.character_widths[i] if i in font.character_widths else 600
        return w * font.font_size / 1000.0
      
    def trade_to_btn(self, trade):
        if trade == 0:
            return 0
        return int(math.log(trade,10))
    
        
if __name__ == '__main__':
    sector = Sector('# Core', '# 0,0')
    hexMap = HexMap(None)
    pdf = hexMap.document(sector)
    hexMap.write_base_map (pdf, sector)
    
    galaxy = Galaxy (0,0)
    
    star1 = Star("0102 Shana Ma             E551112-7 Lo Po                { -3 } (300-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                 galaxy.starline, 0, 0)
    star2 = Star("0405 Azimuth              B847427-B Ni Pa                { 1 }  (634+1) [455B] Bc    N - 200 13 Im M2 V M7 V      ",
                 galaxy.starline, 0, 0)
    hexMap.trade_line(pdf, [star1,star2])
    hexMap.system(pdf, star1)
    hexMap.system(pdf, star2)
    
    hexMap.writer.close()
