import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
import time

class theStarBusinessScraper():
    def __init__(self):
        self.chromeOptions = Options()
        self.chromeOptions.add_argument("--incognito")
        
    def startBrowser(self):
        self.browser = webdriver.Chrome(options = self.chromeOptions)
        self.browser.get("http://www.thestar.com.my/business")
        items = self.browser.find_elements_by_xpath('//h2/a[@href]')
        return items
    
    def scrapeMainPage(self, items):
        DF_list = []
        for item in items:
            DF_list.append([item.get_attribute('data-content-title'), item.get_attribute('data-content-author'), item.get_attribute('href')])
        DF = pd.DataFrame(DF_list, columns = ["Title", "Author", "Link"])
        DF = DF.applymap(str)
        DF = DF[DF["Title"] != "None"]
        self.browser.close()
        return DF
    
    def scrapeIndividualPage(self, DF):
        contentDFList = []
        for i in DF["Link"]:
            print("Scraping Link",i)
            response = requests.get(i)
            soup = BeautifulSoup(response.content,'html.parser')
            element_list = soup.find_all("p")
            if element_list != []:
                text_list = []
                for element in element_list:
                    text_list.append(element.get_text())
                try:
                    for index, line in enumerate(text_list):
                        if ("Tags / Keywords" in line):
                             trimmingIndex = index-1
                except:
                    contentDFList.append([i,"NA","NA","NA","NA"])
                    continue
                try:
                    day = text_list[0].replace("\n","").strip().split(",")[0]
                    date = text_list[0].replace("\n","").strip().split(",")[1].strip()
                    if ("by" in text_list[1].lower()) and (len(text_list[1]) < 50):
                        author = text_list[1].lower().strip("by").strip()
                        content = ''.join(text_list[2:trimmingIndex])
                    else:
                        author = "NA"
                        content = ''.join(text_list[1:trimmingIndex])
                    contentDFList.append([i,day,date,author,content])
                except:
                    contentDFList.append([i,"NA","NA","NA","NA"])
                    continue
            else:
                contentDFList.append([i,"NA","NA","NA","NA"])
            time.sleep(2)
        
        contentDF = pd.DataFrame(contentDFList, columns = ["Link","Day","Date","_Author","Content"])
        mergedDF = DF.merge(contentDF, left_on="Link", right_on="Link")
        mergedDF.drop(columns=["Link"])
        mergedDF["Author"].update(mergedDF.pop("_Author"))
        return mergedDF
    
    def saveCSV(self, mergedDF):
        today = date.today()
        mergedDF.to_csv(today.strftime("%d%m%y") + ".csv")
        
if __name__ == "__main__":
    scraper = theStarBusinessScraper()
    mainPage = scraper.startBrowser()
    DF = scraper.scrapeMainPage(mainPage)
    contentDF = scraper.scrapeIndividualPage(DF)
    scraper.saveCSV(contentDF)
