'''
Created on Jun 3, 2014

@author: tjoneslo
'''
import urllib2
import urllib
import codecs
import string
import time
import os
import argparse

def get_url (url, sector, suffix):
    f = urllib2.urlopen(url)
    
    encoding=f.headers['content-type'].split('charset=')[-1]
    content = f.read()
    if encoding == 'text/xml':
        ucontent = unicode(content, 'utf-8').replace('\r\n', '\n')
    else:
        ucontent = unicode(content, encoding).replace('\r\n','\n')
    
    path = os.path.join(args.output_dir, '%s.%s' % (sector, suffix))
    
    with codecs.open(path, 'wb', 'utf-8') as out:
        out.write (ucontent)
    f.close()
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download sector/metadata from TravellerMap')
    parser.add_argument('sector_list', help='List of sectors to download')
    parser.add_argument('output_dir', help='output directory for sector data and xml metadata')
    args = parser.parse_args()

    sectorsList = [line for line in codecs.open(args.sector_list,'r', 'utf-8')]
        
    for sector in sectorsList: 
        sector = sector.rstrip()
        print 'Downloading %s' % sector
        params = urllib.urlencode({'sector': sector, 'type': 'SecondSurvey'})
        url = 'http://www.travellermap.com/api/sec?%s' % params
        get_url (url, sector, 'sec')
        
        
        params = urllib.urlencode({'sector': sector, 'accept': 'text/xml'})
        url = 'http://travellermap.com/api/metadata?%s' % params
        get_url (url, sector, 'xml')
        
        time.sleep(10)