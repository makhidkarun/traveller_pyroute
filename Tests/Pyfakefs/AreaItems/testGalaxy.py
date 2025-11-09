"""
Created on Nov 09, 2025

@author: CyberiaResurrection
"""
import os

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from Tests.Pyfakefs.baseTest import baseTest


class testGalaxy(baseTest):

    def test_process_owned_worlds_1(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        args = self._make_args()
        args.routes = 'trade'
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.generate_routes()
        galaxy.output_path = args.output
        galaxy.set_borders(args.borders, args.ally_match)

        foostar = galaxy.star_mapping[24]
        foostar.ownedBy = 'Dagu-0'

        self.setUpPyfakefs(allow_root_user=False)
        namepath = args.output + '/owned-worlds-names.csv'
        listpath = args.output + '/owned-worlds-list.csv'

        galaxy.process_owned_worlds()

        self.assertTrue(os.path.exists(namepath))
        self.assertTrue(os.path.exists(listpath))

        expected_name = [
            '"Woden (Zarushagar 0306)", "Mr", "Strela (Zarushagar 0407)", "Imled '
            '(Zarushagar 0406)", "Miller\'s World (Zarushagar 0607)", "Makkus (Zarushagar 0304)"\n',
            '"Aslungi (Zarushagar 0605)", "None", "Gishin (Zarushagar 0804)", "Miller\'s '
            'World (Zarushagar 0607)", "Strela (Zarushagar 0407)", "Imled (Zarushagar 0406)"\n',
            '"Airvae (Zarushagar 0801)", "Mr", "Gishin (Zarushagar 0804)", "Nedadzia (Zarushagar 0701)"\n',
            '"Ginshe (Zarushagar 0805)", "Gishin (Zarushagar 0804)", "Gishin (Zarushagar '
            '0804)", "Miller\'s World (Zarushagar 0607)", "Strela (Zarushagar 0407)", "Imled (Zarushagar 0406)"\n'
        ]
        expected_list = [
            '"Zaru", "0306", "Mr", "O:0407", "O:0406", "O:0607", "O:0304"\n',
            '"Zaru", "0605", "None", "O:0804", "O:0607", "O:0407", "O:0406"\n',
            '"Zaru", "0801", "Mr", "O:0804", "O:0701"\n',
            '"Zaru", "0805", "Gishin (Zarushagar 0804)", "O:0804", "O:0607", "O:0407", "O:0406"\n']
        with open(namepath, 'r', encoding='utf-8') as f:
            name_contents = f.readlines()
        self.assertEqual(expected_name, name_contents)
        with open(listpath, 'r', encoding='utf-8') as f:
            list_contents = f.readlines()
        self.assertEqual(expected_list, list_contents)
