import re

import scrapy
from urllib.parse import unquote, quote

def text_from_selector(s : scrapy.Selector) -> str:
    return ''.join(s.css('::text').getall()).strip()

def _T(s):
    return text_from_selector(s)

def get_pronunciation(response, language : str):
    if not response:
        return None
    selector_list = response.xpath(f'//h2[@id="{language}"] | //span[@class="IPA"]')
    if not selector_list:
        return None
    i = 0
    for sel in selector_list:
        if sel.attrib.get('id') == language:
            break
        i += 1
    if i == len(selector_list) or i == len(selector_list)-1:
        return None
    next_item = selector_list[i+1]
    first_ipa_text = next_item.css("::text").getall()
    if not first_ipa_text:
        return None
    return first_ipa_text[0]


def get_latin_inflection(response):
    table = response.css('table.inflection-table-la')
    if not table:
        return None
    acc = table.xpath('descendant::span[contains(@class, "acc")]').css('::text').getall()
    if not acc:
        return None
    return acc[0]

class WiktionarySpider(scrapy.Spider):
    name = "wiktionary"

    def start_requests(self):
        url_root = "https://en.wiktionary.org/wiki/"
        with open('dictionary_scrape/spiders/nouns_ro_fromLa.txt', 'r', encoding='utf-8') as handle:
            nouns = handle.readlines()
        nouns = [re.sub(r'\(\)', '', n) for n in nouns]
        nouns = [n.strip() for n in nouns if n.strip()]
        # nouns = ['vulpe']
        urls = [ url_root + quote(n) for n in nouns]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url_text = unquote(response.url)
        nom = url_text.rsplit('/', 1)[-1]
        # acc = get_latin_inflection(response)
        # if not acc:
        #     acc = ''
        # data = {'nom':nom, 'acc':acc}
        ipa = get_pronunciation(response, "Romanian")
        if not ipa:
            ipa = ''
        data = {'nom':nom, 'ipa':ipa}
        yield data


