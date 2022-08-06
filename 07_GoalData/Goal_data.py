#imports
import pandas as pd
pd.set_option('display.max_colwidth', 500)

#import for requests
import requests

#import beautiful soup
from bs4 import BeautifulSoup

#we will use selenium webdriver
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
import os


from datetime import datetime,timedelta

currentSecond= datetime.now().second
currentMinute = datetime.now().minute
currentHour = datetime.now().hour

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year


"""
Function to get the data from source page using Beautiful soup

Input : page is the current page

Output: a dataframe
"""
def get_table(df_prev, driver):
    #strUrl = page.current_url
    #soup = BeautifulSoup(driver.page_source, "html5")
    df_result = pd.read_html(driver.page_source)
    df_result = df_result[2]
    df_result = pd.concat([df_prev, df_result])
    return df_result



"""
Function to get the table row and table date to get the xpath values for table row and table data

Input : a dataframe of calender from the website

Output: table row number and table data where we are looking for that date
"""
def get_tr_td(df_date):
    tr = 0
    td = 0
    for i,day in enumerate(df_date.columns):
        if len(df_date[df_date[day] == float(date)].index) != 0:
            tr = df_date[df_date[day] == float(date)].index.tolist()[0] +1
            td = i+1
    
    return tr, td


#get 30 days period
today = datetime.today()
yesterday = today - timedelta(days=1)
one_week_ago = today - timedelta(days=7)
thirty_days_ago = today - timedelta(days=30)




try:

    #Create an empty dataframe
    df = pd.DataFrame()

    #create webdriver instance
    driver = webdriver.Chrome()

    #get the url with login page
    driver.get("https://www.hk33.com/en/user/login-register")
    sleep(1)

    #sign in with username and password
    driver.find_element("name","email_or_username").send_keys("bekkandbutter@gmail.com")
    driver.find_element("name","password").send_keys("bekk1234")
    #click on the login button
    driver.find_element("xpath","/html/body/div[1]/main/div[4]/div[1]/form/div[6]/div/div[1]/div[2]").click()
    sleep(2)

    #click on image on top left corner to go to main page
    link = driver.find_element("id","header_logo").click()

    #click on hkGoal
    sleep(2)
    driver.find_element("xpath","/html/body/div[1]/main/div[2]/div[2]/div[2]/a").click()

    #click on to navigate
    sleep(2)
    driver.find_element("xpath","/html/body/div[1]/main/div[1]/table/tbody/tr/td[3]").click()
    sleep(1)
    driver.find_element("xpath","/html/body/div[1]/main/div[1]/div[3]/div[3]/div[1]/a[3]").click()
    sleep(1)
    driver.find_element("xpath","/html/body/div[1]/main/form/div[1]/div[1]/label/input").click()
    
    
     ##############################Select a year###################################

    #select a month to get the report on last 30 days
    #month = int(thirty_days_ago.month)


    ##############################Select A Month###################################

    #select a month to get the report on last 30 days
    #month = int(thirty_days_ago.month)
    month = int(input("Enter month in number of which you want to retrieve the data: "))
    #print("Thanks")

    driver.find_element("xpath",f"/html/body/div[4]/div/div/select[1]/option[{month-1}]").click()


    ###############################Select a date#####################################
    sleep(1)
    date = thirty_days_ago.day + 1      #Plus one is added if the current timezone is for IST

    #click on a date
    sleep(1)

    df_date = pd.read_html(driver.page_source)[3]
    tr, td = get_tr_td(df_date)
    driver.find_element("xpath",f"/html/body/div[4]/table/tbody/tr[{tr}]/td[{td}]/a").click()


    #clicking on Search Button
    sleep(1)
    driver.find_element("xpath","/html/body/div[1]/main/form/div[4]/div[1]").click()


    ################Select the number of entires to show ############################
    #click on drop and select 200
    sleep(1)
    driver.find_element("xpath","/html/body/div[1]/main/div[6]/select").click()
    sleep(1)
    driver.find_element("xpath","/html/body/div[1]/main/div[6]/select/option[3]").click()


    ################ Count and Iterate through all the available pages #######################

    #get the number of pages
    result = BeautifulSoup(driver.page_source, "html5")
    pages = result.find("div", class_="pagination_pages")
    count_pages =[page for i,page in enumerate(pages) if i%2 !=0]

    for i,num in enumerate(reversed(count_pages)):
        driver.find_element("xpath",f"/html/body/div[1]/main/div[9]/div[3]/div[{num.text}]").click()

        if len(count_pages)-i == len(count_pages):
            df_goal = get_table(df, driver)
        else:
            df_goal = get_table(df_goal, driver)

    
except Exception:
    print("Please try running the code again. Page crashed")
    pass



#export to excel the raw data

cwd = os.getcwd()
writer = pd.ExcelWriter(cwd + "/goal_data.xlsx", engine='openpyxl')
df_goal.to_excel(writer, sheet_name='Sheet1')
#df2.to_excel(writer, sheet_name='Sheet1', merge_cells = True, startrow=1)

writer.close()


cwd = os.getcwd()
df_practice = pd.read_excel(cwd+"/goal_data.xlsx", index_col=0, header=[0,1])
df_practice.rename(columns={'球賽編號':'A球賽編號', '開賽時間':'B開賽時間','賽事類別':'C賽事類別','主隊':'D主隊','客隊':'E客隊',
                            '角球數':'AV角球數','賠率':'BB賠率','賽果HAD':'BA賽果HAD'
                           
                           }, inplace=True)


#let's start splitting the data from the end columns first

df_practice[['AY全場比數','AZ全場比數']] = df_practice['全場比數']['全場比數'].str.split(':', expand=True)


#dropping the column 全場比數
df_practice = df_practice.drop('全場比數', axis=1)


#splitting the column 半場比數
df_practice[['AW半場比數','AX半場比數']] = df_practice['半場比數']['半場比數'].str.split(':', expand=True)
df_practice['AW半場比數'] = df_practice['AW半場比數'].str.replace("(","")
df_practice['AX半場比數'] = df_practice['AX半場比數'].str.replace(")","")
df_practice = df_practice.drop('半場比數', axis=1)
df_practice.head()

#split the data by empty space
df_practice[['F主','I主','L主','O主']]= df_practice['百家平均初盤百家平均終盤馬會初盤馬會終盤']['主'].str.split(" ",expand=True)
df_practice[['G和','J和','M和','P和']]= df_practice['百家平均初盤百家平均終盤馬會初盤馬會終盤']['和'].str.split(" ",expand=True)
df_practice[['H客','K客','N客','Q客']]= df_practice['百家平均初盤百家平均終盤馬會初盤馬會終盤']['客'].str.split(" ",expand=True)
df_practice = df_practice.drop('百家平均初盤百家平均終盤馬會初盤馬會終盤', axis=1, level=0)



df_practice['主1'] = df_practice['百家平均初盤 SD / CV百家平均終盤 SD / CV']['主'].str.replace(" / ", "")
df_practice[['R主','S主','X主','Y主']] = df_practice['主1'].str.split(" ",expand=True)
df_practice['和2'] = df_practice['百家平均初盤 SD / CV百家平均終盤 SD / CV']['和'].str.replace(" / ", "")
df_practice[['T和','U和','Z和','AA和']] = df_practice['和2'].str.split(" ",expand=True)
df_practice['客3'] = df_practice['百家平均初盤 SD / CV百家平均終盤 SD / CV']['客'].str.replace(" / ", "")
df_practice[['V客','W客','AB客','AC客']] = df_practice['客3'].str.split(" ",expand=True)
df_practice.drop('百家平均初盤 SD / CV百家平均終盤 SD / CV', axis=1, level=0, inplace=True)
df_practice = df_practice.drop(['主1','和2','客3'],axis=1)


#dealing with 馬會讓球初盤馬會讓球終盤 column
df_practice[['AD球數','AG球數']] = df_practice['馬會讓球初盤馬會讓球終盤']['球數'].str.split(" ",expand=True)
df_practice[['AE主','AH主']] = df_practice['馬會讓球初盤馬會讓球終盤']['主'].str.split(" ",expand=True)
df_practice[['AF客','AI客']] = df_practice['馬會讓球初盤馬會讓球終盤']['客'].str.split(" ",expand=True)
df_practice.drop('馬會讓球初盤馬會讓球終盤', axis=1, level=0, inplace=True)


#dealing with 馬會大細初盤馬會大細終盤 column
df_practice[['AJ球數','AM球數']] = df_practice['馬會大細初盤馬會大細終盤']['球數'].str.split(" ",expand=True)
df_practice[['AK大','AN大']] = df_practice['馬會大細初盤馬會大細終盤']['大'].str.split(" ",expand=True)
df_practice[['AL細','AO細']] = df_practice['馬會大細初盤馬會大細終盤']['細'].str.split(" ",expand=True)
df_practice.drop('馬會大細初盤馬會大細終盤', axis=1, level=0, inplace=True)


#dealing with 馬會角球初盤馬會角球終盤 column
df_practice[['AP球數','AS球數','dummy1']] = df_practice['馬會角球初盤馬會角球終盤']['球數'].str.split(" ",expand=True)
df_practice[['AQ大','AT大','dummy2']] = df_practice['馬會角球初盤馬會角球終盤']['大'].str.split(" ",expand=True)
df_practice[['AR細','AU細','dummy3']] = df_practice['馬會角球初盤馬會角球終盤']['細'].str.split(" ",expand=True)
df_practice.drop(['馬會角球初盤馬會角球終盤','dummy1','dummy2','dummy3'], axis=1, level=0, inplace=True)


#get the column names
cols=[]

for col_names in df_practice.columns.sort_values().tolist():
    cols.append(col_names[0])


for i in range(len(cols)):
    print(i, cols[i])


#rearrange the columns so that we get data from A to BB
cols = cols[26:27]  + cols[-25:] + cols[:26] + cols[27:29]

#get the final dataframe and then export it to csv
df_final = df_practice[cols]

#export to excel the final processed data

cwd = os.getcwd()
writer = pd.ExcelWriter(cwd + "/goal_data.xlsx", engine='openpyxl')
df_final.to_excel(writer, sheet_name='Sheet1')
#df2.to_excel(writer, sheet_name='Sheet1', merge_cells = True, startrow=1)
writer.close()

#export to csv
cwd = os.getcwd()
df_final.to_csv(cwd + "/final_goal_data.csv",encoding="utf-8-sig")