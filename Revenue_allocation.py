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
import math

def Revenue_allocation_start(ID,Org,Hier1,Hier2):
    #Write log file
    Hier2 = int(Hier2)
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    with open(f'log/{ID}_revenue_allocation.txt', 'w') as file:
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
    
    #save data into a dataframe
    #data = get_sql_data('ODBC Driver 17 for SQL Server','server_name','database_name','table_name')
    
    #calculation module
    
    #create an empty dfs to hold the records to allocate and pre-allocation analysis 
    records_out_of_target_range = pd.DataFrame()
    allocation_parameters = pd.DataFrame(columns=['Hierarchy 1', 'Min rate', 'Max rate', 'Records required to allocate', 'Amount of records', 'Required valid records', 'Amount of valid records' ])
    
    for Hierarchy in Hier1:    
        #apply user-defined filtering criteria
        #since Hier1 parameter is likely to contain a list, a loop is required
        filtered_data = data[(data['Hierarchy 1'] == Hierarchy) & (data['Hierarchy 2'] <= Hier2)]
        #establish variables needed for compliance calculation
        data_sorted = filtered_data.sort_values('Discount', ascending=False)
        N = len(data_sorted)
        #percentage required in compliance assessment
        N1 = math.ceil(N * 0.6)
        #discount range
        discount_range = 0.3
        Max_discount = data_sorted['Discount'].max()
        Min_discount = data_sorted['Discount'].min()
        #amount of iterations required to go through all of the combinations possible
        iteration_amt = int((Max_discount - Min_discount - discount_range) * 100)
        amount_of_compliant_ranges = 0
        #dataframe to hold key parameters of each iteration
        range_parameters = pd.DataFrame(columns=['Records count', 'Min rate', 'Max rate', 'Required count'])
        
        #For each 30% range between max and min discount range capture the amount of compliant revenue entries and add line to range parameters df
        for i in range(iteration_amt):
            Lower_rate = Min_discount + i/100
            Upper_rate = Lower_rate + discount_range
            
            data_range = data_sorted[(data_sorted['Discount'] >= Lower_rate) & (data_sorted['Discount'] < Upper_rate)]
            
            if len(data_range) >= N1:
                amount_of_compliant_ranges += 1
            else:
                pass
            range_parameters = range_parameters.append({'Records count': len(data_range), 'Min rate': Lower_rate, 'Max rate': Upper_rate, 'Required count': N1}, ignore_index=True)
        
        #sort range parameters to capture the range with the most amount of compliant records to minimize allocation movement
        range_parameters = range_parameters.sort_values('Records count', ascending = False)
        #capture new records which are not falling in optimal percentage range and add them to already existing df
        new_records_out_of_target_range = data_sorted[(data_sorted['Discount'] < range_parameters.iloc[0]['Min rate']) | (data_sorted['Discount'] > range_parameters.iloc[0]['Max rate'])]
        records_out_of_target_range =  pd.concat([records_out_of_target_range,new_records_out_of_target_range],ignore_index = True)
        #capture allocation used in current iteration and add them to already existing df
        new_allocation_row = {'Hierarchy 1' : Hierarchy, 'Min rate' : range_parameters.iloc[0]['Min rate'] , 'Max rate' : range_parameters.iloc[0]['Max rate'], 'Records required to allocate' : range_parameters.iloc[0]['Required count'] - range_parameters.iloc[0]['Records count'] , 'Amount of records' : N, 'Required valid records' : N1, 'Amount of valid records' : range_parameters.iloc[0]['Records count']}    
        allocation_parameters = allocation_parameters.append(new_allocation_row, ignore_index = True)
    
    #create empty dfs to hold current iteration and final allocation records
    new_allocation_records = pd.DataFrame()
    suggested_allocation_records = pd.DataFrame()

    for Hierarchy in Hier1:
        #check if any allocation is required
        if allocation_parameters.loc[allocation_parameters['Hierarchy 1'] == Hierarchy, 'Records required to allocate'].item() > 0:
            #filter records needed for allocation from unwanted records and sort them in descending order to minimize the impact
            new_allocation_records = records_out_of_target_range[(records_out_of_target_range['Discount'] >= allocation_parameters.loc[allocation_parameters['Hierarchy 1'] == Hierarchy, 'Min rate'].item()) & (records_out_of_target_range['Discount'] < allocation_parameters.loc[allocation_parameters['Hierarchy 1'] == Hierarchy, 'Max rate'].item())]
            new_allocation_records = new_allocation_records.sort_values('Order amount').head(int(allocation_parameters.loc[allocation_parameters['Hierarchy 1'] == Hierarchy, 'Records required to allocate'].item()))
            #catch the filtering index and drop records used for allocation from unwanted records
            filtered_index = new_allocation_records.index
            records_out_of_target_range = records_out_of_target_range.drop(filtered_index)
            #add a column with suggested allocation hierarchy/category and join new and already existing records
            new_allocation_records['Suggested Hierarchy 1'] = Hierarchy
            suggested_allocation_records = suggested_allocation_records.append(new_allocation_records, ignore_index = True)
        else:
            #pass if there's no allocation needed
            pass
           
    #eqalize amount of rows
    
    #check if any allocation is happening
    if not suggested_allocation_records.empty:
        #establish new df to asses how allocation impacted each category
        counts = suggested_allocation_records.groupby(['Hierarchy 1', 'Suggested Hierarchy 1']).size().reset_index(name='count')
        #iterate through the records and create allocation suggestion to equalize the amount of records in all categories
        for index, row in counts.iterrows():
            new_allocation_records = records_out_of_target_range[records_out_of_target_range['Hierarchy 1'] == row['Suggested Hierarchy 1']]
            new_allocation_records = new_allocation_records.sort_values('Order amount').head(row['count'])
            #if allocation is not possible - leave a message for the user
            if len(new_allocation_records) < row['count']:
                warning_line = pd.DataFrame({'Suggested Hierarchy 1': [row['Hierarchy 1']], 'Comment': ['Not enough records to allocate']})
                suggested_allocation_records = pd.concat([suggested_allocation_records, warning_line], ignore_index=True)
            else:
                pass
            #drop used records from unwanted records df and add records to the final table
            filtered_index = new_allocation_records.index
            records_out_of_target_range = records_out_of_target_range.drop(filtered_index)
            new_allocation_records['Suggested Hierarchy 1'] = row['Hierarchy 1']
            suggested_allocation_records = suggested_allocation_records.append(new_allocation_records, ignore_index = True)
    else:
        #pass if there's no allocation needed
        pass
    
    #save allocation parameters and suggested allocation to xlsx files
    allocation_parameters.to_excel('output/'+ID+' Allocation parameters.xlsx', index=False)
    suggested_allocation_records.to_excel('output/'+ID+' Suggested allocation records.xlsx', index=False)
    
    return

