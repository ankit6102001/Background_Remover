import os
from rembg import remove
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

if 'static' not in os.listdir('.'):
    os.mkdir('static')

if 'uploads' not in os.listdir('static/'):
    os.mkdir('static/uploads')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_background(input_path, output_path):
    input_img = Image.open(input_path)
    output_img = remove(input_img)
    output_img.save(output_path)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/remback', methods=['POST'])
def remback():
    try:
        files = request.files.getlist('file')
        
        # Check if files were uploaded
        if not files:
            flash('No files were uploaded.')
            return redirect(url_for('home'))
        
        org_img_names = []
        rembg_img_names = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                org_img_names.append(filename)
                
                rembg_img_name = filename.split('.')[0] + "_rembg.png"
                remove_background(UPLOAD_FOLDER + '/' + filename, UPLOAD_FOLDER + '/' + rembg_img_name)
                rembg_img_names.append(rembg_img_name)
            else:
                flash(f'Invalid file type: {file.filename}. Only PNG, JPG, JPEG, and WEBP files are allowed.')
        
        return render_template('home.html', org_img_names=org_img_names, rembg_img_names=rembg_img_names)
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
