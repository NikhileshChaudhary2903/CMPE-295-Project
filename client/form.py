import os
import sys
from pathlib import Path
from flask import Flask, request, render_template, url_for, redirect,flash
from werkzeug.utils import secure_filename
import client

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
app.config['PEM_UPLOAD_FOLDER'] = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)+ '/pem'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/upload")
def fileUpload():
    return render_template('upload.html')

@app.route("/download")
def fileDownload():
    return render_template('download.html')

@app.route('/onUpload', methods = ['POST'])
def uploader():
   if request.method == 'POST':
      if 'file' not in request.files:
            flash('Specify file to be uploaded')
            return redirect("/upload")
      
      if 'pem' not in request.files:
            flash('Specify pem file')
            return redirect("/upload")
      f = request.files['file']
      pem = request.files['pem']
      filename = secure_filename(f.filename)      
      pem_filename = secure_filename(pem.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      pem.save(os.path.join(app.config['PEM_UPLOAD_FOLDER'], pem_filename))
      return client.upload_file(str(f.filename), '../pem/' + str(pem.filename))

@app.route('/onDownload', methods = ['POST'])
def downloader():
      if request.method == 'POST':
            file_name = str(request.form.get('filename'))
            pem = request.files['pem']
            pem_filename = secure_filename(pem.filename)
            pem.save(os.path.join(app.config['PEM_UPLOAD_FOLDER'], pem_filename))
            return client.download_file(file_name, '../pem/' + str(pem.filename))
      
if __name__ == '__main__':
    app.run(host='localhost', port=4000, debug=True)
