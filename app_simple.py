#!/usr/bin/env python3
"""
Subsurface - Music Sample Synchronization Web UI (Simplified Version)
A basic Flask web application for uploading music samples.
This version works without complex audio analysis libraries.
"""

import os
import json
import mimetypes
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'subsurface-sync-key-2023'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'ogg', 'aac'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_info(filepath):
    """Get basic file information without audio analysis."""
    try:
        stat = os.stat(filepath)
        filename = os.path.basename(filepath)
        
        return {
            'filename': filename,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'mime_type': mimetypes.guess_type(filepath)[0],
            'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown',
            # Mock audio properties for demonstration
            'tempo': 120.0,  # Default BPM
            'duration': 180.0,  # Mock 3 minutes
            'beat_count': 360,  # Mock beat count
            'sample_rate': 44100,  # Standard sample rate
            'spectral_centroid': 2000.0,  # Mock brightness
            'rms_energy': 0.1,  # Mock energy level
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None

@app.route('/')
def index():
    """Main page with file upload interface."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and basic file analysis."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get file information
        file_info = get_file_info(filepath)
        
        if file_info:
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': {
                    'tempo': file_info['tempo'],
                    'duration': file_info['duration'],
                    'beat_count': file_info['beat_count'],
                    'sample_rate': file_info['sample_rate'],
                    'spectral_centroid': file_info['spectral_centroid'],
                    'rms_energy': file_info['rms_energy']
                },
                'file_info': file_info
            })
        else:
            os.remove(filepath)  # Clean up failed file
            return jsonify({'success': False, 'error': 'Error processing file'})
    
    return jsonify({'success': False, 'error': 'Invalid file type. Please upload MP3, WAV, FLAC, M4A, OGG, or AAC files.'})

@app.route('/files')
def list_files():
    """List all uploaded files with their information."""
    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    
    for filename in os.listdir(upload_dir):
        if allowed_file(filename):
            filepath = os.path.join(upload_dir, filename)
            file_info = get_file_info(filepath)
            if file_info:
                files.append({
                    'filename': filename,
                    'analysis': {
                        'tempo': file_info['tempo'],
                        'duration': file_info['duration'],
                        'beat_count': file_info['beat_count'],
                        'sample_rate': file_info['sample_rate'],
                        'spectral_centroid': file_info['spectral_centroid'],
                        'rms_energy': file_info['rms_energy']
                    },
                    'file_info': file_info
                })
    
    return jsonify(files)

@app.route('/sync')
def sync_interface():
    """Sync interface for loaded samples."""
    return render_template('sync.html')

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files for playback."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/sync_samples', methods=['POST'])
def sync_samples():
    """Sync two audio samples based on tempo."""
    data = request.get_json()
    file1 = data.get('file1')
    file2 = data.get('file2')
    
    if not file1 or not file2:
        return jsonify({'success': False, 'error': 'Two files required for sync'})
    
    try:
        # Get file information for both files
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2)
        
        info1 = get_file_info(filepath1)
        info2 = get_file_info(filepath2)
        
        if not info1 or not info2:
            return jsonify({'success': False, 'error': 'Could not analyze one or both files'})
        
        # Calculate tempo difference and sync recommendation
        tempo_diff = abs(info1['tempo'] - info2['tempo'])
        sync_ratio = info1['tempo'] / info2['tempo'] if info2['tempo'] > 0 else 1.0
        
        # Create mock analysis results
        analysis1 = {
            'tempo': info1['tempo'],
            'duration': info1['duration'],
            'beat_count': info1['beat_count'],
            'sample_rate': info1['sample_rate'],
            'spectral_centroid': info1['spectral_centroid'],
            'rms_energy': info1['rms_energy']
        }
        
        analysis2 = {
            'tempo': info2['tempo'],
            'duration': info2['duration'],
            'beat_count': info2['beat_count'],
            'sample_rate': info2['sample_rate'],
            'spectral_centroid': info2['spectral_centroid'],
            'rms_energy': info2['rms_energy']
        }
        
        recommendation = f"Adjust {file2} speed by {sync_ratio:.2f}x to match {file1}"
        if tempo_diff < 5:
            recommendation = "Files are well matched - minimal adjustment needed"
        elif tempo_diff > 20:
            recommendation = f"Large tempo difference ({tempo_diff:.1f} BPM) - consider significant speed adjustment"
        
        return jsonify({
            'success': True,
            'file1_analysis': analysis1,
            'file2_analysis': analysis2,
            'tempo_difference': tempo_diff,
            'sync_ratio': sync_ratio,
            'recommendation': recommendation
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Subsurface is running'})

if __name__ == '__main__':
    print("Starting Subsurface Music Sample Sync UI...")
    print("Upload your music samples and sync them!")
    app.run(debug=True, host='0.0.0.0', port=5000)