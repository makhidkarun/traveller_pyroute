from Tests.baseTest import baseTest

from AreaItems.Galaxy import Galaxy
from AreaItems.Sector import Sector
from Outputs.Cursor import Cursor
from Outputs.Map import Map


class testMap(baseTest):
    def test_start(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")

        expected_start = Cursor(0, 0)
        self.assertEqual(expected_start, map.start, "Unexpected start value")

    def test_hex_size(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")

        expected_hex_size = Cursor(6, 9)
        self.assertEqual(expected_hex_size, map.hex_size, "Unexpected hex_size value")

    def test_document(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.document("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected document exception")

    def test_close(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.close()
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected close exception")

    def test_add_line(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_line(cursor, cursor, "white")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-line exception")

    def test_add_rectangle(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_rectangle(cursor, cursor, "white", "white", 1)
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-rectangle exception")

    def test_add_text(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_text("text", cursor, "white")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-text exception")

    def test_add_text_centred(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_text_centred("text", cursor, "white")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-text-centred exception")

    def test_add_text_centred_legacy(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_text_centred_legacy("text", cursor, "white")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-text-centred-legacy exception")

    def test_add_text_rotated(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_text_centred_legacy("text", cursor, "white", 0)
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-text-rotated exception")

    def test_add_text_right_aligned(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_text_right_aligned("text", cursor, "white")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-text-right-aligned exception")

    def test_add_circle(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        cursor = Cursor(0, 0)

        try:
            map.add_circle(cursor, 1, 1, True, "white")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected add-circle exception")

    def test_write_maps(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.write_maps()
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected write-maps exception")

    def test_write_base_map(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        sector = Sector("# Core", "# 0, 0")

        try:
            map.write_base_map(sector)
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected write-base-maps exception")

    def test_area_name_title(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.area_name_title("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected area-name-title exception")

    def test_draw_borders(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None
        sector = Sector("# Core", "# 0, 0")

        try:
            map.draw_borders(sector)
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected draw-borders exception")

    def test_coreward_name(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.coreward_name("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected coreward-name exception")

    def test_rimward_name(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.rimward_name("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected rimward-name exception")

    def test_spinward_name(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.spinward_name("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected spinward-name exception")

    def test_trailing_name(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.trailing_name("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected trailing-name exception")

    def test_get_colour_key_error(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map.get_colour("foobar")
        except KeyError as e:
            msg = str(e)

        self.assertEqual("'foobar'", msg, "Unexpected get-colour exception")

    def test_get_colour(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map._get_colour("foobar")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected get-colour exception")

    def test_get_text_size(self) -> None:
        galaxy = Galaxy(8)
        map = Map(galaxy, "trade", "./", "writer")
        msg = None

        try:
            map._get_text_size("foobar", "11")
        except NotImplementedError as e:
            msg = str(e)

        self.assertEqual("Base Class", msg, "Unexpected get-colour exception")
