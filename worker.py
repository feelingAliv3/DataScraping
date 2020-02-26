import requests
from bs4 import BeautifulSoup
import re

def WorkerScanPages(managed_list, year):
    un_url = "http://data.un.org/Data.aspx?d=POP&f=tableCode%3a44%3brefYear%3a" + year + "&c=2,3,6,8,10,12,14,16,17,18&s=_countryEnglishNameOrderBy:asc,refYear:desc,areaCode:asc&v=1"
    response = requests.get(un_url)
    soup = BeautifulSoup(response.content,"html.parser")
    final_page = re.findall('\d+', str(soup.find_all("span",{"id":"spanPageCountB"})))[0]
    
    for i in range(int(final_page)):
        editable_un_url = "http://data.un.org/Data.aspx?d=POP&f=tableCode%3a44%3brefYear%3a" + year + "&c=2,3,6,8,10,12,14,16,17,18&s=_countryEnglishNameOrderBy:asc,refYear:desc,areaCode:asc&v=" + str(i+1)
        response = requests.get(editable_un_url)
        soup = BeautifulSoup(response.content,"html.parser")
        mydivs = soup.find_all("div", {"class": "DataContainer"})
        interested_list = mydivs[0].find_all("td")
        final_index = int(len(interested_list)/11)
        for i in range(final_index):
            if (str(interested_list[(i*10)+i+5]).find("Total Foreign-Born") != -1) and (str(interested_list[(i*10)+i+4]).find("Total") != -1) and (str(interested_list[(i*10)+i+3]).find("Both Sexes") != -1):
                value = re.findall("\d+", str(interested_list[(i*10)+i+9]))[0]
                if (len(re.findall("\d+", str(interested_list[(i*10)+i+9]))) >= 2):
                    for i in np.arange(1,len(re.findall("\d+", str(interested_list[(i*10)+i+9])))):
                        value = value + re.findall("\d+", str(interested_list[(i*10)+i+9]))[i]
                managed_list.append([str(interested_list[(i*10)+i])[4:-5], str(interested_list[(i*10)+i+1])[4:-5], value])
