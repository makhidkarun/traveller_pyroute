'''
Created on Oct 3, 2017

@author: tjoneslo
'''

import re
import logging

class TradeCodes(object):
    '''
    Trade Codes manage the complete set of trade codes for a world
    '''
    pcodes = ['As', 'De', 'Ga', 'Fl', 'He', 'Ic', 'Oc', 'Po', 'Va', 'Wa']
    dcodes = ['Cp', 'Cx', 'Cs', 'Mr', 'Da', 'Di', 'Pz', 'An', 'Ab', 'Fo', 'Px', 
              'Re', 'Rs', 'Sa', 'Tz', 'Lk', 
              'RsA', 'RsB','RsG','RsD','RsE','RsZ', 'RsT', 'RsI', 'RsK',
              'Fr', 'Co', 'Tp', 'Ho', 'Tr', 'Tu',
              'Cm', 'Tw' ]
    ex_codes = set(['As', 'Fl', 'Ic', 'De', 'Na', 'Va', 'Wa', 'He', 'Oc'])
    research = {'RsA': u'\u0391', 'RsB': u'\u0392', 'RsG': u'\u0393', 
                'RsD': u'\u0394', 'RdE': u'\u0395', 'RsZ': u'\u0396',
                'RsT': u'\u0398', 'RsI': u'\u0399', 'RsK': u'\u039A'}
    pcolor = {'As': '#8E9397', 'De': '#d17533', 'Fl': '#e37dff', 'He': '#ff6f0c', 'Ic':'#A5F2F3',
              'Oc': '#0094ED', 'Po': '#6a986a', 'Va': '#c9c9c9', 'Wa': '#4abef4'}

    
    def __init__(self, initial_codes):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('PyRoute.TradeCodes')
        codes = initial_codes.split()
        self.pcode = set(TradeCodes.pcodes) & set(codes)
        self.dcode = set(TradeCodes.dcodes) & set(codes)

        self.owned = [code for code in codes if code.startswith(u'O:') or code.startswith(u'C:')]

        self.sophonts = []
        for homeworld in re.findall(ur"\([^)]+\)\S?", initial_codes, re.U):
            self.sophonts.append(re.sub('[()]', '', homeworld))
            
        codeCheck = set(codes) - self.dcode - set(self.owned)
        self.homeworlds = [code for code in codeCheck if len(code)>4]
        
        self.codeset = set(codes) - self.dcode - set(self.owned) - set(self.homeworlds)
        self.codeset = sorted(list(self.codeset))
        
        if len(self.pcode) > 0:
            self.pcode = sorted(list(self.pcode))[0]
        else:
            self.pcode = None
            
        self.owner = self.owners(None)
        self.colony = self.colonies(None)
        
        self.dcode = list(self.dcode) + self.colony + self.owner
        self.dcode = sorted(self.dcode)

    def __str__(self):
        return u" ".join(self.codeset + self.dcode)
        
    def calculate_pcode(self):
        return self.pcode
   
    def _check_planet_code(self, star, code, size, atmo, hydro):
        size = '0123456789ABC' if size is None else size
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        check = True
        if star.size in size and star.atmo in atmo and star.hydro in hydro \
            and code not in self.codeset:
            self.logger.error(u'{}-{} Calculated "{}" not in trade codes {}'.format(star, star.uwp, code, self.codeset))
            check = False
        if code in self.codeset and \
            not (star.size in size and star.atmo in atmo and star.hydro in hydro):
            self.logger.error(u'{}-{} Found invalid "{}" in trade codes: {}'.format(star, star.uwp, code, self.codeset))
            check = False
        return check


    def _check_pop_code(self, star, code, pop):
        check = True
        if star.pop in pop and code not in self.codeset:
            self.logger.error(u'{} - Calculated "{}" not in trade codes {}'.format(star, code, self.codeset))
            check = False
        if code in self.codeset and star.pop not in pop:
            self.logger.error(u'{} - Found invalid "{}" code on world with {} population: {}'.format(star, code, star.pop, self.codeset))
            check = False
        return check


    def _check_econ_code(self, star, code, atmo, hydro, pop):
        atmo = '0123456789ABCDEF' if atmo is None else atmo
        hydro = '0123456789A' if hydro is None else hydro
        pop = '0123456789ABC' if pop is None else pop
        check = True
        if star.atmo in atmo and star.hydro in hydro and star.pop in pop \
            and code not in self.codeset:
            self.logger.error(u'{}-{} Calculated "{}" not in trade codes {}'.format(star, star.uwp, code, self.codeset))
            check = False
        if code in self.codeset and \
            not (self.atmo in atmo and self.hydro in hydro and self.pop in pop):
            self.logger.error(u'{}-{} Found invalid "{}" in trade codes: {}'.format(star, star.uwp, code, self.codeset))
            check = False
        return check
    
    
    def check_world_codes(self, star):
        check = True
        check = self._check_planet_code(star, 'As', '0', '0', '0') and check
        check = self._check_planet_code(star, 'De', None, '23456789', '0') and check
        check = self._check_planet_code(star, 'Fl', None, 'ABC', '123456789A') and check
        check = self._check_planet_code(star, 'Ga', '678', '568', '567') and check
        check = self._check_planet_code(star, 'He', '3456789ABC', '2479ABC', '012') and check
        check = self._check_planet_code(star, 'Ic', None, '01', '123456789A') and check
        check = self._check_planet_code(star, 'Po', None, '2345', '0123') and check
        check = self._check_planet_code(star, 'Oc', 'ABCD', '3456789', 'A') and check
        check = self._check_planet_code(star, 'Va', None, '0', None) and check
        check = self._check_planet_code(star, 'Wa', '3456789', '3456789', 'A') and check

        #self._check_pop_code('Ba', '0')
        check = self._check_pop_code(star, 'Lo', '123') and check
        check = self._check_pop_code(star, 'Ni', '456') and check
        check = self._check_pop_code(star, 'Ph', '8') and check
        check = self._check_pop_code(star, 'Hi', '9ABC') and check

        check = self._check_econ_code(star, 'Pa', '456789', '45678', '48') and check
        check = self._check_econ_code(star, 'Ag', '456789', '45678', '567') and check
        check = self._check_econ_code(star, 'Na', '0123', '0123', '6789ABC') and check
        check = self._check_econ_code(star, 'Pi', '012479', None, '78') and check
        check = self._check_econ_code(star, 'In', '012479ABC', None, '9ABC') and check
        check = self._check_econ_code(star, 'Pr', '68', None,'59') and check
        check = self._check_econ_code(star, 'Ri', '68', None, '678') and check
        return check
    
    def owned_by(self, star):
        self.ownedBy = self
        if star.gov == '6': 
            self.ownedBy = None
        for code in self.dcode:
            if code.startswith(u'O:'):
                if len(code) == 2:
                    self.ownedBy = 'XXXX'
                else:
                    self.ownedBy = code[2:]
                break
            elif code.startswith(u'Mr'):
                self.ownedBy = 'Mr'
            elif code.startswith(u'Re'):
                self.ownedBy = 'Re'
            elif code.startswith(u'Px'):
                self.ownedBy = 'Px'
        if (star.gov == '6' and not self.ownedBy) or (star.gov != '6' and self.ownedBy != self):
            self.logger.debug (u"{} has incorrect government code {} - {}".format(star, star.gov, self.dcode))
        return self.owned_by
    
    
    def owners(self, sector_name):
        if not sector_name:
            return [code for code in self.owned if code.startswith('O:')]
        else:
            return [code if len(code) > 6 else u'O:'+ sector_name[0:4] + u'-' + code[2:]
                  for code in self.owned if code.startswith(u'O:')]
        
    def colonies(self,sector_name):
        if not sector_name:
            return [code for code in self.owned if code.startswith(u'C:')]
        else: 
            return [code if len(code) > 6 else u'C:'+ sector_name[0:4] + u'-' + code[2:]
                 for code in self.owned if code.startswith(u'C:')]

    @property
    def homeworld(self):
        return self.sophonts if len(self.sophonts) > 0 else None
        
    @property
    def rich(self):
        return 'Ri' in self.codeset
    
    @property
    def industrial(self):
        return 'In' in self.codeset
    
    @property
    def agricultural(self):
        return 'Ag' in self.codeset
    
    @property
    def poor(self):
        return 'Po' in self.codeset
    
    @property
    def nonagricultural (self):
        return 'Na' in self.codeset

    @property
    def barren (self):
        return 'Ba' in self.codeset

    @property
    def low(self):
        return 'Lo' in self.codeset

    @property
    def nonindustrial(self):
        return 'Ni' in self.codeset
    
    @property
    def high (self):
        return 'Hi' in self.codeset

    @property
    def asteriod (self):
        return 'As' in self.codeset

    @property
    def extreme (self):
        return len(self.ex_codes & set(self.dcode)) > 0
    
    @property
    def capital (self):
        return 'Cp' in self.dcode or 'Cx' in self.dcode or 'Cs' in self.dcode

    @property
    def subsector_capital (self):
        return 'Cp' in self.dcode
    
    @property
    def sector_capital (self):
        return 'Cs' in self.dcode
    
    @property
    def other_capital (self):
        return 'Cx' in self.dcode
    
    @property
    def research_station (self):
        return set(self.research.keys()).intersection(self.dcode)
    
    @property
    def research_station_char(self):
        stations = self.research_station
        if len(stations) == 1:
            station = next(iter(self.research_station))
            return self.research[station]
        else:
            return None

    @property
    def pcode_color(self):
        return self.pcolor.get(self.pcode, '#44ff44')
