# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 21:46:09 2023

@author: Kuba
"""

#main.py

from flask import Flask 
from flask import render_template
from flask import request
from Revenue_recognition import Revenue_recognition_start
from Revenue_allocation import Revenue_allocation_start


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/revenue_parameters', methods=['GET', 'POST'])
def rev_rec_pars():
    if request.method == 'POST':        
        EMP_ID = request.form['input1']
        Org_name = request.form['input2']
        Rev_hier_1 = request.form['input3']
        Rev_hier_2 = request.form['input4']
        Revenue_recognition_start(EMP_ID,Org_name,Rev_hier_1,Rev_hier_2)
        pass
    return render_template('recognition.html')

@app.route('/revenue_allocation', methods=['GET', 'POST'])
def rev_rec_allo():
    if request.method == 'POST':        
        EMP_ID = request.form['input1']
        Org_name = request.form['input2']
        Rev_hier_1 = request.form.getlist('input3')
        Rev_hier_2 = request.form['input4']
        Revenue_allocation_start(EMP_ID,Org_name,Rev_hier_1,Rev_hier_2)
        pass
    return render_template('allocation.html')



app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == '__main__':
    app.run(debug=True)
