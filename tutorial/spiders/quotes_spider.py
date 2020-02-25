import scrapy
import json
from selenium import webdriver

class AngularSpider(scrapy.Spider):
    name = 'angular_spider'
    start_urls = [
        'https://www.pulitzer.org/prize-winners-by-year/2019',
        'https://www.pulitzer.org/prize-winners-by-year/2018',
        'https://www.pulitzer.org/prize-winners-by-year/2017',
        'https://www.pulitzer.org/prize-winners-by-year/2016',
        'https://www.pulitzer.org/prize-winners-by-year/2015',
        'https://www.pulitzer.org/prize-winners-by-year/2014',
        'https://www.pulitzer.org/prize-winners-by-year/2013',
        'https://www.pulitzer.org/prize-winners-by-year/2012',
        'https://www.pulitzer.org/prize-winners-by-year/2011',
        'https://www.pulitzer.org/prize-winners-by-year/2010'
    ]    
    # Initalize the webdriver    
    def __init__(self):
        self.driver = webdriver.Firefox()

    
    # Parse through each Start URLs
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)    

    # Parse function: Scrape the webpage and store it
    def parse(self, response):
        self.driver.get(response.url)
        # Output filename
        import pdb
        pdb.set_trace()
        year = self.driver.find_elements_by_class_name("title-group")[0].find_elements_by_tag_name("h1")[0].find_elements_by_css_selector("span.ng-binding")[0].text
        groups = self.driver.find_elements_by_class_name("table-group")
        groups_json = [self.group_to_json(group) for group in groups]
        filename = "angular_data_%s.json" % (year)
        with open(filename, "w") as f:
            json.dump({"year": year, "groups": groups_json}, f)
        self.log('Saved file %s' % filename)

    def group_to_json(self, group):
        if self.is_special_citation_group(group):
            return self.special_citation_group_to_json(group)
        group_name = group.find_elements_by_class_name("section-header2")[0].text
        sections = [self.section_to_json(section) for section in group.find_elements_by_class_name("table-row")]
        sections = [section for section in sections if section is not None]
        return {"name": group_name, "sections": sections}

    def is_special_citation_group(self, group):
        return len(group.find_elements_by_id("special-citations-group")) > 0

    def special_citation_group_to_json(self, group):
        group_name = group.find_elements_by_class_name("section-header2")[0].text
        sections = [self.section_to_json(section) for section in group.find_elements_by_class_name("table-row")]
        new_sections = []
        for section in sections:
            if section is not None:
                new_section = {"name": section["name"], "citations": section["winners"]}
                new_sections.append(new_section)
        return {"name": group_name, "sections": new_sections}

    def section_to_json(self, section):
        section_name = section.find_elements_by_class_name("table-category")[0].text
        winners = [self.winner_to_json(winner) for winner in section.find_elements_by_class_name("table-winners")]
        finalists = [self.finalist_to_json(finalist) for finalist in section.find_elements_by_class_name("finalist")]
        if finalists or winners:
            section_json = {"name": section_name}
            if finalists:
                section_json["finalists"] = finalists
            if winners:
                section_json["winners"] = winners
            return section_json
        return None

    def winner_to_json(self, winner):
        if len(winner.find_elements_by_tag_name("a")) == 0:
            return {}
        winner_name = winner.find_elements_by_tag_name("a")[0].text
        winner_link = winner.find_elements_by_tag_name("a")[0].get_attribute("href")
        winner_citation_items = winner.find_elements_by_class_name("citation")
        if len(winner_citation_items) == 0:
            winner_citation = ""
        else:
            winner_citation = winner_citation_items[0].text
        return {"name": winner_name, "link": winner_link, "citation": winner_citation}

    def finalist_to_json(self, finalist):
        finalist_name = finalist.find_elements_by_tag_name("a")[0].text
        finalist_link = finalist.find_elements_by_tag_name("a")[0].get_attribute("href")
        return {"name": finalist_name, "link": finalist_link}
