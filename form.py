import os
from flask import Flask, request, render_template, url_for, redirect,flash
from werkzeug.utils import secure_filename
from client import upload_file, download_file

# UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
app = Flask(__name__)

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
<<<<<<< HEAD
      if 'file' not in request.files or 'pem' not in request.files:
            flash('Missing files in request')
            return redirect("/upload")
      f = request.files['file']
      pem = request.files['pem']
      # if f.filename == '' or pem.filename == '':
      #       flash('One of files is missing')
      #       return redirect("/upload")
      # filename = secure_filename(f.filename)      
      # f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      # return 'file uploaded successfully'
      # f = request.files['file']
      return upload_file(str(f.filename), str(pem.filename))
=======
      if 'file' not in request.files:
            flash('No file attached in request')
            return redirect(request.url)
      f = request.files['file']
      uploaded_pem = request.files.get('pem')
      if f.filename == '' or uploaded_pem is None:
            flash('One of files is missing')
            return redirect(request.url)
      filename = secure_filename(f.filename)      
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return 'file uploaded successfully'
>>>>>>> 733eabd8dec010e66b4731975e013e19c50a537f

@app.route('/onDownload', methods = ['POST'])
def downloader():
      pass
      
if __name__ == '__main__':
    app.run(host='localhost', port=4000, debug=True)
