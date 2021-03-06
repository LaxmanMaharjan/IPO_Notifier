import scrapy
import pandas as pd
import datetime
import smtplib
import os 

from scrapy.crawler import CrawlerProcess
from email.message import EmailMessage

#data = pd.read_csv("IPO_Infos.csv")
receivers = pd.read_csv("Receivers.csv")

current_date = str(datetime.date.today())

receivers_list = receivers.iloc[:, 2].tolist()

class IpoNotifierSpider(scrapy.Spider):
    name = 'Ipo_Notifier'
    base_url = "https://www.sharesansar.com/"

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # crawler's entry point
    def start_requests(self):
        yield scrapy.Request(
            url = self.base_url,
            headers = self.headers,
            callback = self.parse
        )

    def parse(self, response):
        """
        This function scrapes all the required information about the IPOs
        """
        data = pd.read_csv("IPO_Infos.csv")
        
        for i in range(1,6):
            for info in response.xpath(f"//div[@id='myTableEip']/table/tbody/tr[{i}]"):

                Company = info.xpath(".//td/a/@title").get()
                Symbol = info.xpath(".//td/a/text()").get()
                Units = info.xpath(".//td[@class= 'text-center'][1]/text()").get()
                Unit_Price = info.xpath(".//td[@class= 'text-center'][2]/text()").get()
                Opening_Date = info.xpath(".//td[6]/text()").get().strip()
                Closing_Date = info.xpath(".//td[7]/text()").get().strip()


                # Notify on day before ipo openinig date and on the opening date
                

                if (Opening_Date == str(datetime.date.today() + datetime.timedelta(days = 1))) or (current_date == Opening_Date):
                    
                    ipo_data = {
                    'Company' : info.xpath(".//td/a/@title").get(),
                    'Symbol' : info.xpath(".//td/a/text()").get(),
                    'Units' : info.xpath(".//td[@class= 'text-center'][1]/text()").get(),
                    'Unit_Price' : info.xpath(".//td[@class= 'text-center'][2]/text()").get(),
                    'Opening_Date' : info.xpath(".//td[6]/text()").get().strip(),
                    'Closing_Date' : info.xpath(".//td[7]/text()").get().strip()
                    }


                    ipo_str = '\n'.join([f'{key}: {value}' for key, value in ipo_data.items()])

                    message = f"This Email is to Notify you to apply in the new IPO.\n\nIPO Details:\n{ipo_str}\n\nYours Always,\nLaxman Maharjan"

                    data1 = data.append(ipo_data,ignore_index=True).sort_values(by = "Opening_Date", ascending = False)

                    yield ipo_data

                    # get email and password from environment variables
                    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
                    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

                    msg = EmailMessage()
                    msg['Subject'] = "New IPO Information"
                    msg['From'] = EMAIL_ADDRESS
                    msg['To'] = ', '.join(receivers_list)

                    msg.set_content(message)


                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                        smtp.send_message(msg)
                        
                    #appending new IPO in existing csv file
#                     if Company in data.Company.tolist() == True:
#                         continue
#                     else:
#                         data1.to_csv("IPO_Infos.csv",index=False)
                    
                    if Company in data.Company.tolist() == False:
                        data1.to_csv("IPO_Infos.csv",index=False)

                
if __name__=='__main__':
    #run spider
    process = CrawlerProcess()
    process.crawl(IpoNotifierSpider)
    process.start()
