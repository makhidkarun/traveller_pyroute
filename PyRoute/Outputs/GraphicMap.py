"""
Created on Sep 12, 2023

@author: CyberiaResurrection
"""
import os
import math

from PIL import Image, ImageDraw, ImageColor, ImageFont

from PyRoute.Outputs.Colour import Colour
from PyRoute.Outputs.Cursor import Cursor
from PyRoute.Outputs.FontLayer import FontLayer
from PyRoute.Outputs.Map import Map, Scheme


class GraphicMap(Map):
    fillBlack = (0, 0, 0, 255)
    fillWhite = (255, 255, 255, 255)
    fillBlue = (50, 215, 255, 255)
    fillRed = (255, 48, 48, 255)

    input_scale: float = 1
    output_scale: float = 1

    ym = 9  # half a hex height
    xm = 6  # half the length of one side
    subsector_grid_width = 592
    subsector_width = 144
    subsector_grid_height = 780
    subsector_height = 180

    def __init__(self, galaxy, routes: str, output_path: str, writer: str):
        super(GraphicMap, self).__init__(galaxy, routes, output_path, writer)
        self.image: Image = None
        self.doc: ImageDraw = None

        self.area_name: str = None

        self.font_layer = FontLayer()
        self.fonts: dict[str, ImageFont] = {
            'title': ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed-Bold.ttf'), int(25 * self.input_scale)),
            'info': ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed-Bold.ttf'), int(5 * self.input_scale)),
            'sector': ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed-Bold.ttf'), int(6 * self.input_scale)),
            'system_port': ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed-Bold.ttf'), int(5 * self.input_scale)),
            'system_uwp': ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed-Bold.ttf'), int(3 * self.input_scale)),
            'system_name': ImageFont.truetype(self.font_layer.getpath('DejaVuSerifCondensed-Bold.ttf'), int(5 * self.input_scale)),
            'base code': ImageFont.truetype(self.font_layer.getpath('ZapfDingbats_Regular.ttf'), int(5 * self.input_scale))
        }

        self.colours: dict[str, Colour] = {
            'background': 'white',
            'title': self.fillBlue,
            'info': self.fillBlack,
            'sector': self.fillBlack,
            'system_port': 'black',
            'system_uwp': 'black',
            'system_name': 'black',
            'base code': 'black',

            'grid': 'lightgrey',
            'hexes': 'lightgrey',
            'red zone': 'crimson',
            'amber zone':  (218, 165, 32),  # Goldenrod from the PDF
            'gg refuel': (218, 165, 32),
            'wild refuel': (101, 223, 230),
            'comm': (83, 204, 106),

        }

        self.logger.debug("Completed GraphicMap init")

    def document(self, area_name: str, is_live=True):
        background = self.colours['background']
        size = (int(self.image_size.x * self.input_scale), int(self.image_size.y * self.input_scale))
        self.image = Image.new("RGB", size, "white" if not background else background)
        self.area_name = area_name
        return ImageDraw.Draw(self.image)

    def close(self):
        path = os.path.join(self.output_path, self.area_name + ".png")
        resize = (int(self.image_size.x * self.input_scale * self.output_scale),
                  int(self.image_size.y * self.input_scale * self.output_scale))
        self.image = self.image.resize(resize, Image.BICUBIC)
        self.image.save(path)

    def add_line(self, start: Cursor, end: Cursor, colour: Colour, stroke='solid', width: float = 1):
        origin = (start.x * self.input_scale, start.y * self.input_scale)
        termin = (end.x * self.input_scale, end.y * self.input_scale)
        self.doc.line([origin, termin], self._get_colour(colour), width=width * self.input_scale)

    def add_rectangle(self, start: Cursor, end: Cursor, border_colour: Colour, fill_colour: Colour, width: int):
        origin = (start.x * self.input_scale, start.y * self.input_scale)
        termin = (end.x * self.input_scale, end.y * self.input_scale)
        self.doc.rectangle([origin, termin], self._get_colour(fill_colour), self._get_colour(border_colour), width)

    def add_circle(self, centre: Cursor, radius: int, line_width: int, fill: bool, scheme: Scheme):
        if self.colours[scheme] is None:
            return
        colour = self._get_colour(self.colours[scheme])
        origin = (centre.x - radius) * self.input_scale, (centre.y - radius) * self.input_scale
        termin = (centre.x + radius) * self.input_scale, (centre.y + radius) * self.input_scale
        fill = colour if fill else None
        self.doc.ellipse([origin, termin], outline=colour, width=line_width * self.input_scale, fill=fill)

        # for offset in range(-3, 3):
        #     band = radius + offset
        #     self.doc.ellipse([(centre.x - band, centre.y - band), (centre.x + band, centre.y + band)], outline=colour, width=)

    def add_text(self, text: str, start: Cursor, scheme: Scheme) -> None:
        font = self.get_font(scheme)
        colour = self.get_colour(scheme)
        position = (start.x * self.input_scale, start.y * self.input_scale)
        self.doc.text(position, text, font=font, fill=colour)

    def add_text_centred(self, text: str, start: Cursor, scheme: Scheme, max_width: int = -1) -> None:
        font = self.get_font(scheme)
        colour = self.get_colour(scheme)
        out_text = text
        width, _ = self._get_text_size(font, text)

        if max_width > 0 and len(text) > 0:
            for chars in range(len(text), 0, -1):
                width, _ = self._get_text_size(font, text[:chars])
                if width <= max_width * self.input_scale:
                    out_text = text[:chars]
                    break

        position = ((start.x * self.input_scale) - (width // 2),
                    (start.y * self.input_scale))
        self.doc.text(position, out_text, font=font, fill=colour)

    def add_text_rotated(self, text: str, start: Cursor, scheme: Scheme, rotation: int) -> None:
        font = self.get_font(scheme)
        colour = self.get_colour(scheme)
        width, height = self._get_text_size(font, text)

        size = (width, height + 3)
        txt = Image.new('L', size, 0)
        d = ImageDraw.Draw(txt)
        d.text((0, 0), text, font=font, fill=255)
        w = txt.rotate(rotation, expand=True)

        self.doc.bitmap((start.x * self.input_scale, (start.y * self.input_scale) - w.size[1] // 2), w, fill=colour)

    def add_text_right_aligned(self, text: str, start: Cursor, scheme: Scheme) -> None:
        font = self.get_font(scheme)
        colour = self.get_colour(scheme)
        width, _ = self._get_text_size(font, text)
        position = ((start.x * self.input_scale) - width, start.y * self.input_scale)
        self.doc.text(position, text, font=font, fill=colour)

    @staticmethod
    def _get_colour(colour: Colour):
        if isinstance(colour, str):
            return ImageColor.getrgb(colour)
        return colour

    @staticmethod
    def _get_text_size(font: ImageFont, string: str) -> tuple[int, int]:
        _, _, width, height = font.getbbox(string)
        return width, height


class DashedImageDraw(ImageDraw.ImageDraw):

    def thick_line(self, xy, direction, fill=None, width=0) -> None:
        """
        Draw a dotted or dashed line
        :param xy: sequence of 2-tuples like [(x, y), (x, y), ...]. end points of the line(s)
        :param direction: Sequence of 2-tuples like [(x, y), (x, y), ...] describing dashes and spaces
        :param fill: Fill colour
        :param width: width of the line to be drawn
        :return: None
        """
        if xy[0] != xy[1]:
            self.line(xy, fill=fill, width=width)
        else:
            x1, y1 = xy[0]
            dx1, dy1 = direction[0]
            dx2, dy2 = direction[1]
            if dy2 - dy1 < 0:
                x1 -= 1
            if dx2 - dx1 < 0:
                y1 -= 1
            if dy2 - dy1 != 0:
                if dx2 - dx1 != 0:
                    k = - (dx2 - dx1) / (dy2 - dy1)
                    a = 1 / math.sqrt(1 + k ** 2)
                    b = (width * a - 1) / 2
                else:
                    k = 0
                    b = (width - 1) / 2
                x3 = x1 - math.floor(b)
                y3 = y1 - int(k * b)
                x4 = x1 + math.ceil(b)
                y4 = y1 + int(k * b)
            else:
                x3 = x1
                y3 = y1 - math.floor((width - 1) / 2)
                x4 = x1
                y4 = y1 + math.ceil((width - 1) / 2)
            self.line([(x3, y3), (x4, y4)], fill=fill, width=1)
        return

    def dashed_line(self, xy, dash=(2, 2), fill=None, width=0):
        # xy – Sequence of 2-tuples like [(x, y), (x, y), ...]
        for i in range(len(xy) - 1):
            x1, y1 = xy[i]
            x2, y2 = xy[i + 1]
            x_length = x2 - x1
            y_length = y2 - y1
            length = math.sqrt(x_length ** 2 + y_length ** 2)
            dash_enabled = True
            postion = 0
            while postion <= length:
                for dash_step in dash:
                    if postion > length:
                        break
                    if dash_enabled:
                        start = postion / length
                        end = min((postion + dash_step - 1) / length, 1)
                        self.thick_line([(round(x1 + start * x_length),
                                          round(y1 + start * y_length)),
                                         (round(x1 + end * x_length),
                                          round(y1 + end * y_length))],
                                        xy, fill, width)
                    dash_enabled = not dash_enabled
                    postion += dash_step
        return
