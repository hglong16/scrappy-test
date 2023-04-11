import scrapy
from pathlib import Path
import urllib.parse
import json
import requests
import http
import re


class Detail(scrapy.Spider):
    name = "detail"

    def start_requests(self):
        start_urls = []
        with open("sample.txt", "r") as f:
            # for test only first 5 link
            urls = [line.rstrip() for line in f]
            start_urls.extend(urls)

            # urls = [line.rstrip() for line in f]
            # start_urls.extend(urls)
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        core_url = "/".join(response.url.split("/")[:4])
        download_documents_href = response.xpath(
            '//div[@class="downloadDocuments"]//a/@href'
        ).extract_first()
        if download_documents_href:
            print(core_url, download_documents_href)
            target_detail = core_url + "/" + download_documents_href

            yield scrapy.Request(target_detail, callback=self.parse_detail)
        else:
            print(" Check this URLLLLLLLLLLLLLL", response.url)

    def parse_detail(self, response):
        data_oid = response.xpath(
            '//a[contains(@class, "zipFileContents")]/@data-oid'
        ).extract_first()
        data_title = response.xpath(
            '//a[contains(@class, "zipFileContents")]/@data-title'
        ).extract_first()
        data_token = response.xpath(
            '//a[contains(@class, "zipFileContents")]/@data-token'
        ).extract_first()
        core_url = "/".join(response.url.split("/")[:4])
        endpoint = core_url + "/" + "DataProvider"
        cookie_list = response.headers.getlist("Set-Cookie")

        # Step 2: Parse cookies and store in dictionary
        cookies = {}
        for cookie in cookie_list:
            cookie_obj = http.cookies.SimpleCookie()
            cookie_obj.load(cookie.decode("utf-8"))
            for key, morsel in cookie_obj.items():
                cookies[key] = morsel.value
        payload = {"param": "FileTree", "oid": data_oid, "VALIDATION_TOKEN": data_token}
        print("---------------------------------------------------")
        print(payload)
        yield scrapy.FormRequest(
            endpoint,
            formdata=payload,
            headers={
                "Cookie": cookies,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34",
                "content-type": "application/x-www-form-urlencoded",
                "x-puid": "YNgN2QokGScAA0-MH9MAAAIQ",
                "x-requested-with": "XMLHttpRequest",
            },
            callback=self.parse_formdata,
            meta={
                "data_title": data_title,
                "core_url": core_url,
                "data_oid": data_oid,
            },
        )

    def parse_formdata(self, response):
        print(response.text)
        response.meta["data_title"]
        if response.text:
            data = json.loads(response.text)
            print("-------------DATATATATATTATAT----------------------")
            print(data)
            print("---------------------------------------------------")
            import os

            for k, v in data.items():
                for key, value in v.items():
                    if "size" in value.keys():
                        value["download_url"] = self.create_download_url(
                            response.meta["core_url"], response.meta["data_oid"], value
                        )

            os.makedirs("result", exist_ok=True)
            file_name = response.meta["data_oid"]
            with open("result/" + file_name + ".json", "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)

    def remove_special_characters(self, text):
        # define the pattern to match any non-alphanumeric character
        pattern = r"[^a-zA-Z0-9\s]"

        # use regex to replace any special characters with an empty string
        cleaned_text = re.sub(pattern, "", text)

        return cleaned_text

    def create_download_url(self, core_url, data_oid, data):
        return (
            core_url
            + "/"
            + f'TenderingProcedureDetails?function=_DownloadTenderDocument&documentOID={data_oid}&Document={data["nameEncoded"]}'
        )
