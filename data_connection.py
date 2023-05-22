# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 18:41:13 2023

@author: Kuba
"""

import pyodbc
import pandas as pd

def get_sql_data(driver,server,database,table):
    #establish connection
    cnxn = pyodbc.connect(
        'DRIVER='+driver+';'
        'SERVER='+server+';'
        'DATABASE='+database+';'
        'Trusted_Connection=yes')
    
    #execute query
    query = 'SELECT * FROM '+database+'.dbo.'+table
    cursor = cnxn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    #save data in df
    data = pd.read_sql(query, cnxn)
    
    #close connection
    cnxn.close()
    
    return data
    
def get_excel_data(path):
 
    #save data into a dataframe
    data = pd.read_excel(path)
    return data
 
