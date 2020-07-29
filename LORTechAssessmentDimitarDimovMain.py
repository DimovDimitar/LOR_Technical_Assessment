# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 10:00:48 2020

@author: dimit
"""

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
os.chdir(r"C:\Users\dimit\Desktop\Laing O'Rourke Tech Assessment")

data = pd.read_csv("Online Retail Database.csv", parse_dates=["InvoiceDate"])

#-------------------------------------#
# Pre-processing and cleaning #
#-------------------------------------#

# get more information about data types and missing values

data.info()
data.describe()

data.head(20)

# I noticed the C string in the Invoices column whilst initial screening in Excel

data.InvoiceNo.str.contains("C").sum()
data = data[data.InvoiceNo.astype(str).str.contains("C") == False]

# check for and remove outliers

data[data['UnitPrice']>500].groupby(["StockCode"]).tail(20)
data = data[~data['StockCode'].isin(['DOT',"POST", "M", "B", "AMAZONFEE"])]

# typos / errors in the Quantity column - important to remove those 
# for next steps and calculating the total revenue

data = data[data.Quantity > 0]
data['TotalSales'] = data['Quantity'].multiply(data['UnitPrice'])

# final check for outliers

data[data.Quantity > 5000]
data = data[data.Quantity < 5000]

# remove empty descriptions and duplicates

print (data.Description.isnull().sum())
data = data[data.Description.isnull() == False]
data = data.drop_duplicates()

#-------------------------------------#
# Export both databases for tableau visualisations #
#-------------------------------------#

data.info()
data.describe()

products_database = data 
customers_database = data[data.CustomerID.isnull() == False]

products_database.to_excel("Products Database.xlsx")
customers_database.to_excel("Customers Database.xlsx")

#-------------------------------------#
# RFM Analysis #
#-------------------------------------#

import datetime as dt
now = dt.date(2011,12,9)
customers_database['Date'] = customers_database['InvoiceDate'].dt.date
customers_database.head()

recency_data = customers_database.groupby(by='CustomerID',
                                          as_index=False)['Date'].max()
recency_data.columns = ['CustomerID','LastPurshaceDate']
recency_data.head()
recency_data['Recency'] = recency_data['LastPurshaceDate'].apply(lambda x: 
                                                                 (now - x).days)
recency_data.drop('LastPurshaceDate',axis=1,inplace=True)

data_copy=customers_database
# drop duplicates
data_copy.drop_duplicates(subset=['InvoiceNo', 'CustomerID', "Country"], keep="first",
                          inplace=True)
#calculate frequency of purchases
frequency_data = data_copy.groupby(by=['CustomerID'], as_index=False)['InvoiceNo'].count()
frequency_data.columns = ['CustomerID','Frequency']
frequency_data.head()

monetary_data = customers_database.groupby(by='CustomerID',as_index=False).agg({'TotalSales': 'sum'})
monetary_data.columns = ['CustomerID','Monetary']
monetary_data.head()

rfm_data = recency_data.merge(frequency_data.merge(monetary_data,on='CustomerID'),on='CustomerID')
rfm_data.head()

#-------------------------------------#
# Export RFM data for visualisations
#-------------------------------------#

rfm_data.to_excel("RFM_data.xlsx")