import os
from flask import Flask, request, render_template, url_for, redirect,flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload")
def fileUpload():
    return render_template('upload.html')

@app.route("/download")
def fileDownload():
    return render_template('download.html')

@app.route('/onUpload', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      if 'file' not in request.files:
            flash('No file attached in request')
            return redirect("/upload")
      f = request.files['file']
      uploaded_pem = request.files.get('pem')
      if f.filename == '' or uploaded_pem is None:
            flash('One of files is missing')
            return redirect("/upload")
      filename = secure_filename(f.filename)      
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return 'file uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)
