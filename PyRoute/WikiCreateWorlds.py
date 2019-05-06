"""
Created on Dec 27, 2017

@author: tjoneslo
"""

import logging
import argparse
import os
from .Galaxy import Galaxy
from .WikiReview import WikiReview
from wikitools.page import Page

logger = logging.getLogger('WikiCreateWorlds')


class WikiCreateWorld(object):
    """
    classdocs
    """
    page_template = '''{{{{UWP
 |name    = {{{{World|{full name}|{sector}|{subsector}|{pos}}}}}
 |system  = 
 |uc      = {uwp}
 |popc    = {popc}
 |zonec   = {zone}
 |alg     = {alg}
 |class   = {class}
 |trade   = {pcode}
 |climate = TBD
 |orbit   = TBD
 |gravity = TBD
 |worlds  = {worlds}
 |nblty   = {nobility}
 |bases   = {bases}
 |primary = {stars}
 |belts   = {belt}
 |GGcount = {ggcount}
}}}}
{{{{World summary |name= {name} |trade={trade} }}}}{comment summary}
{{{{World summary {alg}|sector={sector}|subsector={subsector} }}}}
* {{{{World summary allegiance|code={alg}|sector={sector}|subsector={subsector} }}}}{base summary}

== Astrography and planetology == 
No information yet available. 
 
{star template}

=== System Data ===
No information yet available. 
 
=== Mainworld Data ===
No information yet available.

==== Mainworld Geography and topography ====
No information yet available.

==== Mainworld Map ====
No information yet available.

=== Native Lifeforms ===
No information yet available.

== History and background ==
No information yet available. 
{nobility summary}
=== World Starport ===
{{{{Starport|name= {name}|Starport={port} }}}}

=== World Technology Level ===
{{{{WorldTech|name= {name}|WorldTech={tech} }}}}

=== World Government ===
{{{{WorldGov|name= {name}|Government={gov} }}}}  

==== World Law Level ====
No information yet available. 

==== World Military ====
No information yet available. 

=== World Economy ===
No information yet available. 

==== Trade Data ====
No information yet available. 

=== World Demographics ===
No information yet available. 

=== World Culture ===
No information yet available. 

==== World Languages ====
No information yet available. 

==== Urbanization ====
No information yet available. 

==== World Infrastructure ====
No information yet available. 

=== Historical Data ===
No information yet available. 

==== World Timeline ====
No information yet available.

==== UWP Listing ====
No information yet available.

== References and contributors ==
{{{{Intermediate}}}}
{{{{Detail}}}}
{sources}

{categories}
{{{{LEN}}}}
'''
    monostellarTemplate = '''
{{{{MonostellarSystem
 |name        = {}
 |primary     = {}
}}}} 
'''
    binaryTemplate = '''
{{{{BinaryStarSystem
 |name        = {}
 |primary     = {} 
 |secondary   = {}
}}}}
'''
    trinaryTemplate = '''
{{TrinaryStarSystem
 |name        = {}
 |primary     = {}
 |secondary   = {}
 |tertiary    = {}
}}
'''

    def __init__(self):
        """
        Constructor
        """

    def get_star_template(self, star):
        if len(star.star_list) == 1:
            star_template = self.monostellarTemplate.format(star.name, star.star_list[0])
            star_category = None
        elif len(star.star_list) == 2:
            star_template = self.binaryTemplate.format(star.name, star.star_list[0], star.star_list[1])
            star_category = '[[Category: Binary Star System]]'
        elif len(star.star_list) == 3:
            star_template = self.trinaryTemplate.format(star.name, star.star_list[0], star.star_list[1], star.star_list[2])
            star_category = '[[Category: Trinary Star System]]'
        else:
            logger.info("found system {} with {:d} stars".format(star.name, len(star.star_list)))
            star_template = None
            star_category = None

        return (star_template, star_category)

    def get_sources(self, star, sources):
        source_text = '{{Sources\n'
        index = 1
        for source in sources:
            source_text += " |S{}={}\n".format(index, source)
            index += 1

        source_text += "}}\n"

        return source_text

    def get_categories(self, star, categories):
        # base_categories = ['[[Category: First Imperium worlds]]', '[[Category: Humaniti worlds]]', '[[Category: Rule of Man worlds]]',
        #                   '[[Category: Second Imperium worlds]]','[[Category: Ziru Sirka worlds]]']
        base_categories = []
        if star:
            base_categories.append(star)
        if categories:
            base_categories.extend(categories)
        base_categories.sort()
        return '\n'.join(base_categories)

    def get_comments(self, star):
        comments = []
        for code in star.tradeCode.dcode:
            comments.append('{{{{World summary comment|trade={} }}}}'.format(code))
        for code in star.tradeCode.xcode:
            comments.append('{{{{World summary comment|trade={} }}}}'.format(code))
        comments = '\n' + '\n'.join(comments) if len(comments) > 0 else ' '
        return comments

    def get_bases(self, star):
        if star.baseCode != '-':
            bases = '\n{{{{World summary bases|bases={} }}}}'.format(star.baseCode)
        else:
            bases = ' '
        return bases

    def get_nobility(self, star):
        if len(str(star.nobles)):
            nobility = '''
=== Imperial High / Landed Nobility ===
{{{{Imperial Nobility|name= {}|Noble={} }}}}
'''. format(star.name, star.nobles)
        else:
            nobility = '\n'
        return nobility

    def create_page(self, star, categories, sources, full_name):
        star_template, star_category = self.get_star_template(star)
        sources = self.get_sources(star, sources)
        comments = self.get_comments(star)
        bases = self.get_bases(star)
        nobility = self.get_nobility(star)
        subsector = star.sector.subsectors[star.subsector()].name
        pcode = star.tradeCode.pcode if star.tradeCode.pcode else ''
        trade = ' '.join(star.tradeCode.codeset)
        categories = self.get_categories(star_category, categories)
        classification = ' '.join(star.tradeCode.codeset)
        if len(star.tradeCode.xcode) > 0:
            classification += ' / ' + ' '.join(star.tradeCode.xcode)

        formatting = {'sector': star.sector.name, 'subsector': subsector, 'pos': star.position,
                      'uwp': star.uwp, 'popc': star.uwpCodes['Pop Code'], 'zone': star.zone,
                      'alg': star.alg, 'pcode': pcode, 'nobility': str(star.nobles),
                      'bases': star.baseCode, 'stars': star.stars, 'belt': str(star.belts), 'worlds': star.worlds,
                      'ggcount': str(star.ggCount), 'trade': trade, 'class': classification,
                      'star template': star_template, 'port': star.uwpCodes['Starport'], 
                      'tech': star.uwpCodes['Tech Level'], 'gov': star.uwpCodes['Government'],
                      'comment summary': comments, 'base summary': bases,
                      'nobility summary': nobility, 'categories': categories,
                      'sources': sources, 'name': star.name, 'full name': full_name
                      }

        page_text = self.page_template.format(**formatting)
        return page_text

    def read_sector(self, sectors):
        galaxy = Galaxy(12)
        galaxy.read_sectors(sectors, 'fixed', 'scaled')
        return galaxy


def get_category_list(category_files):
    category_list = {}
    for cat in category_files:
        cat_name = '[[Category: {}]]'.format(os.path.splitext(os.path.basename(cat))[0].replace('_', ' '))
        cat_worlds = get_skip_list(cat)
        logger.debug("processing category: {} -> {} of {}".format(cat, cat_name, cat_worlds))

        for world in cat_worlds:
            if world.strip() in category_list:
                category_list[world.strip()].append(cat_name)
            else:
                category_list[world.strip()] = [cat_name]

    return category_list


def get_sources_list(sources_files):
    sources_list = {}
    
    for src in sources_files:
        src_worlds = get_skip_list(src)
        src_name = src_worlds[0]
        for world in src_worlds[1:]:
            if world.strip() in sources_list:
                sources_list[world.strip()].append(src_name)
            else:
                sources_list[world.strip()] = [src_name]
    return sources_list


def get_skip_list(name):
    with open(name) as f:
        skip_list = f.read().splitlines()
    return skip_list


def get_max_list():
    with open('Zar_max_present.txt') as f:
        max_list = f.read().splitlines()

    return max_list


def set_logging(level):
    log = logging.getLogger()
    log.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    log.addHandler(ch)


def process():
    parser = argparse.ArgumentParser(description='Traveller Wiki create world articles.', fromfile_prefix_chars='@')
    parser.add_argument('--skip-list', help='file of worlds to skip adding/updating')
    parser.add_argument('-c', '--category', action='append', help='File with list of worlds to append different category')
    parser.add_argument('-s', '--source', action='append', help='File with list of worlds to append a source')
    parser.add_argument('--log-level', default='INFO')

    parser.add_argument('--site', dest='site', default='https://wiki.travellerrpg.com/api.php')
    parser.add_argument('--user', dest='user', default='AB-101', help='(Bot) user to connect to the wiki, default [AB-101]')
    parser.add_argument('--search-disambig', help='Search value to refine disambiguation title')

    parser.add_argument('--save-to-wiki', dest='save', default=False, action='store_true', help='Save the generated pages to the wiki')
    parser.add_argument('sector', nargs='*', help='T5SS sector file(s) to process')

    args = parser.parse_args()
    set_logging(args.log_level)

    worlds = WikiCreateWorld()
    skip_list = get_skip_list(args.skip_list) if args.skip_list else []

    site = WikiReview.get_site(args.user, args.site)
    wiki_review = WikiReview(site, None, args.search_disambig, 1000)

    category_list = get_category_list(args.category)
    sources_list = get_sources_list(args.source)

    galaxy = worlds.read_sector(args.sector)
    for star in galaxy.stars:
        if star.name in skip_list:
            continue

        wiki_page = wiki_review.get_page(star.wiki_short_name())
        wiki_page = wiki_page[0] if isinstance(wiki_page, (list, tuple)) else wiki_page
        if wiki_page is None:
            
            logger.info("Unable to find: {}, creating new page".format(star.name))
            wiki_page = Page(site, star.wiki_short_name())

        # Alpha (world)
        title = wiki_page.title[:-8]
        logger.info("Processing {} -> {}".format(star.name, wiki_page.title))

        categories = category_list[star.name] if star.name in category_list else None
        sources = sources_list[star.name] if star.name in sources_list else []

        new_page = worlds.create_page(star, categories, sources, title)

        # print new_page
        # print "=============================================="
        if args.save:
            logger.info("Saving Page: %s", wiki_page.title)
            result = wiki_review.save_page(wiki_page, new_page, create=True)
            logger.info("Save result: %s", result)


if __name__ == '__main__':
    process()
