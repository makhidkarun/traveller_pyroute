'''
Created on Mar 8, 2014

@author: tjoneslo
'''
import logging
import math
from pypdflite import PDFLite
from pypdflite import PDFCursor
from pypdflite.pdfobjects.pdfline import PDFLine
from Galaxy import Sector
from Galaxy import Galaxy
from Star import Star


class HexMap(object):
    '''
    classdocs
    '''

    def __init__(self, galaxy):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('PyRoute.HexMap')
        self.galaxy = galaxy
        self.ym = 9     # half a hex height
        self.xm = 6     # half the length of one side
        self.colorStart = 0

    def write_maps(self):
        for sector in self.galaxy.sectors.itervalues():
            pdf = self.document(sector.name)
            self.write_base_map(pdf, sector)
            
            for (star, neighbor, data) in self.galaxy.stars.edges_iter(sector.worlds, True):
                if self.galaxy.stars[neighbor][star]['trade'] > 0:
                    if self.galaxy.stars[neighbor][star]['trade'] > data['trade']:
                        self.galaxy.stars[neighbor][star]['trade'] += data['trade']
                        data['trade'] = 0
                    else:
                        data['trade'] += self.galaxy.stars[neighbor][star]['trade']
                        self.galaxy.stars[neighbor][star]['trade'] = 0
                    
                if data['trade'] > 0 and self.trade_to_btn(data['trade']) > 7:
                    self.logger.debug("trade line %s - %s : %s" % (star, neighbor, data))
                    self.trade_line(pdf, [star, neighbor], data)

            for star in sector.worlds:
                self.system(pdf, star)
            self.writer.close()
    
    def write_base_map(self, pdf, sector):
        self.sector_name(pdf, sector.name)
        self.subsector_grid(pdf)
        self.hex_grid(pdf)
        
    def sector_name(self,pdf,name):
        cursor = PDFCursor(5, 25, True)
        def_font = pdf.get_font()
        pdf.set_font('times', size=30)
        width = pdf.get_font()._string_width(name)
        cursor.x = 306-(width/2)
        pdf.add_text (name, cursor)
        pdf.set_font(font=def_font)

    def subsector_grid(self, pdf):
        color = pdf.get_color()
        color.set_color_by_name('lightgray')
        pdf.set_draw_color(color)
        vlineStart = PDFCursor (0,59)
        vlineEnd = PDFCursor (0,778)
        for x in [15, 159, 303, 447, 591]:
            vlineStart.x = x
            vlineEnd.x = x
            pdf.add_line(cursor1=vlineStart, cursor2=vlineEnd)
            
        hlineStart = PDFCursor(15,0)
        hlineEnd   = PDFCursor(591,0)
        for y in [59, 238, 418, 598, 778]:
            hlineStart.y = y
            hlineEnd.y = y
            pdf.add_line(cursor1=hlineStart, cursor2=hlineEnd)

    def hex_grid(self, pdf):
        hlineStart = PDFCursor(0,0)
        hlineEnd   = PDFCursor(0,0)
        
        llineStart = PDFCursor(-10,0)
        llineEnd    = PDFCursor(-10,0)
        
        rlineStart   = PDFCursor(0,0)
        rlineEnd    = PDFCursor(0,0)
        
        color = pdf.get_color()
        color.set_color_by_name('lightgray')
        
        hline = PDFLine(pdf.session, pdf.page, hlineStart, hlineEnd, style='solid', color=color, size=0.5)
        lline = PDFLine(pdf.session, pdf.page, llineStart, llineEnd, style='solid', color=color, size=0.5)
        rline = PDFLine(pdf.session, pdf.page, rlineStart, rlineEnd, style='solid', color=color, size=0.5)
        
        hlineStart.x = 3
        hlineStart.dx = self.xm * 3
        hlineStart.dy = self.ym * 2
        hlineEnd.x = self.xm * 2.5
        hlineEnd.dx = self.xm * 3
        hlineEnd.dy = self.ym * 2
        
        llineStart.x = 15
        llineStart.dx = self.xm * 3
        llineStart.dy = self.ym * 2
        llineEnd.x  = 21
        llineEnd.dx = self.xm * 3
        llineEnd.dy = self.ym * 2
        
        rlineStart.x = 21
        rlineStart.dx = self.xm * 3
        rlineStart.dy = self.ym * 2
        rlineEnd.x=15
        rlineEnd.dx = self.xm * 3
        rlineEnd.dy = self.ym * 2
        
        for x in xrange (33):
            hlineStart.x_plus()
            hlineEnd.x_plus()
            
            if (x & 1) :
                hlineStart.y = 53 - self.ym
                hlineEnd.y = 53 - self.ym
                llineStart.y = 53 - 2 * self.ym
                llineEnd.y = 53 - self.ym
                rlineStart.y = 53 - 3 *self.ym
                rlineEnd.y = 53 - 2 * self.ym
            else:
                hlineStart.y = 53 - 2 * self.ym
                hlineEnd.y = 53 - 2 * self.ym
                llineStart.y = 53 - self.ym
                llineEnd.y = 53 - 2 * self.ym
                rlineStart.y = 53 - 2 * self.ym
                rlineEnd.y = 53 - 3 * self.ym
                
            for y in xrange(41):
                hlineStart.y_plus()
                hlineEnd.y_plus()
                llineStart.y_plus()
                llineEnd.y_plus()
                rlineStart.y_plus()
                rlineEnd.y_plus()
                if (x < 32):
                    hline._draw()
                lline._draw()
                if (y > 0):
                    rline._draw()
            llineStart.x_plus()
            llineEnd.x_plus ()
            rlineStart.x_plus()
            rlineEnd.x_plus()

    def system(self, pdf, star):
        def_font = pdf.get_font()
        pdf.set_font('times', size=4)
        
        col = (self.xm * 3 * (star.col))
        if (star.col & 1):
            row = (53 - self.ym * 2) + (star.row * self.ym * 2) 
        else:
            row = (53 - self.ym) +  (star.row * self.ym * 2)
             
        point = PDFCursor(col, row)
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
        
        tradeColors = ['red','yellow', 'green', 'cyan', 'blue', 'darkgray' ]
        start = edge[0]
        end = edge[1]
        
        starty = 53 + ( self.ym * 2 * (start.row)) - (self.ym * (1 if start.col & 1 else 0))
        endy   = 53 + ( self.ym * 2 * (end.row)) - (self.ym * (1 if end.col & 1 else 0))
        lineStart = PDFCursor ((self.xm * 3 * (start.col)) + self.ym, starty)
        lineEnd = PDFCursor ((self.xm * 3 * (end.col)) + self.ym, endy)
        color = pdf.get_color()
        
        
        color.set_color_by_name(tradeColors[min(max(0, self.trade_to_btn(data['trade']) - 8), 5)])

        line = PDFLine(pdf.session, pdf.page, lineStart, lineEnd, style='solid', color=color, size=1)
        line._draw()
        self.colorStart += 30
                        
    def document(self, name):
        self.writer = PDFLite(name + ".pdf")
        document = self.writer.get_document()
        document.set_margins(5)
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
    pdf = hexMap.document('test')
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
        