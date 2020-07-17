from flask import Flask, render_template, request, Response,redirect, url_for, flash
from datetime import date
import pandas as pd
import os
from scripts import YT_MP3
app = Flask(__name__)


from werkzeug.utils import secure_filename

UPLOAD_FOLDER = r'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
key = 'jUNrE-I|m,I9Wr~nG7KKd]8I%>zIuf{K*IlV<W<Y-m_Pd?U.w368S4YB+H*3cG8'
app.secret_key = key
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
    return render_template('home.html')


@app.route('/processcsv', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data =  YT_MP3.processfile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return '''
        <a href="%s.zip">Download</a>
        ''' % data

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
