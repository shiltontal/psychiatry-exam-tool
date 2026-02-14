from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import config

bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_status():
    """Check which files are uploaded."""
    return {
        'synopsis': os.path.exists(config.SYNOPSIS_PATH),
        'dulcan': os.path.exists(config.DULCAN_PATH),
        'synopsis_path': config.SYNOPSIS_PATH,
        'dulcan_path': config.DULCAN_PATH,
    }

@bp.route('/uploads')
def uploads_page():
    status = get_upload_status()
    return render_template('uploads.html', status=status)

@bp.route('/uploads/upload', methods=['POST'])
def upload_file():
    file_type = request.form.get('file_type')

    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('uploads.uploads_page'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('uploads.uploads_page'))

    if file and allowed_file(file.filename):
        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)

        if file_type == 'synopsis':
            filepath = config.SYNOPSIS_PATH
            filename = 'Synopsis 2021.pdf'
        elif file_type == 'dulcan':
            filepath = config.DULCAN_PATH
            filename = 'Dulcan.pdf'
        else:
            flash('Invalid file type', 'error')
            return redirect(url_for('uploads.uploads_page'))

        file.save(filepath)
        flash(f'{filename} uploaded successfully!', 'success')
    else:
        flash('Invalid file format. Please upload PDF or DOC files.', 'error')

    return redirect(url_for('uploads.uploads_page'))

@bp.route('/uploads/delete/<file_type>', methods=['POST'])
def delete_file(file_type):
    if file_type == 'synopsis':
        filepath = config.SYNOPSIS_PATH
    elif file_type == 'dulcan':
        filepath = config.DULCAN_PATH
    else:
        flash('Invalid file type', 'error')
        return redirect(url_for('uploads.uploads_page'))

    if os.path.exists(filepath):
        os.remove(filepath)
        flash('File deleted successfully', 'success')

    return redirect(url_for('uploads.uploads_page'))
