from pathlib import Path
import json
import scrapy
import os
from urllib.parse import urlparse, urlencode, urlsplit, urlunsplit
import urllib.parse


class NetServer(scrapy.Spider):
    name = "netserver"
    start_urls = [
        "https://evergabe.sachsen.de/NetServer/",
        # "https://vergabe.duesseldorf.de/NetServer/",
    ]

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.all_tr = []

    def parse(self, response):
        with open("sample.txt", "w") as f:
            f.truncate(0)
        page = response.url.split("/")[-3]
        footer = self.table_footer(response)
        content = {
            "page": page,
            "pagination_href": response.url + self.pagination_href(footer),
        }

        yield scrapy.Request(content["pagination_href"], callback=self.parse_pagination)

    def parse_pagination(self, response):
        next_page = response.xpath(
            '//ul[@class="pagination"]//li/a[@title="Next Page"]'
        )
        print("Before action detail")
        self.action_detail(response)

        if next_page:
            next_url = next_page.xpath("@href").extract_first()
            yield scrapy.Request(
                response.urljoin(next_url), callback=self.parse_pagination
            )
            print(response.urljoin(next_url))
            print("VAN CON NHE")
        else:
            print("DEO CON NUA")

    def table_footer(self, response):
        footer = response.xpath("//p[@class='tableFooterText']")
        return footer

    def pagination_href(self, footer):
        # Footer must be a Selector
        href = footer.xpath("a/@href").extract_first()
        return href

    def action_detail(self, response):
        print("action detail")
        tr_elements = response.xpath("//tr[@data-oid]")
        for tr in tr_elements:
            data_oid = tr.xpath("@data-oid").extract_first()
            detail_page = self.create_detail_url(response.url, data_oid)
            print(detail_page)
            with open("sample.txt", "a") as f:
                f.writelines(detail_page + "\n")

    def parse_detail(self, response):
        # download_document = response.xpath(
        #     '//div[@class="downloadDocuments"]//a@href'
        # ).extract_first()
        print("Hello", response.url)

    def create_detail_url(self, url_string, data_oid):
        url_obj = urlparse(url_string)
        params = {
            "function": "Detail",
            "TOID": data_oid,
            "Category": "InvitationToTender",
        }
        query_string = urlencode(params)
        new_path = "/NetServer/PublicationControllerServlet"
        new_parse_url = url_obj._replace(query=query_string, path=new_path)
        new_url = urllib.parse.urlunparse(new_parse_url)
        return new_url
