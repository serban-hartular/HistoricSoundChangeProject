import re

import scrapy

def text_from_selector(s : scrapy.Selector) -> str:
    return ''.join(s.css('::text').getall()).strip()

def _T(s):
    return text_from_selector(s)

class DexonlineSpider(scrapy.Spider):
    name = "dexonline"

    def start_requests(self):
        url_root = "https://dexonline.ro/definitie/"
        with open('dictionary_scrape/spiders/nouns_ro.txt', 'r', encoding='utf-8') as handle:
            nouns = handle.readlines()
        nouns = [re.sub(r'[0-9]+', '', n) for n in nouns]
        nouns = [n.strip() for n in nouns if n.strip()]
        urls = [ url_root + n for n in nouns]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        definition = _T(response.css('h3.tree-heading')[0])
        inflected = _T(response.css('h3.tree-heading')[0].xpath('.//*[@class="tree-inflected-form"]'))
        pos = _T(response.css('h3.tree-heading')[0].xpath('.//*[@class="tree-pos-info"]'))
        origins = []
        for orig in response.css('div.etymology')[0].css('li.type-etymology'):
            orig_lang = _T(orig.css('span.tag'))
            orig_word = _T(orig.css('span.def'))
            origins.append((orig_lang, orig_word))
        word = definition
        if word.endswith(pos):
            word = word[:-len(pos)]
        else:
            word = ''
        if word.endswith(inflected):
            word = word[:-len(inflected)]
        else:
            word = ''
        data = {'word':word, 'definition':definition,
                'inflected':inflected, 'pos':pos,
                'origins':origins}
        yield data


