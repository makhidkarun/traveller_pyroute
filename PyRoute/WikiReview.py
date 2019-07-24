#!/usr/bin/python

from wikitools_py3 import wiki
from wikitools_py3.api import APIRequest
from wikitools_py3.exceptions import WikiError, NoPage
from wikitools_py3.wikifile import File
from wikitools_py3.page import Page
import logging
import traceback
import re
import os

logger = logging.getLogger('WikiReviewClass')


class PageReview(object):

    def __init__(self, search, replace, text, replace_count):
        self.search = search
        self.replace = replace
        self.text = text
        self.replace_count = replace_count

    def review(self, page, formats):
        raise NotImplementedError("Base Class")

    def update_formats(self, formats):
        search = self.search.format(**formats)
        replace = self.replace.format(**formats) if self.replace else None
        text = self.text.format(**formats) if self.text else None
        return (search, replace, text)


class PageReviewSearch(PageReview):

    def __init__(self, search, replace, text, replace_count):
        super(PageReviewSearch, self).__init__(search, replace, text, replace_count)

    def review(self, page, formats):
        (s, r, t) = self.update_formats(formats)
        logger.debug("searching for {} in {}".format(s, page.title))
        if re.search(s, page.getWikiText()):
            logger.info("Article {} has match search {}".format(page.title, self.search))
        return page.getWikiText()


class PageReviewReplace(PageReview):

    def __init__(self, search, replace, text, replace_count):
        super(PageReviewReplace, self).__init__(search, replace, text, replace_count)

    def review(self, page, formats):
        logger.debug('Searching for replacements in {}'.format(page.title))
        (s, r, t) = self.update_formats(formats)
        page_text = re.sub(s, r, page.getWikiText(), count=self.replace_count)
        return page_text


class PageReviewAddBefore(PageReview):

    def __init__(self, search, replace, text, replace_count):
        super(PageReviewAddBefore, self).__init__(search, replace, text, replace_count)

    def review(self, page, formats):
        (s, r, t) = self.update_formats(formats)
        s = "({})".format(s)
        r = "{}\1".format(t)
        page_text = re.sub(s, r, page.getWikiText(), count=self.replace_count)
        return page_text


class PageReviewAddAfter(PageReview):

    def __init__(self, search, replace, text, replace_count):
        super(PageReviewAddAfter, self).__init__(search, replace, text, replace_count)

    def review(self, page, formats):
        (s, r, t) = self.update_formats(formats)
        s = "({})".format(s)
        r = "\1{}".format(t)
        page_text = re.sub(s, r, page.getWikiText(), count=self.replace_count)
        return page_text


class WikiReview(object):
    reviews = {'search': PageReviewSearch,
               'replace': PageReviewReplace,
               'before': PageReviewAddBefore,
               'after': PageReviewAddAfter}

    def __init__(self, site, review, search_disambig, count):
        self.site = site
        self.review = review
        self.search_disambig = search_disambig
        self.count = count
        self.review_count = 0
        self.considered = 0
        self.logger = logging.getLogger('WikiReview')

    @staticmethod
    def get_site(user='AB-101', api_site='http://wiki.travellerrpg.com/api.php', password=False):
        site = wiki.Wiki(api_site)
        access = site.login(user, password=password)
        if not access:
            logger.error('Unable to log in')
        return site

    def get_page(self, title):
        try:
            target_page = Page(self.site, title)
        except NoPage as e:
            self.logger.error("Article {} page does not exist, skipped".format(title))
            return None
        except WikiError as e:
            if e.args[0] == 'missingtitle':
                self.logger.error("Article {} does not exist, skipped".format(title))
            else:
                self.logger.error("review article for Article {} got exception {}".format(title, e))

            return None

        if not target_page.exists:
            self.logger.error("Article {} page does not exist, skipped".format(title))
            return None

        categories = target_page.getCategories(True)
        if self.search_disambig and 'Category:Disambiguation pages' in categories:
            pages = []
            for disambig_title in self.search_disambiguation_page(title):
                pages.append(self.get_page(disambig_title))

            return pages[0] if len(pages) > 0 else None

        return target_page

    def save_page(self, page, text, summary="Wiki review change", create=False):
        try:
            if create:
                result = page.edit(text=text, summary=summary,
                                   bot=True, skipmd5=True)
            else:
                result = page.edit(text=text, summary=summary,
                                   bot=True, skipmd5=True, nocreate=True)

            if result['edit']['result'] == 'Success':
                self.logger.info('Saved: {}'.format(page.title))
                return True
            else:
                self.logger.error('Save failed {} - {}'.format(page.title, result))
                return False

        except NoPage as e:
            self.logger.error("Save Page for page {}, page does not exist, skipped".format(page.title))
            return False
        except WikiError as e:
            if e.args[0] == 'missingtitle':
                self.logger.error("Save Page for page {}, page does not exist".format(page.title))
            else:
                self.logger.error("Save Page for page {} got exception {} ".format(page.title, e))
            return False

    def upload_file(self, filename):
        with open(filename, "rb") as f:
            try:
                page = File(self.site, os.path.basename(filename))
                result = page.upload(f, "{{Trade map disclaimer}}", ignorewarnings=True)
                if result['upload']['result'] == 'Success':
                    self.logger.info('Saved: {}'.format(filename))
                else:
                    self.logger.error('Save failed {}'.format(filename))
            except Exception as e:
                self.logger.error("UploadPDF for {} got exception: {}".format(filename, e))
                traceback.print_exc()

    def process_page_name(self, name, append_title, insert_mode, message):
        formatting = {'title': name}
        page_name = name + append_title if append_title else name

        pages = self.get_page(page_name)
        if pages is None:
            return
        pages = [pages] if not isinstance(pages, (list, tuple)) else pages

        for page in pages:
            self.considered += 1
            text = self.review.review(page, formatting)
            if insert_mode in ['replace', 'before', 'after'] and text and text != page.getWikiText():
                self.review_count += 1
                self.save_page(page, text, message)
            elif insert_mode in ['search']:
                self.review_count += 1

    def search_disambiguation_page(self, title):
        search_title = title + self.search_disambig
        args = {'action': 'query', 'list': 'search', 'srsearch': search_title, 'srprop': 'size|wordcount'}
        request = APIRequest(self.site, args)
        results = request.queryGen()
        titles = []
        for r in results:
            for values in r['query']['search']:
                titles.append(values['title'])
        return titles

    def get_linked_here(self, page):
        args = {'action': 'query', 'prop': 'linkshere', 'titles': page}
        logger.debug("processing Links Here list")
        request = APIRequest(self.site, args)
        results = request.queryGen()
        titles = []
        for r in results:
            pages = r['query']['pages']
            key, values = pages.popitem()
            for value in values['linkshere']:
                # logger.debug(value)
                titles.append(value['title'])

        self.logger.info("Returning {:d} titles".format(len(titles)))
        return titles
