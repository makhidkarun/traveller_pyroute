#!/usr/bin/python
'''
Created on Apr 26, 2015

@author: tjoneslo
'''

# Requires wikitools and poster to run correctly
# pip install wikitools
# pip install poster 
#
#
from wikitools import wiki
from wikitools import api
from wikitools.wikifile import File
from wikitools.page import Page, NoPage
import logging
import argparse
import warnings
import os
import codecs
import glob
import re
from itertools import izip
import traceback

logger = logging.getLogger('WikiUpload')

def uploadSummaryText(site, summaryFile, era):
    try:
        lines = [line for line in codecs.open(summaryFile,'r', 'utf-8')]
    except (OSError, IOError):
        logger.error(u"Summary file not found: {}".format(summaryFile))
        return 
    index = [i for i,n in enumerate(lines) if 'Statistics' in n][0]
    lines = lines[index + 3:]
    index = 1
    
    while True:
        baseTitle = lines[index].split('|')[1]
        if not baseTitle.startswith('[['):
            logger.info(u"Upload Summary for {} not a page, skipped".format(baseTitle))
            while (not (lines[index].startswith('|-') or lines[index].startswith('|}'))):
                index += 1
            if lines[index].startswith('|}'):
                break    
            index += 1   
            continue
        else:
            baseTitle = baseTitle.strip('[')
        targetTitle= u"{}/summary".format(baseTitle)
        index += 1
        text = lines[index][3:]
        index += 1
        while (not (lines[index].startswith('|-') or lines[index].startswith('|}'))):
            text += lines[index]
            index += 1

        target_page = None
        try:
            target_page = Page(site, targetTitle)
            categories = target_page.getCategories(True)
            if 'Category:Meta' in categories:
                targetTitle += u'/{}'.format(era)
                target_page = Page(site, targetTitle) 
        except api.APIError as e:
            if e.args[0] == 'missingtitle':
                logger.error(u"UploadSummary for page {}, page does not exist, skipped".format(baseTitle))
                index += 1
                continue
            else:
                logger.error(u"UploadSummary for page {} got exception {} ".format(baseTitle, e))
                return
        except NoPage as e:
            logger.error(u"UploadSummary for page {}, page does not exist, skipped".format(baseTitle))
            index += 1
            continue
        
        try:
            result = target_page.edit(text=text, summary='Trade Map update summary', 
                                      bot=True, nocreate=True,skipmd5=True)
    
            if result['edit']['result'] == 'Success':
                logger.info(u'Saved: {}'.format(targetTitle))
            else:
                logger.info(u'Save failed {}'.format(targetTitle)) 
        except api.APIError as e:
            if e.args[0] == 'missingtitle':
                logger.error(u"UploadSummary for page {}, page does not exist, skipped".format(baseTitle))
            else:
                logger.error(u"UploadSummary for page {} got exception {} ".format(baseTitle, e))
        except NoPage as e:
            logger.error(u"UploadSummary for page {}, page does not exist, skipped".format(baseTitle))
            
        if lines[index].startswith('|}'):
            break       
        index += 1
        
def uploadPDF(site, filename):
    with open(filename, "rb") as f:        
        try:
            page = File (site, os.path.basename(filename))
            result = page.upload(f, "{{Trade map disclaimer}}", ignorewarnings=True)
            if result['upload']['result'] == 'Success':
                logger.info(u'Saved: {}'.format(filename))
            else:
                logger.error(u'Save failed {}'.format(filename)) 
        except Exception as e:
            logger.error("UploadPDF for {} got exception: {}".format(filename, e))
            traceback.print_exc()

def uploadSec (site, filename, place, era):
    with codecs.open(filename, "r", 'utf-8') as f:
        text = f.read()
    target_page=None
    try :
        targetTitle = os.path.basename(filename).split('.')[0] + place    
        target_page = Page(site, targetTitle)
        categories = target_page.getCategories(True)
        if 'Category:Meta' in categories:
            targetTitle += u'/{}'.format(era)
            target_page = Page(site, targetTitle) 
    except api.APIError as e:
        if e.args[0] == 'missingtitle':
            logger.error(u"UploadSummary for page {}, page does not exist, skipped".format(targetTitle))
        else:
            logger.error(u"UploadSummary for page {} got exception {} ".format(targetTitle, e))
        return
    except NoPage as e:
        logger.error(u"UploadSummary for page {}, page does not exist, skipped".format(targetTitle))
        return
    
    try:        
        result = target_page.edit(text=text, summary='Trade Map update sector data', 
                                  bot=True, nocreate=True, skipmd5=True)
        if result['edit']['result'] == 'Success':
            logger.info(u'Saved: {}'.format(targetTitle))
        else:
            logger.error('Save failed {}'.format(targetTitle)) 
    except Exception as e:
        logger.error("uploadSec for {} got exception: {}".format(filename, e))

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)
    
def uploadWorlds (site, sectorFile, economicFile, era):
    data_template=u'''
{{{{StellarData
 |world     = {0}
 |sector    = {1}
 |subsector = {2}
 |era       = {31}
 |hex       = {3}
 |name      = {4}
 |UWP       = {5}
 |pcode     = {6}
 |codes     = {7}
 |sophonts  = {8}
 |details   = {9}
 |ix        = {10}
 |ex        = {11}
 |cx        = {12}
 |nobility  = {13}
 |bases     = {14}
 |zone      = {15}
 |popmul    = {16}
 |belts     = {17}
 |giants    = {18}
 |worlds    = {19}
 |aleg      = {20}
 |stars     = {21}
 |wtn       = {22}
 |ru        = {23}
 |gwp       = {24}
 |trade     = {25}
 |pass      = {26}
 |build     = {27}
 |army      = {28}
 |portSize  = {29}
 |spa       = {30}
 |mspr      = {32}
}}}}'''
    
    page_template = u'''{{{{StellarDataQuery|name={{{{World|{0}|{1}|{2}|{3}}}}} }}}}

== Astrography and planetology ==
No information yet available. 
 
== History and background ==
No information yet available. 

== References and contributors ==
{{{{Incomplete}}}}
{{{{Source}}}}
{{{{LEN}}}}
'''
    try:
        sectorLines = [line for line in codecs.open(sectorFile,'r', 'utf-8')]
    except (OSError, IOError):
        logger.error(u"Sector file not found: {}".format(sectorFile))
        return

    sectorData = [line.split(u"||") for line in sectorLines[5:]
                  if not (line.startswith(u'|-') or line.startswith(u'<section')
                          or line.startswith(u'|}') or line.startswith(u'[[Category:'))]

    try:
        economicLines = [line for line in codecs.open(economicFile, 'r', 'utf-8')]
    except (OSError, IOError):
        logger.error(u"Economic file not found: {}".format(economicFile))
        return
    economicData = [line.split(u"||") for line in economicLines[5:]
                    if not(line.startswith(u'|-') or line.startswith(u'<section') 
                           or line.startswith(u'|}') or line.startswith(u'[[Category:'))]

    sectorName = economicLines[2][3:-15]
    logger.info( u"Uploading {}".format(sectorName))
    for sec, eco in zip (sectorData, economicData):
        
        if not sec[0] == eco[0]:
            logger.error(u"{} is not equal to {}".format(sec[0], eco[0]))
            break
        subsectorName = eco[14].split(u'|')[1].strip(u'\n').strip(u']')
        pcodes = ['As', 'De', 'Ga', 'Fl', 'He', 'Ic', 'Oc', 'Po', 'Va', 'Wa']
        dcodes = ['Cp', 'Cx', 'Cs', 'Mr', 'Da', 'Di', 'Pz', 'An', 'Ab', 'Fo', 'Px', 
                  'Re', 'Rs', 'Sa', 'Tz', 'Lk', 
                  'RsA', 'RsB','RsG','RsD','RsE','RsZ', 'RsT',
                  'Fr', 'Co', 'Tp', 'Ho', 'Tr', 'Tu',
                  'Cm', 'Tw' ]
        codes = sec[3].split()
        pcode = set(pcodes) & set(codes)
        dcode = set(dcodes) & set(codes)

        owned = [code for code in codes if code.startswith(u'O:') or code.startswith(u'C:')]
        homeworlds = re.findall(ur"\([^)]+\)\S?", sec[3], re.U)
        
        codeCheck = set(codes) - dcode - set(owned) - set(homeworlds)
        sophCodes = [code for code in codeCheck if len(code)>4]
        
        sophonts = homeworlds + sophCodes
        
        codeset = set(codes) - dcode - set(owned) - set(sophCodes) - set(homeworlds)

        if len(pcode) > 0:
            pcode = sorted(list(pcode))[0]
        else:
            pcode = ''

        colony = [code if len(code) > 6 else u'O:'+ sectorName[0:4] + u'-' + code[2:]
                 for code in owned if code.startswith(u'O:')]
        parent =  [code if len(code) > 6 else u'C:'+ sectorName[0:4] + u'-' + code[2:]
                 for code in owned if code.startswith(u'C:')]
        dcode = list(dcode) + colony + parent

        starparts = sec[13].split()
        stars = []

        for x,y in pairwise ( starparts ):
            if y in ['V', 'IV', 'Ia', 'Ib', 'II', 'III']:
                stars.append(' '.join((x,y)))
            else:
                stars.append(x)
                stars.append(y)
        if len(starparts) % 2 == 1:
            stars.append(starparts[-1])

        hexNo = sec[0].strip(u'|').strip()
        worldPage = eco[1].strip() + u" (world)"
        try:
            target_page = Page(site, worldPage)
            # First, check if this is a disambiguation page, if so generate
            # the alternate (location) name
            categories = target_page.getCategories(True)
            if 'Category:Disambiguation pages' in categories:
                worldName = worldPage.split(u'(')
                shortName = shortNames[sectorName]
                worldPage = worldName[0] + u'('+ shortName + u' ' + hexNo + u') (' + worldName[1]
                target_page = Page(site, worldPage)
                
            # Second, check if this page was redirected to another page
            if target_page.title != worldPage:
                logger.info(u"Redirect {} to {}".format(worldPage, target_page.title))
                worldPage = target_page.title
                
        except NoPage:
            logger.info( u"Missing Page: {}".format(worldPage))
            page_data = page_template.format(eco[1].strip(), sectorName, subsectorName, hexNo)
            target_page = Page(site, worldPage)
            try:
                result = target_page.edit(text=page_data, summary='Trade Map update created world page', 
                                      bot=True, skipmd5=True)

                if result['edit']['result'] == 'Success':
                    logger.info(u'Saved: {}'.format(worldPage))
            except api.APIError as e:
                logger.error(u"UploadSummary for page {} got exception {} ".format(worldPage, e))
                continue

        data = data_template.format(eco[1].strip(),                   # World
                                    sectorName,                       # Sector
                                    subsectorName,                    # Subsector
                                    hexNo,                            # hex
                                    worldPage,                        # Name
                                    sec[2].strip(),                   # UWP
                                    pcode,                            # pcode
                                    u','.join(sorted(list(codeset))), # codes
                                    u','.join(sophonts),              # sophonts
                                    u','.join(sorted(list(dcode))),   # details
                                    sec[4].strip(u'{}'),              # ix (important)
                                    sec[5].strip(u'()'),              # ex (Economiv)
                                    sec[6].strip(u'[]'),              # cx (cultureal)
                                    sec[7].strip(),                   # nobility
                                    sec[8].strip(),                   # bases
                                    sec[9].strip(),                   # Zone
                                    sec[10][0],                       # pop mult
                                    sec[10][1],                       # Belts
                                    sec[10][2],                       # GG Count
                                    sec[11],                          # Worlds
                                    sec[12],                          # Alegiance
                                    u','.join(stars),                 # stars
                                    int(eco[5].strip()),              # wtn
                                    eco[6].strip(),                   # RU
                                    eco[7].strip(),                   # GWP
                                    eco[8].strip(),                   # Trade
                                    eco[9].strip(),                   # Passengers
                                    eco[10].strip(),                  # build capacity
                                    eco[11].strip(),                  # Army
                                    eco[12].strip(),                  # port size
                                    eco[13].strip(),                  # spa population
                                    era,                              # era
                                    eco[14].strip()                   # MSPR
                                    )
        try:
            target_page = Page(site,  worldPage + u'/data')
            if target_page.exists:
                page_text = unicode(target_page.getWikiText(), 'utf-8')
                templates = re.findall (ur"{{[^}]*}}", page_text, re.U)
                era_name = u"|era       = {}".format(era)
                newtemplates = [template if not era_name in template else data
                                for template in templates]
                newdata = u'\n'.join(newtemplates) 
                if era_name not in newdata:
                    newtemplates.insert(0, data)
                    newdata = u'\n'.join(newtemplates)
                
                if newdata == page_text:
                    logger.info(u'No changes to template: skipping {}'.format(worldPage)) 
                    continue            
                data = newdata
            result = target_page.edit(text=data, summary='Trade Map update world data', 
                                      bot=True, skipmd5=True)

            if result['edit']['result'] == 'Success':
                logger.info(u'Saved: {}/data'.format(worldPage))
            else:
                logger.error(u'Save failed {}/data'.format(worldPage))
        except api.APIError as e:
            if e.args[0] == 'missingtitle':
                logger.error(u"UploadSummary for page {}, page does not exist".format(worldPage))
            else:
                logger.error(u"UploadSummary for page {} got exception {} ".format(worldPage, e))

shortNames = {u'Dagudashaag': u'Da', u'Deneb': u'De', 
              u'Empty Quarter': u'EQ', u'Spinward Marches': u'SM',
              u'Knoellighz': u'Kn' }

def set_logging(level):
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def process():
    warnings.simplefilter("always")

    parser = argparse.ArgumentParser(description='Trade map generator wiki upload.')
    parser.add_argument('--input', default='../maps', help='output directory for maps, statistics')
    parser.add_argument('--no-maps', dest='maps', default=True, action='store_false')
    parser.add_argument('--no-secs', dest='secs', default=True, action='store_false')
    parser.add_argument('--no-summary', dest='summary', default=True, action='store_false')
    parser.add_argument('--no-subsector', dest='subsector', default=True, action='store_false')
    parser.add_argument('--worlds', default=None)
    parser.add_argument('--site', dest='site', default='http://wiki.travellerrpg.com/api.php')
    parser.add_argument('--era', dest='era', default='Milieu 1116')
    parser.add_argument('--log-level', default='INFO')
    
    args = parser.parse_args()
    set_logging(args.log_level)

    # create a Wiki object
    site = wiki.Wiki(args.site)
    #site = wiki.Wiki("http://localhost/wiki/api.php")
    site.login("AB-101", remember=True)

    if args.maps:
        path = os.path.join(args.input, "*Sector.pdf")
        for f in glob.glob(path):
            uploadPDF(site, f)

    if args.secs:        
        path = os.path.join(args.input, "*Sector.economic.wiki")
        for f in glob.glob(path):
            uploadSec (site, f, "/economic", args.era)
        path = os.path.join(args.input, "*Sector.sector.wiki")
        for f in glob.glob(path):
            uploadSec (site, f, "/sector", args.era)

    if args.summary:
        path = os.path.join(args.input, "summary.wiki")
        uploadSummaryText(site, path, args.era)
    if args.subsector:
        path = os.path.join(args.input, "subsector_summary.wiki")
        uploadSummaryText(site, path, args.era)

    if args.worlds:
        path = os.path.join(args.input, "{0} Sector.economic.wiki".format(args.worlds))
        logger.debug("Checking Path {} -> {}".format(path, glob.glob(path)))

        for eco in glob.glob(path):
            sector = args.worlds
            if sector in shortNames.keys():
                sec = eco.replace('Sector.economic.wiki', 'Sector.sector.wiki')
                uploadWorlds(site, sec, eco, args.era)

if __name__ == '__main__':
    process()
