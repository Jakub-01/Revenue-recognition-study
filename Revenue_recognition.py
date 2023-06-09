# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 18:41:13 2023

@author: Kuba
"""
import pandas as pd
import os
from datetime import datetime
from data_connection import get_sql_data
from data_connection import get_excel_data

def Revenue_recognition_start(ID,Org,Hier1,Hier2):
    #Write log file
    Hier2 = int(Hier2)
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    with open(f'log/{ID}.txt', 'w') as file:
        file.write(f'Employee ID: {ID}\n')
        file.write(f'Organization name: {Org}\n')
        file.write(f'Revenue hierarchy level 1: {Hier1}\n')
        file.write(f'Revenue hierarchy level 2: {Hier2}\n')
        file.write(f'timestamp: {timestamp}\n')   
    #get data    
    
    #excel module - cam be used when it's not possible to connect to SQL
    
    #define file path
    current_path = os.getcwd()
    filepath = os.path.join(current_path,"data","Revenue_Data.xlsx")
    #call a function
    data = get_excel_data(filepath)

    #sql module
    #data = get_sql_data('ODBC Driver 17 for SQL Server','server_name','database_name','table_name')
    
    #calculation module
    
    #apply user-defined filtering criteria
    filtered_data = data[(data['Hierarchy 1'] == Hier1) & (data['Hierarchy 2'] <= Hier2)]
    #establish variables needed for compliance calculation
    data_sorted = filtered_data.sort_values('Discount', ascending=False)
    N = len(data_sorted)
    #percentage required in compliance assessment
    N1 = N * 0.6
    #discount range
    discount_range = 0.3
    Max_discount = data_sorted['Discount'].max()
    Min_discount = data_sorted['Discount'].min()
    #amount of iterations required to go through all of the combinations possible
    Iteration_amt = int((Max_discount - Min_discount - discount_range) * 100)
    Amount_of_compliant_ranges = 0
    
    #For each 30% range between max and min discount range check if it contains required number of transactions
    data_sorted
    for i in range(Iteration_amt):
        Lower_rate = Min_discount + i/100
        Upper_rate = Lower_rate + discount_range
        
        data_range = data_sorted[(data_sorted['Discount'] >= Lower_rate) & (data_sorted['Discount'] < Upper_rate)]
        
        #if the given discount ratio range contains the required amount of rows then increment the appropriate variable by 1
        if len(data_range) >= N1:
            Amount_of_compliant_ranges += 1
            pass
     

    
    #save file 
    current_time2 = datetime.now()
    timestamp2 = current_time2.strftime("%Y-%m-%d_%H-%M-%S")
    if Amount_of_compliant_ranges > 0:
        with open(f'output/Output analysis generated by {ID}.txt', 'w') as file:
            file.write(f'Revenue recognition calculated for {Org} organization, for hierarchy {Hier1}, on level# {Hier2} is compliant. There is following amount of compliant discount percentage ranges considering 1 percentage point increments: {Amount_of_compliant_ranges}.\n')
            file.write(f'Analysis calculated on {timestamp2}\n')
    else:
        with open(f'output/Output analysis generated by {ID}.txt', 'w') as file:
            file.write(f'Revenue recognition calculated for {Org} organization, for hierarchy {Hier1}, on level# {Hier2} is not compliant. Tool was not able to find any compliant range considering 1 percentage point increments in calculation.\n')
            file.write(f'Analysis calculated on {timestamp2}\n')

    return