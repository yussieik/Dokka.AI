# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:52:12 2020

@author: YUSS
"""
import pathlib
import csv
from math import sin, cos, sqrt, atan2, radians
import os
from werkzeug import secure_filename
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, send_from_directory
import webbrowser


current_dir = pathlib.Path.cwd()

app = Flask(__name__, template_folder = 'templates')
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = current_dir / 'uploads'
app.config['DOWNLOAD_FOLDER'] = current_dir / 'downloads'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('file_upload_form.html')

#@app.route('/', methods=['GET','POST'])
#def upload_file():
#	if request.method == 'POST':
#        # check if the post request has the file part
#		if 'file' not in request.files:
#			flash('No file part')
#			return redirect(request.url)
#		file = request.files['file']
#		if file.filename == '':
#			flash('No file selected for uploading')
#			return redirect(request.url)
#		if file and allowed_file(file.filename):
#			filename = secure_filename(file.filename)
#			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
#			flash('File successfully uploaded')
#			return redirect('/')
#		else:
#			flash('Allowed file types are csv')
#			return redirect(request.url)
  
@app.route('/', methods=['GET', 'POST'])
def get_address():
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
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           return redirect(url_for('uploaded_file', filename=filename))
   return render_template('get_address.html')
      
def process_file(points):
    
    def upload_file():
        if request.method == 'POST':
          points = request.files['file']
          points.save(secure_filename(points.filename))
          return points
    
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
        
    with open(points, newline='') as csvfile:
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
   
    return jsonify({points : points, links : links})    
        
@app.route('/uploads/<filename>')
def uploaded_file(filename):
   return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

                        
if __name__ == "__main__":
    webbrowser.open('http://localhost:5000')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug = True)
            
            
       
