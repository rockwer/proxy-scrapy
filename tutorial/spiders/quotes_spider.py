from scrapy_splash import SplashRequest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import scrapy
import re

Base = declarative_base()
class Proxy(Base):
    __tablename__ = 'proxy'

    id = Column('id', Integer, primary_key=True)
    ip_address = Column('ip_address', String)
    port = Column('port', String)
engine = create_engine('sqlite:///proxy.sqlite', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


class ProxiesSpider(scrapy.Spider):
    name = "proxies"

    def start_requests(self):
        urls = [
            'http://spys.one/proxies/',
            'http://spys.one/proxies/1/',
            'http://spys.one/proxies/2/',
            'http://spys.one/proxies/3/',
        ]
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):
        iteml1 = response.xpath('//tr[@class="spy1xx"]/td/*').extract()
        iteml2 = response.xpath('//tr[@class="spy1x"]/td/*').extract()
        item = iteml1[4:] + iteml2[9:]
        tags = re.compile(r'<.*?>')
        scripts = re.compile(r'<(script).*?</\1>(?s)')
        new_list = []
        for i in item:
            i_encoded = i.encode('utf-8')
            new_i_without_scripts = scripts.sub('', i_encoded)
            new_i_without_tags = tags.sub('', new_i_without_scripts)
            new_i_splitted = new_i_without_tags.split(':')
            new_list.append(new_i_splitted)
        beautiful_list = []
        proxy_ip_index = 1
        proxy_id_index = 0
        for element in new_list:
            while proxy_ip_index < len(new_list):
                update_dic = {}
                update_dic['id'] = new_list[proxy_id_index][0]
                update_dic['ip'] = new_list[proxy_ip_index][0]
                update_dic['port'] = new_list[proxy_ip_index][1]
                beautiful_list.append(update_dic)
                proxy_ip_index, proxy_id_index = proxy_ip_index + 11, proxy_id_index + 11

        element_index = 0
        session = Session()
        while element_index <= len(beautiful_list):
            proxy = Proxy()
            proxy.id = int(beautiful_list[element_index]['id'])
            proxy.ip_address = beautiful_list[element_index]['ip']
            proxy.port = beautiful_list[element_index]['port']
            session.add(proxy)
            session.commit()
            print element_index
            element_index += 1
        session.close()
