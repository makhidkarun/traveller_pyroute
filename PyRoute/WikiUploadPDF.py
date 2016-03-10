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
import argparse
import warnings
import os
import codecs
import glob
import time
from itertools import izip

def uploadSummaryText(site, summaryFile):
    try:
        lines = [line for line in codecs.open(summaryFile,'r', 'utf-8')]
    except (OSError, IOError):
        print "Summary file not found: {}".format(summaryFile)
        return 
    index = [i for i,n in enumerate(lines) if 'Statistics' in n][0]
    lines = lines[index + 3:]
    index = 1
    
    while True:
        baseTitle = lines[index].split('|')[1]
        if not baseTitle.startswith('[['):
            print "Upload Summary for {} not a page, skipped".format(baseTitle)
            while (not (lines[index].startswith('|-') or lines[index].startswith('|}'))):
                index += 1
            if lines[index].startswith('|}'):
                break    
            index += 1   
            continue
        else:
            baseTitle = baseTitle.strip('[')
        targetTitle= "{}/summary".format(baseTitle)
        index += 1
        text = lines[index][3:]
        index += 1
        while (not (lines[index].startswith('|-') or lines[index].startswith('|}'))):
            text += lines[index]
            index += 1

        try:
            target_page = Page(site, targetTitle)
            result = target_page.edit(text=text, summary='Trade Map update sector summary', 
                                      bot=True, nocreate=True,skipmd5=True)
    
            if result['edit']['result'] == 'Success':
                print 'Saved: {}'.format(targetTitle)
            else:
                print 'Save failed {}'.format(targetTitle) 
        except api.APIError as e:
            if e.args[0] == 'missingtitle':
                print "UploadSummary for page {}, page does not exist, skipped".format(baseTitle)
            else:
                print "UploadSummary for page {} got exception {} ".format(baseTitle, e)
            
        if lines[index].startswith('|}'):
            break       
        index += 1
        
def uploadPDF(site, filename):
    with open(filename, "rb") as f:        
        try:
            page = File (site, os.path.basename(filename))
            result = page.upload(f, "{{Trade map disclaimer}}", ignorewarnings=True)
            if result['upload']['result'] == 'Success':
                print 'Saved: {}'.format(filename)
            else:
                print 'Save failed {}'.format(filename) 
        except Exception as e:
            print "UploadPDF for {} got exception: {}".format(filename, e)
#            traceback.print_exc()
    

def uploadSec (site, filename, place):
    with codecs.open(filename, "r", 'utf-8') as f:
        text = f.read()
    try :
        targetTitle = os.path.basename(filename).split('.')[0] + place    
        target_page = Page(site, targetTitle)
        result = target_page.edit(text=text, summary='Trade Map update sector data', 
                                  bot=True, nocreate=True, skipmd5=True)
        if result['edit']['result'] == 'Success':
            print 'Saved: {}'.format(targetTitle)
        else:
            print 'Save failed {}'.format(targetTitle) 
    except Exception as e:
        print "uploadSec for {} got exception: {}".format(filename, e)

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)
    
def uploadWorlds (site, sectorFile, economicFile):
    data_template=u'''
{{{{StellarData
 |world     = {0}
 |sector    = {1}
 |subsector = {2}
 |era       = Milieu 1116
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
}}}}'''

    try:
        sectorLines = [line for line in codecs.open(sectorFile,'r', 'utf-8')]
    except (OSError, IOError):
        print "Sector file not found: {}".format(sectorFile)
        return

    sectorData = [line.split(u"||") for line in sectorLines[5:]
                  if not (line.startswith(u'|-') or line.startswith(u'<section')
                          or line.startswith(u'|}') or line.startswith(u'[[Category:'))]

    try:
        economicLines = [line for line in codecs.open(economicFile, 'r', 'utf-8')]
    except (OSError, IOError):
        print "Economic file not found: {}".format(economicFile)
        return
    economicData = [line.split(u"||") for line in economicLines[5:]
                    if not(line.startswith(u'|-') or line.startswith(u'<section') 
                           or line.startswith(u'|}') or line.startswith(u'[[Category:'))]

    sectorName = economicLines[2][3:-15]
    for sec, eco in zip (sectorData, economicData):
        if not sec[0] == eco[0]:
            print "{} is not equal to {}".format(sec[0], eco[0])
            break
        pcodes = ['As', 'De', 'Fl', 'He', 'Ic', 'Oc', 'Va', 'Wa']
        dcodes = ['Cp', 'Cx', 'Cs', 'Mr', 'Da', 'Pz', 'An', 'Ab', 'Fo', 'Re', 'Sa', 'Tz']
        codes = sec[3].split()
        pcode = set(pcodes) & set(codes)
        dcode = set(dcodes) & set(codes)

        sophonts = [code for code in codes if len(code) >= 4 and not code.startswith(u'O:')]
        owned = [code for code in codes if code.startswith(u'O:')]

        codeset = set(codes) - set(sophonts) - dcode - set(owned)
        dcode = list(dcode) + owned

        if len(pcode) > 0:
            pcode = pcode.pop()
        else:
            pcode = ''

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
        worldPage = sec[1].strip().strip(u'[]').strip(u'|')
        try:
            target_page = Page(site, worldPage)
            categories = target_page.getCategories(True)
            if 'Category:Disambiguation pages' in categories:
                worldName = worldPage.split(u'(')
                shortName = shortNames[sectorName]
                worldPage = worldName[0] + u'('+ shortName + u' ' + hexNo + u') (' + worldName[1]
        except NoPage:
            print u"Missing Page: {}".format(worldPage)
            continue

        data = data_template.format(eco[1].strip(),                                 # World
                                    sectorName,                                     # Sector
                                    eco[14].split(u'|')[1].strip(u'\n').strip(u']'),# Subsector
                                    hexNo,                                          # hex
                                    worldPage,                                      # Name
                                    sec[2].strip(),                                 # UWP
                                    pcode,                                          # pcode
                                    u','.join(sorted(list(codeset))),               # codes
                                    u','.join(sophonts),                            # sophonts
                                    u','.join(sorted(list(dcode))),                 # details
                                    sec[4].strip(u'{}'),                            # ix (important)
                                    sec[5].strip(u'()'),                            # ex (Economiv)
                                    sec[6].strip(u'[]'),                            # cx (cultureal)
                                    sec[7].strip(),                                 # nobility
                                    sec[8].strip(),                                 # bases
                                    sec[9].strip(),                                 # Zone
                                    sec[10][0],                                     # pop mult
                                    sec[10][1],                                     # Belts
                                    sec[10][2],                                     # GG Count
                                    sec[11],                                        # Worlds
                                    sec[12],                                        # Alegiance
                                    u','.join(stars),                               # stars
                                    eco[5].strip(),                                 # wtn
                                    eco[6].strip(),                                 # RU
                                    eco[7].strip(),                                 # GWP
                                    eco[8].strip(),                                 # Trade
                                    eco[9].strip(),                                 # Passengers
                                    eco[10].strip(),                                # build capacity
                                    eco[11].strip(),                                # Army
                                    eco[12].strip(),                                # port size
                                    eco[13].strip()                                 # spa population
                                    )
        try:
            target_page = Page(site,  worldPage + u'/data')
            result = target_page.edit(text=data, summary='Trade Map update world data', 
                                      bot=True, skipmd5=True)

            if result['edit']['result'] == 'Success':
                print u'Saved: {}/data'.format(worldPage)
            else:
                print u'Save failed {}/data'.format(worldPage)
        except api.APIError as e:
            if e.args[0] == 'missingtitle':
                print u"UploadSummary for page {}, page does not exist".format(worldPage)
            else:
                print u"UploadSummary for page {} got exception {} ".format(worldPage, e)

shortNames = {u'Dagudashaag': u'Da'}

if __name__ == '__main__':
    warnings.simplefilter("always")

    parser = argparse.ArgumentParser(description='Trade map generator wiki upload.')
    parser.add_argument('--input', default='../maps', help='output directory for maps, statistics')
    parser.add_argument('--no-maps', dest='maps', default=True, action='store_false')
    parser.add_argument('--no-secs', dest='secs', default=True, action='store_false')
    parser.add_argument('--no-summary', dest='summary', default=True, action='store_false')
    parser.add_argument('--no-subsector', dest='subsector', default=True, action='store_false')
    parser.add_argument('--no-worlds', dest="worlds", default=True, action='store_false')
    parser.add_argument('--site', dest='site', default='http://wiki.travellerrpg.com/api.php')
    
    args = parser.parse_args()
    
    # create a Wiki object
    site = wiki.Wiki(args.site)
    #site = wiki.Wiki("http://localhost/wiki/api.php")
    site.login("AB-101", remember=True)

    if args.maps:
        path = os.path.join(args.input, "*Sector.pdf")
        for f in glob.glob(path):
            uploadPDF(site, f)
            time.sleep(5)

    if args.secs:        
        path = os.path.join(args.input, "*Sector.economic.wiki")
        for f in glob.glob(path):
            uploadSec (site, f, "/economic")
            time.sleep(5)
        path = os.path.join(args.input, "*Sector.sector.wiki")
        for f in glob.glob(path):
            uploadSec (site, f, "/sector")
            time.sleep(5)

    if args.summary:
        path = os.path.join(args.input, "summary.wiki")
        uploadSummaryText(site, path)
    if args.subsector:
        path = os.path.join(args.input, "subsector_summary.wiki")
        uploadSummaryText(site, path)

    if args.worlds:
        path = os.path.join(args.input, "*Sector.economic.wiki")
        for eco in glob.glob(path):
            sector = os.path.basename(eco)[:-21]
            if sector in shortNames.keys():
                sec = eco.replace('Sector.economic.wiki', 'Sector.sector.wiki')
                uploadWorlds(site, sec, eco)
