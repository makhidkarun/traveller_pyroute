import os
import logging
import math
import itertools
from .SubsectorMap2 import GraphicSubsectorMap
from .Galaxy import Galaxy
from PIL import Image, ImageDraw, ImageFont


class DrawArcsTest(GraphicSubsectorMap):
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

    def __init__(self, galaxy, routes):
        super(GraphicSubsectorMap, self).__init__(galaxy, routes)
        self.x_start = 56
        self.y_start = 56
        self.ym = 48  # half a hex height
        self.xm = 28  # half the length of one side
        self.textFill = self.fillWhite
        self.namesFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 32)
        self.titleFont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf', 48)
        self.hexFont = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 15)
        self.worldFont = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 22)
        self.hexFont2 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 22)
        self.hexFont3 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 36)
        self.hexFont4 = ImageFont.truetype("/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf", 22)
        self.hexFont5 = ImageFont.truetype("/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf", 36)
        self.logger = logging.getLogger('PyRoute.DrawArcsTest')

    def document(self, sector):
        self.sector = sector
        self.image = Image.new("RGB", self.image_size, "black")
        return ImageDraw.Draw(self.image)

    def close(self, subsector_name):
        path = os.path.join(self.galaxy.output_path, subsector_name + ".png")
        self.image = self.image.resize((413, 636), Image.BICUBIC)
        self.image.save(path)

    def write_maps(self):
        self.logger.info("writing test maps")
        sector = next(iter(self.galaxy.sectors.values()))
        self.logger.info("Processing sector %s" % sector.name)
        self.subsector = next(iter(sector.subsectors.values()))
        img = self.document(sector)
        self.write_base_map(img, self.subsector)
        self.draw_arcs(img)

        self.close("TestMap")

    def draw_arcs(self, doc):
        self.image = self.image.convert("RGBA")
        img = Image.new("RGBA", self.image_size, 0)
        draw = ImageDraw.Draw(img)

        start = self.centerpoint(1, 1)
        for row, col in itertools.product(list(range(0, 4)), list(range(0, 4))):
            self.draw_one_arc(draw, start, self.centerpoint(row, col))

        start = self.centerpoint(4, 4)
        for row, col in itertools.product(list(range(3, 6)), list(range(3, 6))):
            self.draw_one_arc(draw, start, self.centerpoint(row, col))

        start = self.centerpoint(8, 8)
        for row, col in itertools.product(list(range(7, 12)), list(range(7, 12))):
            self.draw_one_arc(draw, start, self.centerpoint(row, col))

        cropped = img.crop((53, 53, 760, 1067))
        cropped = cropped.crop((-53, -53, 760 + (826 - 760 - 53), 1067 + (1272 - 1067 - 53)))

        self.logger.info("Image size: {}, cropped size: {}".format(self.image.size, cropped.size))

        self.image = Image.alpha_composite(self.image, cropped)

    def draw_one_arc(self, doc, start, end):
        center = self.circle_center(start, end)
        # self.logger.info("Points are : start: {}, end: {}, and center {}".format(start,end,center))
        self.draw_arc(doc, center, start, end)

    def centerpoint(self, row, col):
        xcol = self.xm * 3 * col
        if (col & 1):
            xrow = (self.y_start - self.ym * 2) + (row * self.ym * 2)
        else:
            xrow = (self.y_start - self.ym) + (row * self.ym * 2)

        point = self.cursor(xcol, xrow)
        # Put the point in the center of the hex
        point.x_plus(self.xm)
        point.y_plus(self.ym)

        return point

    def circle_center(self, start, end):
        # Calculate the center of an equilateral triangle  from start and end
        # root3 = math.sqrt(3)
        root3 = 2
        xm = 0.5 * (start.x + end.x)
        ym = 0.5 * (start.y + end.y)

        xslope = (xm - start.x)
        yslope = (ym - start.y)

        slope = xslope / yslope if yslope != 0 else 0

        cx = xm + (root3 * slope)
        cy = ym + (root3 * slope)

        # dist1 = math.sqrt ((start.x - end.x) ** 2 + (start.y - end.y) ** 2)
        # dist2 = math.sqrt ((start.x - cx) ** 2 + (start.y - cy) ** 2)
        # dist3 = math.sqrt ((end.x - cx) ** 2 + (end.y - cy) ** 2)
        # distm1 = math.sqrt((start.x - xm) ** 2 + (start.y - ym) ** 2)
        # distm2 = math.sqrt((end.x - xm) ** 2 + (end.y - ym) ** 2)
        # self.logger.info("X: {}, Y: {}, M: {}, X -> M: {}, Y -> M:{} ".format(start, end, (xm,ym), distm1, distm2))
        # self.logger.info("X -> Y: {}, X -> C: {}, Y -> C: {}".format(dist1, dist2, dist3))

        # slope = xslope/yslope if yslope != 0 else 0

        # self.logger.info("X -> Y slope: {}/{} = {}".format(xslope, yslope, slope))

        # cxslope = (xm - cx)
        # cyslope = (ym - cy)
        # cslope = cxslope/cyslope if cyslope != 0 else 0
        # self.logger.info("M -> C slope: {}/{} = {}".format(cxslope, cyslope, cslope))

        return self.cursor(round(cx), round(cy))

    def draw_arc(self, doc, center, start, end):
        r = math.sqrt((start.x - center.x) ** 2 + (start.y - center.y) ** 2)
        x1 = center.x - r
        y1 = center.y - r
        x2 = center.x + r
        y2 = center.y + r
        startAngle = (180 / math.pi) * math.atan2(start.y - center.y, start.x - center.x)
        endAngle = (180 / math.pi) * math.atan2(end.y - center.y, end.x - center.x)

        # self.logger.info ("Radius: {}, Starting Angle: {}, ending angle: {}".format(r,startAngle, endAngle))

        # startAngle = startAngle * -1 if startAngle < 0 else startAngle
        # endAngle = endAngle * -1 if endAngle < 0 else endAngle
        # doc.ellipse([x1,y1,x2,y2], outline=self.fillWhite)

        for i in range(-4, 4):
            doc.arc([x1 + i, y1, x2 + i, y2], startAngle, endAngle, self.fillRed)
            doc.arc([x1, y1 + i, x2, y2 + i], startAngle, endAngle, self.fillRed)

        # doc.ellipse([end.x-6, end.y-6, end.x+6, end.y+6], outline=self.fillWhite, fill=self.fillWhite)
        # doc.ellipse([center.x-6, center.y-6, center.x+6, center.y+6], outline=self.fillBlue, fill=self.fillBlue)


def set_logging(level):
    logging.getLogger('PyRoute').setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logging.getLogger('PyRoute').addHandler(ch)


if __name__ == '__main__':
    set_logging('INFO')
    galaxy = Galaxy(15, 4, 8)
    galaxy.output_path = '.'
    galaxy.read_sectors(['./sectors/TNE/SpinwardMarches.sec'], 'fixed', 'collapse')
    galaxy.set_borders('erode', 'collapse')

    graphMap = DrawArcsTest(galaxy, None)
    graphMap.write_maps()
