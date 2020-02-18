#!/usr/bin/python
"""
Created on Apr 26, 2015

@author: tjoneslo
"""

# Requires wikitools and poster to run correctly
# pip install wikitools
# pip install poster 
#
#
from wikitools_py3.exceptions import WikiError, NoPage
from wikitools_py3.page import Page
from WikiReview import WikiReview

import logging
import argparse
import warnings
import os
import codecs
import glob
import re

logger = logging.getLogger('WikiUpload')


def uploadSummaryText(site, summaryFile, era, area_name):
    with codecs.open(summaryFile, 'r', 'utf-8') as f:
        lines = f.readlines()

    name = 'initial table'
    stats_text = {name:[]}

    for line in lines:
        if "statistics ==" in line:
            name = line.strip().strip('=').replace('statistics', '').strip()
            stats_text[name] = []
        else:
            stats_text[name].append(line)

    logger.info("uploading summary articles: %s", " ".join(stats_text.keys()))

    for name, lines in stats_text.items():
        targetTitle = "{} {}/summary".format(name, area_name)
        target_page = site.get_page(targetTitle)
        if target_page and 'Category:Meta' in target_page.getCategories(True):
            targetTitle += '/{}'.format(era)
            target_page = site.get_page(targetTitle)

        if not target_page:
            continue
        text = "".join(lines)
        site.save_page(target_page, text, 'Trade Map update summary')


def uploadSec(site, filename, place, era):
    with codecs.open(filename, "r", 'utf-8') as f:
        text = f.read()
    targetTitle = os.path.basename(filename).split('.')[0] + place
    target_page = site.get_page(targetTitle)
    if target_page and 'Category:Meta' in target_page.getCategories(True):
        targetTitle += '/{}'.format(era)
        target_page = site.get_page(targetTitle)

    if not target_page:
        return

    site.save_page(target_page, text, 'Trade Map update sector data')


def pairwise(iterable):
    """
    s -> (s0, s1), (s2, s3), (s4, s5), ...
    """
    a = iter(iterable)
    return list(zip(a, a))


def uploadWorlds(site, sectorFile, economicFile, era):
    data_template = '''
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

    page_template = '''{{{{StellarDataQuery|name={{{{World|{0}|{1}|{2}|{3}}}}} }}}}

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
        sectorLines = [line for line in codecs.open(sectorFile, 'r', 'utf-8')]
    except (OSError, IOError):
        logger.error("Sector file not found: {}".format(sectorFile))
        return

    sectorData = [line.split("||") for line in sectorLines[5:]
                  if not (line.startswith('|-') or line.startswith('<section')
                          or line.startswith('|}') or line.startswith('[[Category:'))]

    try:
        economicLines = [line for line in codecs.open(economicFile, 'r', 'utf-8')]
    except (OSError, IOError):
        logger.error("Economic file not found: {}".format(economicFile))
        return
    economicData = [line.split("||") for line in economicLines[5:]
                    if not (line.startswith('|-') or line.startswith('<section')
                            or line.startswith('|}') or line.startswith('[[Category:'))]

    sectorName = economicLines[2][3:-15]
    logger.info("Uploading {}".format(sectorName))
    for sec, eco in zip(sectorData, economicData):

        if not sec[0] == eco[0]:
            logger.error("{} is not equal to {}".format(sec[0], eco[0]))
            break
        subsectorName = eco[14].split('|')[1].strip('\n').strip(']')
        pcodes = ['As', 'De', 'Ga', 'Fl', 'He', 'Ic', 'Oc', 'Po', 'Va', 'Wa']
        dcodes = ['Cp', 'Cx', 'Cs', 'Mr', 'Da', 'Di', 'Pz', 'An', 'Ab', 'Fo', 'Px',
                  'Re', 'Rs', 'Sa', 'Tz', 'Lk',
                  'RsA', 'RsB', 'RsG', 'RsD', 'RsE', 'RsZ', 'RsT',
                  'Fr', 'Co', 'Tp', 'Ho', 'Tr', 'Tu',
                  'Cm', 'Tw']
        codes = sec[3].split()
        pcode = set(pcodes) & set(codes)
        dcode = set(dcodes) & set(codes)

        owned = [code for code in codes if code.startswith('O:') or code.startswith('C:')]
        homeworlds = re.findall(r"\([^)]+\)\S?", sec[3], re.U)

        codeCheck = set(codes) - dcode - set(owned) - set(homeworlds)
        sophCodes = [code for code in codeCheck if len(code) > 4]

        sophonts = homeworlds + sophCodes

        codeset = set(codes) - dcode - set(owned) - set(sophCodes) - set(homeworlds)

        if len(pcode) > 0:
            pcode = sorted(list(pcode))[0]
        else:
            pcode = ''

        colony = [code if len(code) > 6 else 'O:' + sectorName[0:4] + '-' + code[2:]
                  for code in owned if code.startswith('O:')]
        parent = [code if len(code) > 6 else 'C:' + sectorName[0:4] + '-' + code[2:]
                  for code in owned if code.startswith('C:')]
        dcode = list(dcode) + colony + parent

        starparts = sec[13].split()
        stars = []

        for x, y in pairwise(starparts):
            if y in ['V', 'IV', 'Ia', 'Ib', 'II', 'III']:
                stars.append(' '.join((x, y)))
            else:
                stars.append(x)
                stars.append(y)
        if len(starparts) % 2 == 1:
            stars.append(starparts[-1])

        hexNo = sec[0].strip('|').strip()
        worldPage = eco[1].strip() + " (world)"

        worldName = worldPage.split('(')
        shortName = shortNames[sectorName]
        worldPage = worldName[0] + '(' + shortName + ' ' + hexNo + ') (' + worldName[1]

        site.search_disambig = worldName
        target_page = site.get_page(worldPage)

        pages = [target_page] if not isinstance(target_page, (list, tuple)) else target_page

        for page in pages:
            pass

        try:
            target_page = Page(site, worldPage)
            # First, check if this is a disambiguation page, if so generate
            # the alternate (location) name
            categories = target_page.getCategories(True)
            if 'Category:Disambiguation pages' in categories:
                worldName = worldPage.split('(')
                shortName = shortNames[sectorName]
                worldPage = worldName[0] + '(' + shortName + ' ' + hexNo + ') (' + worldName[1]
                target_page = Page(site, worldPage)

            # Second, check if this page was redirected to another page
            if target_page.title != worldPage:
                logger.info("Redirect {} to {}".format(worldPage, target_page.title))
                worldPage = target_page.title

        except NoPage:
            logger.info("Missing Page: {}".format(worldPage))
            page_data = page_template.format(eco[1].strip(), sectorName, subsectorName, hexNo)
            target_page = Page(site, worldPage)
            try:
                result = target_page.edit(text=page_data, summary='Trade Map update created world page',
                                          bot=True, skipmd5=True)

                if result['edit']['result'] == 'Success':
                    logger.info('Saved: {}'.format(worldPage))
            except WikiError as e:
                logger.error("UploadSummary for page {} got exception {} ".format(worldPage, e))
                continue

        data = data_template.format(eco[1].strip(),  # World
                                    sectorName,  # Sector
                                    subsectorName,  # Subsector
                                    hexNo,  # hex
                                    worldPage,  # Name
                                    sec[2].strip(),  # UWP
                                    pcode,  # pcode
                                    ','.join(sorted(list(codeset))),  # codes
                                    ','.join(sophonts),  # sophonts
                                    ','.join(sorted(list(dcode))),  # details
                                    sec[4].strip('{}'),  # ix (important)
                                    sec[5].strip('()'),  # ex (economic)
                                    sec[6].strip('[]'),  # cx (cultural)
                                    sec[7].strip(),  # nobility
                                    sec[8].strip(),  # bases
                                    sec[9].strip(),  # Zone
                                    sec[10][0],  # pop mult
                                    sec[10][1],  # Belts
                                    sec[10][2],  # GG Count
                                    sec[11],  # Worlds
                                    sec[12],  # Allegiance
                                    ','.join(stars),  # stars
                                    int(eco[5].strip()),  # wtn
                                    eco[6].strip(),  # RU
                                    eco[7].strip(),  # GWP
                                    eco[8].strip(),  # Trade
                                    eco[9].strip(),  # Passengers
                                    eco[10].strip(),  # build capacity
                                    eco[11].strip(),  # Army
                                    eco[12].strip(),  # port size
                                    eco[13].strip(),  # spa population
                                    era,  # era
                                    eco[14].strip()  # MSPR
                                    )
        try:
            target_page = Page(site, worldPage + '/data')
            if target_page.exists:
                page_text = str(target_page.getWikiText(), 'utf-8')
                templates = re.findall(r"{{[^}]*}}", page_text, re.U)
                era_name = "|era       = {}".format(era)
                newtemplates = [template if not era_name in template else data
                                for template in templates]
                newdata = '\n'.join(newtemplates)
                if era_name not in newdata:
                    newtemplates.insert(0, data)
                    newdata = '\n'.join(newtemplates)

                if newdata == page_text:
                    logger.info('No changes to template: skipping {}'.format(worldPage))
                    continue
                data = newdata
            result = target_page.edit(text=data, summary='Trade Map update world data',
                                      bot=True, skipmd5=True)

            if result['edit']['result'] == 'Success':
                logger.info('Saved: {}/data'.format(worldPage))
            else:
                logger.error('Save failed {}/data'.format(worldPage))
        except WikiError as e:
            if e.args[0] == 'missingtitle':
                logger.error("UploadSummary for page {}, page does not exist".format(worldPage))
            else:
                logger.error("UploadSummary for page {} got exception {} ".format(worldPage, e))


shortNames = {'Dagudashaag': 'Da', 'Deneb': 'De',
              'Empty Quarter': 'EQ', 'Spinward Marches': 'SM',
              'Knoellighz': 'Kn'}


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
    parser.add_argument('--no-maps', dest='maps', default=True, action='store_false',
                        help="Don't upload the sector PDF maps, default is upload the maps")
    parser.add_argument('--no-secs', dest='secs', default=True, action='store_false',
                        help="Don't upload the sector table pages, default is to upload the sector table pages")
    parser.add_argument('--no-summary', dest='summary', default=True, action='store_false',
                        help="Don't upload the sector summary pages, default is to upload the sector summary pages")
    parser.add_argument('--no-subsector', dest='subsector', default=True, action='store_false',
                        help="Don't upload the subsector summary pages, default is to upload the subsector summary pages")
    parser.add_argument('--worlds', default=False, action='store_true',
                        help="Upload the data for individual worlds, default is to not upload world data")
    parser.add_argument('--era', dest='era', default='Milieu 1116',
                        help="Set the era for the world upload data, default [Milieu 1116]")
    parser.add_argument('--log-level', default='INFO')
    parser.add_argument('--site', dest='site', default='https://wiki.travellerrpg.com/api.php')
    parser.add_argument('--user', default='AB-101',
                        help="(Bot) user to connect to the wiki and perform the uploads, default [AB-101]")

    args = parser.parse_args()
    set_logging(args.log_level)

    site = WikiReview.get_site(args.user, args.site)
    wiki_review = WikiReview(site, None, False, None)

    # create a Wiki object
    # site = wiki.Wiki(args.site)
    # site = wiki.Wiki("http://localhost/wiki/api.php")
    # site.login(args.user, remember=True)

    if args.maps:
        path = os.path.join(args.input, "*Sector.pdf")
        for f in glob.glob(path):
            wiki_review.upload_file(f)

    if args.secs:
        path = os.path.join(args.input, "*Sector.economic.wiki")
        for f in glob.glob(path):
            uploadSec(wiki_review, f, "/economic", args.era)
        path = os.path.join(args.input, "*Sector.sector.wiki")
        for f in glob.glob(path):
            uploadSec(wiki_review, f, "/sector", args.era)

    if args.summary:
        path = os.path.join(args.input, "sectors.wiki")
        uploadSummaryText(wiki_review, path, args.era, "Sector")
    if args.subsector:
        path = os.path.join(args.input, "subsectors.wiki")
        uploadSummaryText(wiki_review, path, args.era, "Subsector")

    if args.worlds:
        path = os.path.join(args.input, "{0} Sector.economic.wiki".format(args.worlds))
        logger.debug("Checking Path {} -> {}".format(path, glob.glob(path)))

        for eco in glob.glob(path):
            sector = args.worlds
            if sector in list(shortNames.keys()):
                sec = eco.replace('Sector.economic.wiki', 'Sector.sector.wiki')
                uploadWorlds(wiki_review, sec, eco, args.era)


if __name__ == '__main__':
    process()
