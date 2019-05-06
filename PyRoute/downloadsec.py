"""
Created on Jun 3, 2014

@author: tjoneslo
"""
import urllib.request, urllib.error, urllib.parse
import codecs
import time
import os
import argparse


def get_url(url, sector, suffix, output_dir):
    try:
        f = urllib.request.urlopen(url)
    except urllib.error.HTTPError as ex:
        print ("get URL failed: {} -> {}".format(url, ex))
        return

    encoding = f.headers['content-type'].split('charset=')[-1]
    content = f.read()
    if encoding == 'text/xml' or encoding == 'text/html':
        ucontent = str(content, 'utf-8').replace('\r\n', '\n')
    else:
        ucontent = str(content, encoding).replace('\r\n', '\n')
    
    path = os.path.join(output_dir, '%s.%s' % (sector, suffix))

    with codecs.open(path, 'wb', 'utf-8') as out:
        out.write(ucontent)
    f.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download sector/metadata from TravellerMap')
    parser.add_argument('--routes', dest='routes', default=False, action='store_true',
                        help='Include route information in the sector downloads')
    parser.add_argument('sector_list', help='List of sectors to download')
    parser.add_argument('output_dir', help='output directory for sector data and xml metadata')
    args = parser.parse_args()

    sectorsList = [line for line in codecs.open(args.sector_list, 'r', 'utf-8')]

    for sector in sectorsList:
        sector = sector.rstrip()
        print ('Downloading %s' % sector)
        params = {'sector': sector, 'type': 'SecondSurvey'}
        if args.routes:
            params['routes'] = '1'
        params = urllib.parse.urlencode(params)
        url = 'http://www.travellermap.com/api/sec?%s' % params

        get_url(url, sector, 'sec', args.output_dir)
        
        params = urllib.parse.urlencode({'sector': sector, 'accept': 'text/xml'})
        url = 'http://travellermap.com/api/metadata?%s' % params
        get_url(url, sector, 'xml', args.output_dir)

        time.sleep(5)
