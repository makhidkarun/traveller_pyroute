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
from wikitools.wikifile import File
from wikitools.page import Page
import warnings
import os
import codecs
import glob
import time

def uploadSummaryText(site, summaryFile):
    try:
        lines = [line for line in codecs.open(summaryFile,'r', 'utf-8')]
    except (OSError, IOError):
        print "Summary file not found: {}".format(summaryFile)
        return 
    index = [i for i,n in enumerate(lines) if 'Statistics' in n][0]
    lines = lines[index + 3:]
    index = 1;
    
    while True:
        baseTitle = lines[index].split('|')[1].strip('[')
        targetTitle= "{}/summary".format(baseTitle)
        index += 1
        text = lines[index][3:]
        index += 1
        while (not (lines[index].startswith('|-') or lines[index].startswith('|}'))):
            text += lines[index]
            index += 1
        
        target_page = Page(site, targetTitle)
        result = target_page.edit(text=text, summary='Trade Map update sector summary', 
                                  bot=True, nocreate=True)

        if result['edit']['result'] == 'Success':
            print 'Saved: {}'.format(targetTitle)
        else:
            print 'Save failed {}'.format(targetTitle) 
        if lines[index].startswith('|}'):
            break       
        index += 1
        
def uploadPDF(site, filename):
    with open(filename, "rb") as f:        
        try:
            page = File (site, os.path.basename(filename))
            page.setPageInfo()
            page.upload(f, "{{Trade map summary}}", ignorewarnings=True)
        except Exception as e:
            print "Got Exception: {}".format(e)
#            traceback.print_exc()
    

def uploadSec (site, filename):
    with codecs.open(filename, "r", 'utf-8') as f:
        text = f.read()

    targetTitle = os.path.splitext(os.path.basename(filename))[0] + "/data"    
    target_page = Page(site, targetTitle)
    result = target_page.edit(text=text, summary='Trade Map update sector data', 
                              bot=True, nocreate=True)
    if result['edit']['result'] == 'Success':
        print 'Saved: {}'.format(targetTitle)
    else:
        print 'Save failed {}'.format(targetTitle) 

    

if __name__ == '__main__':
    warnings.simplefilter("always")
    
    # create a Wiki object
    site = wiki.Wiki("http://wiki.travellerrpg.com/api.php") 
    site.login("GORT",remember=True)

    for f in glob.glob('../maps/*Sector.pdf'):
        uploadPDF(site, f)
        time.sleep(10)
        
    for f in glob.glob('../maps/*Sector.sec'):
        uploadSec (site, f)
        time.sleep(10)
        
    uploadSummaryText(site, "../maps/summary.wiki")
    uploadSummaryText(site, "../maps/summary_subsector.wiki")
    
        
    