"""
Created on Aug 05, 2024

@author: CyberiaResurrection
"""
import logging

from PyRoute.Outputs.Map import Map
from PyRoute.StatCalculation import StatCalculation


class SectorHexMap(Map):

    def __init__(self, galaxy, routes, min_btn=8):
        super(SectorHexMap, self).__init__(galaxy, routes)
        self.min_btn = min_btn
        self.writer = None

    def comm_line(self, pdf, edge):
        raise NotImplementedError("Base Class")

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

    def _setup_sector_pdf_map(self, gal_sector, is_live):
        pdf_doc = self.document(gal_sector, is_live)
        self.write_base_map(pdf_doc, gal_sector)
        self.draw_borders(pdf_doc, gal_sector)
        worlds = [item.index for item in gal_sector.worlds]
        comm_routes = [star for star in self.galaxy.stars.edges(worlds, True)
                       if star[2].get('xboat', False) or star[2].get('comm', False)]
        return comm_routes, pdf_doc, worlds

    def _sector_map_comm_and_trade_routes(self, comm_routes, pdf_doc, worlds):
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

    def _sector_map_systems_and_sectors(self, gal_sector, pdf_doc):
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

    def _system_write_additional_data(self, star):
        added = ''
        trade_in = StatCalculation.trade_to_btn(star.tradeIn)
        trade_through = StatCalculation.trade_to_btn(star.tradeIn + star.tradeOver)
        if self.routes == 'trade':
            added += "{:X}{:X}{:X}{:d}".format(star.wtn, trade_in, trade_through, star.starportSize)
        elif self.routes == 'comm':
            added += "{}{} {}".format(star.baseCode, star.ggCount, star.importance)
        elif self.routes == 'xroute':
            added += " {}".format(star.importance)
        return added

    def _trade_line_setup(self, data, edge):
        trade_colours = [(255, 0, 0),  # Red
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
            return None, None, None
        if trade > 6:
            logging.getLogger('PyRoute.HexMap').warn("trade calculated over %d" % self.min_btn + 6)
            trade = 6
        trade_colour = trade_colours[trade]
        return end, start, trade_colour

    def _get_line_endpoints(self, end, start):
        starty = self.y_start + (self.ym * 2 * start.row) - (self.ym * (1 if start.col & 1 else 0))
        startx = (self.xm * 3 * start.col) + self.ym
        end_row = end.row
        end_col = end.col
        if end.sector != start.sector:
            up = False
            down = False
            if end.sector.x < start.sector.x:
                end_col -= 32
            if end.sector.x > start.sector.x:
                end_col += 32
            if end.sector.y > start.sector.y:
                end_row -= 40
                up = True
            if end.sector.y < start.sector.y:
                end_row += 40
                down = True
            endy = self.y_start + (self.ym * 2 * end_row) - (self.ym * (1 if end_col & 1 else 0))
            endx = (self.xm * 3 * end_col) + self.ym

            (startx, starty), (endx, endy) = self.clipping(startx, starty, endx, endy)
            if up:
                assert starty >= endy, "Misaligned to-coreward trade segment between " + str(start) + " and " + str(end)
            if down:
                assert starty <= endy, "Misaligned to-rimward trade segment between " + str(start) + " and " + str(end)

        else:
            endy = self.y_start + (self.ym * 2 * end_row) - (self.ym * (1 if end_col & 1 else 0))
            endx = (self.xm * 3 * end_col) + self.ym
        return endx, endy, startx, starty
