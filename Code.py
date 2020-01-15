#!/usr/bin/env python
# coding: utf-8

# <h1 style='margin-bottom:10px;margin-top:0;' align = 'center'>Spectrum Data Collection</h1>
# <h3 style = 'margin-top:0;margin-bottom:8px;' align = 'center'>ECE1551: Mobile Broadband Radio Access Networks</h3>
# <h4 style = 'margin-top:0;margin-bottom:5px;' align = 'center'>Navaneetha Krishna Madan Gopal</h4>
# <h4 style = 'margin-top:0;margin-bottom:20px;' align = 'center'>1005171127</h4>
# 
# ### Abstract
# With the initial implementations of 5G in Canada aroud the corner, it is of great importance for providers to analyze various aspects of the spectrum. Data regarding the bands owned by operators, possible carrier aggregation scenarios will help tailor the solutions deployed to achieve better datarates. Data regarding the population and area covered, tiers spanned will help providers optmize their deployment solutions to obtain optimum utility of the resources deployed from an economic standpoint. Possible partnerships with other providers can also be identified through the analysis of this spectrum data. 
# 
# Collecting all this data manually is a daunting and wasteful task. This project is a solution to automate the process of collecting data regarding the licenses held by various operators in different categories. Besides this, the frequency ranges, bandwidth and the poplation covered by the operator in each of the licences can also be obtained through this code.
# 
# ### Programming environment
# The process of extracting data from websites called <em>web scraping</em> has been implemented using Python 3.7.1 in the Jupyter Notebook environment. The libraries being used are:
# <ul style="list-style-type:circle;margin-top:0;">
#   <li>selenium - used to control the opening, clicking and navigation in the web browser. In this case, Google Chrome is being used</li>
#   <li>BeautifulSoup - used to extract information from the contents displayed on the webpage</li>
#   <li>pandas - used to handle the extracted data and convert into convenient csv format</li>
#   <li>requests</li>
#   <li>tabula - used to obtain data from tables in the downloaded PDF files</li>
#   <li>lxml - works with BeautifulSoup to help extract data from the webpage</li>
#   <li>os - used to store, delete and perform other directory related tasks on the system running the code</li>
# </ul>
# 
# ### Program flow
# The program flow can be divided into two pipelines. The first pipeline extracts all the licences in the user specified licence category from the [Spectrum Licence Browser](https://sms-sgs.ic.gc.ca/licenseSearch/searchSpectrumLicense?execution=e1s14). The data collected in this pipeline is:
# <ul style="list-style-type:circle;margin-top:0;">
#   <li>Authorizatin Number</li>
#   <li>Former Authorization Number</li>
#   <li>Company Name</li>
#   <li>Account Number</li>
#   <li>Licence Category</li>
#   <li>Area Code (Tier)</li>
#   <li>Area Name</li>
#   <li>Subservice</li>
#   <li>Poplation</li>
# </ul>
# This is shown in the following flowcart. 
# 
# <img src="Fs1.png" width="875" style="bottom-margin:10px;">
# 
# The second pipeline extracts data regarding each of the licences. PDF files for each licence are downloaded from [Search for Virtual Licence or Certificate](https://sms-sgs.ic.gc.ca/licenseSearch/searchVirtualLicense?execution=e3s1). From the downloaded PDF file, the following data is extracted:
# <ul style="list-style-type:circle;margin-top:0;">
#   <li>Effective date</li>
#   <li>Expiry date</li>
#   <li>Licence number</li>
#   <li>Account number</li>
#   <li>Service type</li>
#   <li>Licence holder type</li>
#   <li>Frequency Ranges</li>
#   <li>Spectrum</li>
#   <li>Conditions</li>
# </ul>
# This is shown in the following flowchart.
# 
# <img src="Fs2.png" width="875" style="bottom-margin:15px;">
# 
# ### Special features
# One common problem with web scraping is the speed of the internet connection used to perform the tasks. If the connection is slow, the code will raise errors about not finding certain elements in the webpage as it has still noit been loaded. This can cause the entire data extraction pipeline to creash after a considerable amount of work has been done. This problem has been solved by incorporaing a "wait till button is loaded" feature thus increasing the reliability of this solution.
# 
# The option to also keep or delete the downloaded licence PDF files is provided to avoid unwanted clutter and memory consumption on the device.

# In[1]:


# import the required modules
from selenium import webdriver
import selenium.webdriver.support.ui as UI
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
import lxml
import time
import pandas as pd
from selenium.webdriver.common.by import By
import os
import tabula

# set chrome preference to download PDF rather than display on the Chrome Viewer
download_dir = "Z:\Courses\MBRAN\Project\Report Downloads"
options = webdriver.ChromeOptions()
prefs = {"plugins.always_open_pdf_externally": True, "download.default_directory": download_dir} 
options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path = r'C:\Users\navan\ChromeDriver\chromedriver.exe', chrome_options = options)
# open Chrome and load the Spectrum Licence Browser
driver.get('https://sms-sgs.ic.gc.ca/licenseSearch/searchSpectrumLicense?execution=e1s14')
print('Hello! Welcome to %s'%driver.title)


# In[2]:


# find the dropdown menu to choose the Licence Category and print its values
licCat = UI.Select(driver.find_element_by_id("licenceCategory"))
print("Please choose one of the following Licence Ccategories")
licCatList = []
for ele in licCat.options:
    print(ele.get_attribute("value"))
    licCatList.append(ele.get_attribute("value"))


# In[3]:


# Obtain the Licence Category the user is interested in
choice = input("You have chosen to view ")
if choice not in licCatList:
    raise ValueError("Sorry, try again with a valid Licence Category")


# In[4]:


def get_data(driver):
    try:
        UI.WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'span-8']")))
    except TimeoutException:
        no_res = int([l.text for l in driver.find_elements_by_class_name("form-group")][-1].split()[-1])
        soup = BeautifulSoup(driver.page_source, 'lxml')
        required_table = soup.find("table", id = 'spectrumLicenceSearchResultTable')
        no_pages = int(no_res / 20 - 0.0001) + 1
        rows = []
        pop_list = []
        for i in range(no_pages):
            soup = BeautifulSoup(driver.page_source, 'lxml')
            required_table = soup.find("table", id = 'spectrumLicenceSearchResultTable')
            for row in required_table.tbody.find_all('tr'):
                row_text = [l.text.strip() for l in row.find_all("td")]
                driver.find_element_by_link_text(str(row_text[0])).click()
                rows.append(row_text)
                p = int(UI.WebDriverWait(driver, 30).
                        until(EC.presence_of_element_located
                              ((By.XPATH,"//table[@id='licenceInformationTable']/tbody/tr[6]/td[2]")))
                        .text.split(" ")[0])
                pop_list.append(p)
                driver.back()
            if no_pages == 1 or i == no_pages - 1:
                break
            driver.find_element_by_xpath("//a[contains(text(),'Next')]").click()
            time.sleep(2)
        headers = [header.text for header in required_table.find_all('th')]
        licences = pd.DataFrame(rows, columns = headers)
        pop_df = pd.DataFrame(pop_list, columns = ['Population'])
        licences = pd.concat([licences, pop_df], axis = 1)
        return licences
    else:
        return pd.DataFrame()


# In[5]:


licCat.select_by_value(choice)
driver.find_element_by_xpath("//input[@type='submit' and @value='Search']").click()
try:
    UI.WebDriverWait(driver, 3).until(EC.presence_of_element_located
                                      ((By.XPATH, "//div[@id='errorMessageSpectumLicense']")))
except TimeoutException:
    status = 'Peace'        
else:
    status = 'Hmm'


# In[6]:


if status == 'Hmm':
    
    #driver2 = webdriver.Chrome(executable_path = r'C:\Users\navan\ChromeDriver\chromedriver.exe')
    #driver2.get('http://www.ic.gc.ca/eic/site/smt-gst.nsf/eng/sf11437.html')
    #driver2.find_element_by_xpath("//button[contains(text(),'Expand all content / collapse all content')]").click()
    #all_opt = UI.WebDriverWait(driver2, 10).until(EC.presence_of_element_located
    #                                              ((By.XPATH,"//select[@name = 'tA1_length']")))
    #UI.Select(all_opt).select_by_value("-1")
    #comp_col = [l.text for l in driver2.find_elements_by_xpath("//table[@id ='tA1']/tbody/tr/td[3]")]
    #comp_list = list(set(comp_col))
    #driver2.close()
    comp_list = ['SSI Micro', 'Tbaytel']
    licences = pd.DataFrame()
    for comp in comp_list:
        comp_field = driver.find_element_by_xpath("//input[@id='companyName']")
        comp_field.send_keys(comp)
        driver.find_element_by_xpath("//input[@type='submit' and @value='Search']").click()
        comp_lic = get_data(driver)
        time.sleep(2)
        comp_field = driver.find_element_by_xpath("//input[@id='companyName']")
        comp_field.clear()
        if comp_lic.empty:
            pass
        else:
            licences = licences.append(comp_lic, ignore_index = True)
        
else:
    licences = get_data(driver)
    if licences.empty:
        raise SystemExit('There are no active licences in this category!')
path = 'Z:\Courses\MBRAN\Project\CSV exports'
csv_name = choice + '_licenses.csv'
csv_path = os.path.join(path, csv_name)
licences.to_csv(csv_path, index = False, index_label = False)


# In[7]:


path = 'Z:\Courses\MBRAN\Project\CSV exports'
csv_name = choice + '_licenses.csv'
csv_path = os.path.join(path, csv_name)
licences.to_csv(csv_path, index = False, index_label = False)


# A csv file of all the licences granted has been saved to the path specified in the pervious cell. Please look it up and choose the authorization number you are interested in and enter into the next field.

# In[8]:


keep = input("Would you like to keep the license PDF flies? Type yes if you want to.")


# In[9]:


# open the Search for Virtual Licence or Certificate page
driver.get('https://sms-sgs.ic.gc.ca/licenseSearch/searchVirtualLicense?execution=e3s1')
print('Hello! Welcome to %s'%driver.title)
df1 = pd.DataFrame()
df2 = pd.DataFrame()
df3 = pd.DataFrame()
# iterate over all authorization numbers and obtain the data specified in pipeline 2
for a_n in list(licences["Authorization Number"]):
    field = driver.find_element_by_name("licenseName")
    field.send_keys(a_n)
    driver.find_element_by_xpath("//input[@type='submit' and @value='Search']").click()
    UI.WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "downloadLicenceAsPDFButton"))).click()
    driver.back()
    UI.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,"licenseName"))).clear()    
    file_name = "\ISED-"+ a_n + ".pdf"
    file_path = "Z:\Courses\MBRAN\Project\Report Downloads" + file_name
    while not os.path.exists(file_path):
        pass
    table = tabula.read_pdf(file_path, multiple_tables = True)
    if not (keep == 'yes' or keep == 'Yes'):
        os.unlink(file_path)
    if len(table[2]) == 0:
        temp = table[3].iloc[2:, 0:6]
        for i in range(temp.shape[0]):
            for j in range(temp.shape[1] - 1):
                temp.iloc[i,j] = float(temp.iloc[i,j].replace(' ','').replace('kHz','').replace('MHz',''))
        l = len(table[3].iloc[2:,:])
    else:
        temp = table[2].iloc[2:, 0:6]
        for i in range(temp.shape[0]):
            for j in range(temp.shape[1] - 1):
                temp.iloc[i,j] = float(temp.iloc[i,j].replace(' ','').replace('kHz','').replace('MHz',''))
        l = len(table[2].iloc[2:,:])        
    if l > 1:
        df1 = df1.append(pd.concat([table[0].iloc[1,:]] * l, ignore_index = 1, axis = 1).T, ignore_index = 1)
        df2 = df2.append(pd.concat([table[1].iloc[1,:]] * l, ignore_index = 1, axis = 1).T, ignore_index = 1)
    else:
        df1 = df1.append(table[0].iloc[1,:].T, ignore_index = True)
        df2 = df2.append(table[1].iloc[1,:].T, ignore_index = True)
    df3 = df3.append(temp, ignore_index = 1)  
df1.columns = [table[0].iloc[0,:]]
df2.columns = [table[1].iloc[0,:]]
if len(table[2]) == 0:
    df3.columns = [w.replace('\r',' ') for w in (list(table[3].iloc[1,0:4]) + list(table[3].iloc[0,1:3]))]
else:
    df3.columns = [w.replace('\r',' ') for w in (list(table[2].iloc[1,0:4]) + list(table[2].iloc[0,1:3]))]
data = pd.concat([df1, df2, df3], axis = 1)
csv_name = choice + '_licenceDetails.csv'
csv_path = os.path.join(path, csv_name)
data.to_csv(csv_path, index = False, index_label = False)

