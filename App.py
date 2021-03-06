# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:52:12 2020
@author: YUSS
"""
import pathlib
import csv
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
import sys
import os
from werkzeug import secure_filename
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, send_from_directory
from flask_restful import Resource
import webbrowser
import json

current_dir = pathlib.Path.cwd()

app = Flask(__name__, template_folder = 'templates')

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.secret_key = "secret key"
app.config['WORK_FOLDER'] = current_dir / 'work'

ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def upload_form():
    return render_template('file_upload_form.html')
  
@app.route('/', methods=['GET', 'POST'])
def getAddress():
   if request.method == 'POST':
       if 'file' not in request.files:
           print('No file attached in request')
           return redirect(request.url)
       file = request.files['file']
       if file.filename == '':
           print('No file selected')
           return redirect(request.url)
       if file and allowed_file(file.filename):
           filename = secure_filename(file.filename)
           file.save(os.path.join(app.config['WORK_FOLDER'], filename))
           a = process_file(os.path.join(app.config['WORK_FOLDER'], filename))
           return a
   return render_template('file_upload_form.html')
      
def process_file(filename):
    
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        # approximate radius of earth in mm
        radius = 6371.0 * 1000 
        dlat = radians(lat2-lat1)
        dlon = radians(lon2-lon1)
        a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) \
            * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = radius * c
        return d    
        
    with open(filename, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      points = []
      links = []
      for row in reader:  
        p = {"name": list(row.items())[0][1], "address (La/Lo)": (list(row.items())[1][1], list(row.items())[2][1])}    
        points.append(p) 
        
    l = []
    for point in points:
        for v in point.values():
            l.append(v)
    
    links = []
    for i in range(0, len(l) -1 , 2):    
        if(i>0):
            for j in range(i-2, 0, -2):
                    links.append({'name': l[i] + l[j], 'distance': calculate_distance(float(l[i+1][0]), float(l[i+1][1]), float(l[j+1][0]), float(l[j+1][1]))})
        else:
            for j in range(i+2, len(l), 2):
                    links.append({'name': l[i] + l[j], 'distance': calculate_distance(float(l[i+1][0]), float(l[i+1][1]), float(l[j+1][0]), float(l[j+1][1]))})
    
    
    jsonf = {"Points" : points, "Links" : links}
    with open(filename[:-3] + 'json', 'w', encoding = "utf-8") as f:
        json.dump(jsonf, f, ensure_ascii=False, indent=4)            
    return jsonify({"points": points, "links": links})    
               
            
if __name__ == "__main__":
    webbrowser.open('http://localhost:5000')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
