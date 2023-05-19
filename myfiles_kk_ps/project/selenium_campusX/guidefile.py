#open google.com
#search campusx
#learwith.campusx.in
#dsmp course page

"""
Note:
    1.check for service path always 
"""
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By   #for finding xpath
from selenium.webdriver.common.keys import Keys 

import time

s = Service("C:\\keshav\\myfiles_kk_ps\\project\\selenium_campusX\\edgedriver_win64\\msedgedriver.exe")

# Set Edge options for keeping window on oth getting close automatically
edge_options = Options()
edge_options.add_experimental_option("detach", True)  
driver = webdriver.Edge(service=s, options=edge_options)

driver.get("https://www.google.com/")
# time.sleep(2)
#fetch search box using xpath
user_input = driver.find_element(by=By.XPATH,value='//*[@id="APjFqb"]')
user_input.send_keys('Campusx')
# time.sleep(1)

user_input.send_keys(Keys.ENTER)

link = driver.find_element(by=By.XPATH,value='//*[@id="rso"]/div[2]/div/div/div/div/div/div[1]/div/a/h3')
link.click()

