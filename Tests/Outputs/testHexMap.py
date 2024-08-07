import ast
import os
import re
import unittest
from PIL import Image

import networkx as nx
import numpy as np
import pytest
from pymupdf import pymupdf

from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary, SectorDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Outputs.HexMap import HexMap
from PyRoute.Outputs.PDFHexMap import PDFHexMap
from Tests.baseTest import baseTest


class testHexMap(baseTest):
    timestamp_regex = rb'(\d{14,})'
    md5_regex = rb'([0-9a-f]{32,})'
    timeline = re.compile(timestamp_regex)
    md5line = re.compile(md5_regex)

    def test_document_object(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh empty.sec')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.subsectors = True

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = HexMap(galaxy, 'trade')

        blurb = [
            ("Live map", True, os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')),
            ("Regression map", False, "string")
        ]

        for msg, is_live, expected_path in blurb:
            with self.subTest(msg):
                document = hexmap.document(galaxy.sectors[secname], is_live=is_live)
                self.assertEqual(4, document.margins.left, 'Unexpected margins value')
                # check writer properties
                if is_live:
                    self.assertTrue(hexmap.compression, 'PDF writer compression not set')
                else:
                    self.assertFalse(hexmap.compression, 'PDF writer compression set')
                self.assertEqual('Sector Zao Kfeng Ig Grilokh (-2,4)', hexmap.writer.title)
                self.assertEqual('Trade route map generated by PyRoute for Traveller', hexmap.writer.subject)
                self.assertEqual('PyPDFLite', hexmap.writer.creator)
                self.assertEqual(expected_path, hexmap.writer.filepath)

    def test_document_object_pdf(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh empty.sec')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.subsectors = True

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = PDFHexMap(galaxy, 'trade')

        blurb = [
            ("Live map", True, os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')),
            ("Regression map", False, "string")
        ]

        for msg, is_live, expected_path in blurb:
            with self.subTest(msg):
                document = hexmap.document(galaxy.sectors[secname], is_live=is_live)
                # self.assertEqual(4, document.margins.left, 'Unexpected margins value')
                # check writer properties
                #if is_live:
                #    self.assertTrue(hexmap.compression, 'PDF writer compression not set')
                #else:
                #    self.assertFalse(hexmap.compression, 'PDF writer compression set')
                self.assertEqual('Sector Zao Kfeng Ig Grilokh (-2,4)', document._doc.info.title)
                self.assertEqual('Trade route map generated by PyRoute for Traveller', document._doc.info.subject)
                self.assertEqual('ReportLab', document._doc.info.creator)
                self.assertEqual(expected_path, document._filename)

    def test_verify_empty_sector_write(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh empty.sec')

        outfile = self.unpack_filename('OutputFiles/verify_empty_sector_write/Zao Kfeng Ig Grilokh empty.txt')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.subsectors = True

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)

        galaxy.output_path = args.output

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = HexMap(galaxy, 'trade')
        self.assertTrue(hexmap.compression)

        oldtime = b'20230911163653'
        oldmd5 = b'8419949643701e6b438d6f3f93239cf7'

        with open(outfile, 'rb') as file:
            expected_result = file.read()

        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=False)
        self.assertFalse(hexmap.compression)
        self.assertIsNotNone(result)
        # rather than try to mock datetime.now(), patch the output result.
        # this also lets us check that there's only a single match
        matches = self.timeline.search(result)
        self.assertEqual(1, len(matches.groups()), 'Should be exactly one create-date match')
        result = self.timeline.sub(oldtime, result)
        # likewise patch md5 outout
        matches = self.md5line.findall(result)
        self.assertEqual(2, len(matches), 'Should be exactly two MD5 matches')
        result = self.md5line.sub(oldmd5, result)

        self.assertEqual(expected_result, result)

    def test_verify_empty_sector_write_pdf(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh empty.sec')
        srcpdf = self.unpack_filename(
            'OutputFiles/verify_empty_sector_write/Zao Kfeng Ig Grilokh empty.pdf')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.subsectors = True

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)

        galaxy.output_path = args.output

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = PDFHexMap(galaxy, 'trade')
        self.assertTrue(hexmap.compression)

        targpath = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')
        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)
        self.assertTrue(hexmap.compression)
        src_img = pymupdf.open(srcpdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        srcfile = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector original.png')
        src.save(srcfile)
        trg_img = pymupdf.open(targpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trgfile = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector remix.png')
        trg.save(trgfile)

        image1 = Image.open(srcfile)
        image2 = Image.open(trgfile)

        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

    @pytest.mark.xfail(reason='Flaky on ubuntu')
    def test_verify_subsector_trade_write(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh - subsector P.sec')
        outfile = self.unpack_filename('OutputFiles/verify_subsector_trade_write/Zao Kfeng Ig Grilokh - subsector P - trade.txt')

        starsfile = self.unpack_filename('OutputFiles/verify_subsector_trade_write/trade stars.txt')
        rangesfile = self.unpack_filename('OutputFiles/verify_subsector_trade_write/trade ranges.txt')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.subsectors = True
        args.routes = 'trade'

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        with open(starsfile, 'rb') as file:
            galaxy.stars = nx.read_edgelist(file, nodetype=int)
        self.assertEqual(26, len(galaxy.stars.nodes()), "Unexpected number of stars nodes")
        self.assertEqual(53, len(galaxy.stars.edges), "Unexpected number of stars edges")
        for item in galaxy.stars.edges(data=True):
            self.assertIn('trade', item[2], 'Trade value not set during edgelist read')

        self._load_ranges(galaxy, rangesfile)
        self.assertEqual(27, len(galaxy.ranges.nodes()), "Unexpected number of ranges nodes")
        self.assertEqual(44, len(galaxy.ranges.edges), "Unexpected number of ranges edges")

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = HexMap(galaxy, 'trade')

        oldtime = b'20230912001440'
        oldmd5 = b'b1f97f6ac37340ab332a9a0568711ec0'

        with open(outfile, 'rb') as file:
            expected_result = file.read()

        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=False)
        self.assertIsNotNone(result)
        # rather than try to mock datetime.now(), patch the output result.
        # this also lets us check that there's only a single match
        matches = self.timeline.search(result)
        self.assertEqual(1, len(matches.groups()), 'Should be exactly one create-date match')
        result = self.timeline.sub(oldtime, result)
        # likewise patch md5 output
        matches = self.md5line.findall(result)
        self.assertEqual(2, len(matches), 'Should be exactly two MD5 matches')
        result = self.md5line.sub(oldmd5, result)
        self.assertEqual(expected_result, result)

    def test_verify_subsector_trade_write_pdf(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh - subsector P.sec')
        srcpdf = self.unpack_filename('OutputFiles/verify_subsector_trade_write/Zao Kfeng Ig Grilokh - subsector P - trade.pdf')

        starsfile = self.unpack_filename('OutputFiles/verify_subsector_trade_write/trade stars.txt')
        rangesfile = self.unpack_filename('OutputFiles/verify_subsector_trade_write/trade ranges.txt')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.subsectors = True
        args.routes = 'trade'

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        with open(starsfile, 'rb') as file:
            galaxy.stars = nx.read_edgelist(file, nodetype=int)
        self.assertEqual(26, len(galaxy.stars.nodes()), "Unexpected number of stars nodes")
        self.assertEqual(53, len(galaxy.stars.edges), "Unexpected number of stars edges")
        for item in galaxy.stars.edges(data=True):
            self.assertIn('trade', item[2], 'Trade value not set during edgelist read')

        self._load_ranges(galaxy, rangesfile)
        self.assertEqual(27, len(galaxy.ranges.nodes()), "Unexpected number of ranges nodes")
        self.assertEqual(44, len(galaxy.ranges.edges), "Unexpected number of ranges edges")

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = PDFHexMap(galaxy, 'trade')

        targpath = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')
        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)
        src_img = pymupdf.open(srcpdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        srcfile = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector original.png')
        src.save(srcfile)
        trg_img = pymupdf.open(targpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trgfile = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector remix.png')
        trg.save(trgfile)

        image1 = Image.open(srcfile)
        image2 = Image.open(trgfile)

        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

    def test_verify_subsector_comm_write(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh - subsector P.sec')
        outfile = self.unpack_filename('OutputFiles/verify_subsector_comm_write/Zao Kfeng Ig Grilokh - subsector P - comm.txt')

        starsfile = self.unpack_filename('OutputFiles/verify_subsector_comm_write/comm stars.txt')

        rangesfile = self.unpack_filename('OutputFiles/verify_subsector_comm_write/comm ranges.txt')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.routes = 'comm'
        args.subsectors = True

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        with open(starsfile, 'rb') as file:
            galaxy.stars = nx.read_edgelist(file, nodetype=int)
        self.assertEqual(5, len(galaxy.stars.nodes()), "Unexpected number of stars nodes")
        self.assertEqual(4, len(galaxy.stars.edges), "Unexpected number of stars edges")
        for item in galaxy.stars.edges(data=True):
            self.assertIn('trade', item[2], 'Trade value not set during edgelist read')

        self._load_ranges(galaxy, rangesfile)
        self.assertEqual(27, len(galaxy.ranges.nodes()), "Unexpected number of ranges nodes")
        self.assertEqual(28, len(galaxy.ranges.edges), "Unexpected number of ranges edges")

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = HexMap(galaxy, 'trade')

        oldtime = b'20230912013953'
        oldmd5 = b'ff091edb9d8ca0abacea39e5791a9843'

        with open(outfile, 'rb') as file:
            expected_result = file.read()

        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=False)
        self.assertIsNotNone(result)
        # rather than try to mock datetime.now(), patch the output result.
        # this also lets us check that there's only a single match
        matches = self.timeline.search(result)
        self.assertEqual(1, len(matches.groups()), 'Should be exactly one create-date match')
        result = self.timeline.sub(oldtime, result)
        # likewise patch md5 output
        matches = self.md5line.findall(result)
        self.assertEqual(2, len(matches), 'Should be exactly two MD5 matches')
        result = self.md5line.sub(oldmd5, result)
        self.assertEqual(expected_result, result)

    def test_verify_subsector_comm_write_pdf(self):
        sourcefile = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh - subsector P.sec')
        srcpdf = self.unpack_filename(
            'OutputFiles/verify_subsector_comm_write/Zao Kfeng Ig Grilokh - subsector P - comm.pdf')

        starsfile = self.unpack_filename('OutputFiles/verify_subsector_comm_write/comm stars.txt')
        rangesfile = self.unpack_filename('OutputFiles/verify_subsector_comm_write/comm ranges.txt')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.routes = 'comm'
        args.subsectors = True

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        with open(starsfile, 'rb') as file:
            galaxy.stars = nx.read_edgelist(file, nodetype=int)
        self.assertEqual(5, len(galaxy.stars.nodes()), "Unexpected number of stars nodes")
        self.assertEqual(4, len(galaxy.stars.edges), "Unexpected number of stars edges")
        for item in galaxy.stars.edges(data=True):
            self.assertIn('trade', item[2], 'Trade value not set during edgelist read')

        self._load_ranges(galaxy, rangesfile)
        self.assertEqual(27, len(galaxy.ranges.nodes()), "Unexpected number of ranges nodes")
        self.assertEqual(28, len(galaxy.ranges.edges), "Unexpected number of ranges edges")

        secname = 'Zao Kfeng Ig Grilokh'

        hexmap = PDFHexMap(galaxy, 'comm')

        targpath = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')
        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)
        src_img = pymupdf.open(srcpdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        srcfile = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector original.png')
        src.save(srcfile)
        trg_img = pymupdf.open(targpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trgfile = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector remix.png')
        trg.save(trgfile)

        image1 = Image.open(srcfile)
        image2 = Image.open(trgfile)

        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

    def test_verify_coreward_rimward_sector(self):
        source1file = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh empty.sec')
        source2file = self.unpack_filename('DeltaFiles/no_subsectors_named/Ngathksirz empty.sec')

        source1pdf = self.unpack_filename('OutputFiles/verify_coreward_rimward/Zao Kfeng Ig Grilokh Sector.pdf')
        source2pdf = self.unpack_filename('OutputFiles/verify_coreward_rimward/Ngathksirz Sector.pdf')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.routes = 'trade'
        args.subsectors = False

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(source1file)
        delta[sector.name] = sector
        sector = SectorDictionary.load_traveller_map_file(source2file)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        zaokpath = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')
        ngatpath = os.path.abspath(args.output + '/Ngathksirz Sector.pdf')

        hexmap = PDFHexMap(galaxy, 'trade')

        secname = 'Zao Kfeng Ig Grilokh'
        hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)
        secname = 'Ngathksirz'
        hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)

        srczaok = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector original.png')
        srcngat = os.path.abspath(args.output + '/Ngathksirz Sector original.png')
        trgzaok = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector remix.png')
        trgngat = os.path.abspath(args.output + '/Ngathksirz Sector remix.png')

        src_img = pymupdf.open(source1pdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        src.save(srczaok)

        src_img = pymupdf.open(source2pdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        src.save(srcngat)

        trg_img = pymupdf.open(zaokpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trg.save(trgzaok)

        trg_img = pymupdf.open(ngatpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trg.save(trgngat)

        image1 = Image.open(srczaok)
        image2 = Image.open(trgzaok)

        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

        image1 = Image.open(srcngat)
        image2 = Image.open(trgngat)
        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

    def test_verify_spinward_trailing_sector(self):
        source1file = self.unpack_filename('DeltaFiles/no_subsectors_named/Zao Kfeng Ig Grilokh empty.sec')
        source2file = self.unpack_filename('DeltaFiles/no_subsectors_named/Knaeleng empty.sec')

        source1pdf = self.unpack_filename('OutputFiles/verify_spinward_trailing/Zao Kfeng Ig Grilokh Sector.pdf')
        source2pdf = self.unpack_filename('OutputFiles/verify_spinward_trailing/Knaeleng Sector.pdf')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.routes = 'trade'
        args.subsectors = False

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(source1file)
        delta[sector.name] = sector
        sector = SectorDictionary.load_traveller_map_file(source2file)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        zaokpath = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector.pdf')
        ngatpath = os.path.abspath(args.output + '/Knaeleng Sector.pdf')

        hexmap = PDFHexMap(galaxy, 'trade')

        secname = 'Zao Kfeng Ig Grilokh'
        hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)
        secname = 'Knaeleng'
        hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)

        srczaok = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector original.png')
        srcngat = os.path.abspath(args.output + '/Knaeleng Sector original.png')
        trgzaok = os.path.abspath(args.output + '/Zao Kfeng Ig Grilokh Sector remix.png')
        trgngat = os.path.abspath(args.output + '/Knaeleng Sector remix.png')

        src_img = pymupdf.open(source1pdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        src.save(srczaok)

        src_img = pymupdf.open(source2pdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        src.save(srcngat)

        trg_img = pymupdf.open(zaokpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trg.save(trgzaok)

        trg_img = pymupdf.open(ngatpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trg.save(trgngat)

        image1 = Image.open(srczaok)
        image2 = Image.open(trgzaok)

        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

        image1 = Image.open(srcngat)
        image2 = Image.open(trgngat)
        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference above threshold")

    def test_verify_xboat_write_pdf(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        srcpdf = self.unpack_filename(
            'OutputFiles/verify_subsector_xroute_write/Zarushagar Sector.pdf')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.routes = 'xroute'
        args.subsectors = False

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()

        secname = 'Zarushagar'

        hexmap = PDFHexMap(galaxy, 'xroute')

        targpath = os.path.abspath(args.output + '/Zarushagar Sector.pdf')
        result = hexmap.write_sector_pdf_map(galaxy.sectors[secname], is_live=True)
        src_img = pymupdf.open(srcpdf)
        src_iter = src_img.pages(0)
        for page in src_iter:
            src = page.get_pixmap()
        srcfile = os.path.abspath(args.output + '/Zarushagar Sector original.png')
        src.save(srcfile)
        trg_img = pymupdf.open(targpath)
        trg_iter = trg_img.pages(0)
        for page in trg_iter:
            trg = page.get_pixmap()
        trgfile = os.path.abspath(args.output + '/Zarushagar Sector remix.png')
        trg.save(trgfile)

        image1 = Image.open(srcfile)
        image2 = Image.open(trgfile)

        array1 = np.array(image1)
        array2 = np.array(image2)

        mse = np.mean((array1 - array2) ** 2)
        self.assertTrue(0.2 > mse, "Image difference " + str(mse) + " above threshold")

    def test_verify_quadripoint_trade_write(self):
        source1file = self.unpack_filename('DeltaFiles/quadripoint_trade_write/Tuglikki.sec')
        source2file = self.unpack_filename('DeltaFiles/quadripoint_trade_write/Provence.sec')
        source3file = self.unpack_filename('DeltaFiles/quadripoint_trade_write/Deneb.sec')
        source4file = self.unpack_filename('DeltaFiles/quadripoint_trade_write/Corridor.sec')

        args = self._make_args()
        args.interestingline = None
        args.interestingtype = None
        args.maps = True
        args.routes = 'trade'
        args.subsectors = False
        args.btn = 7

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(source1file)
        delta[sector.name] = sector
        sector = SectorDictionary.load_traveller_map_file(source2file)
        delta[sector.name] = sector
        sector = SectorDictionary.load_traveller_map_file(source3file)
        delta[sector.name] = sector
        sector = SectorDictionary.load_traveller_map_file(source4file)
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.set_borders(args.borders, args.ally_match)
        galaxy.trade.calculate_routes()

        secname = ['Tuglikki', 'Provence', 'Deneb', 'Corridor']

        hexmap = PDFHexMap(galaxy, 'trade', args.btn)
        for sector_name in secname:
            hexmap.write_sector_pdf_map(galaxy.sectors[sector_name], is_live=True)

        fullname = ['Tuglikki Sector', 'Provence Sector', 'Deneb Sector', 'Corridor Sector']
        srcstem = self.unpack_filename('OutputFiles/verify_quadripoint_trade_write/Corridor Sector.pdf')
        srcstem = srcstem[:-20]
        trgstem = os.path.abspath(args.output + '/')

        for full in fullname:
            srcpdf = srcstem + '/' + full + '.pdf'
            trgpdf = trgstem + '/' + full + '.pdf'

            src_img = pymupdf.open(srcpdf)
            src_iter = src_img.pages(0)
            for page in src_iter:
                src = page.get_pixmap()

            srcfile = os.path.abspath(args.output + '/' + full + ' original.png')
            src.save(srcfile)

            trg_img = pymupdf.open(trgpdf)
            trg_iter = trg_img.pages(0)
            for page in trg_iter:
                trg = page.get_pixmap()
            trgfile = os.path.abspath(args.output + '/' + full + ' remix.png')
            trg.save(trgfile)

            image1 = Image.open(srcfile)
            image2 = Image.open(trgfile)

            array1 = np.array(image1)
            array2 = np.array(image2)

            mse = np.mean((array1 - array2) ** 2)
            self.assertTrue(0.24 > mse, "Image difference " + str(mse) + " above threshold for " + full)

    def _load_ranges(self, galaxy, sourcefile):
        with open(sourcefile, "rb") as f:
            lines = f.readlines()
            for rawline in lines:
                line = rawline.strip()
                bitz = line.split(b') ')
                source = str(bitz[0]).replace('\'', '').lstrip('b')
                target = str(bitz[1]).replace('\'', '').lstrip('b')
                srcbitz = source.split('(')
                targbitz = target.split('(')
                hex1 = srcbitz[1][-4:]
                sec1 = srcbitz[1][0:-5]
                hex2 = targbitz[1][-4:]
                sec2 = targbitz[1][0:-5]

                world1 = galaxy.sectors[sec1].find_world_by_pos(hex1)
                world2 = galaxy.sectors[sec2].find_world_by_pos(hex2)
                rawdata = str(bitz[2]).lstrip('b')
                data = ast.literal_eval(ast.literal_eval(rawdata))

                galaxy.ranges.add_edge(world1, world2)
                for item in data:
                    galaxy.ranges[world1][world2][item] = data[item]


if __name__ == '__main__':
    unittest.main()
