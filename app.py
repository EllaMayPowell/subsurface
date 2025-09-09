#!/usr/bin/env python3
"""
Subsurface - Music Sample Synchronization Web UI
A Flask web application for uploading and synchronizing music samples.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
import librosa
import numpy as np
from pydub import AudioSegment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'subsurface-sync-key-2023'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_audio(filepath):
    """Analyze audio file and extract tempo, duration, and other properties."""
    try:
        # Load audio file
        y, sr = librosa.load(filepath)
        
        # Get tempo
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        
        # Get duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Get spectral centroid (brightness)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_centroid_mean = np.mean(spectral_centroids)
        
        # Get RMS energy
        rms = librosa.feature.rms(y=y)[0]
        rms_mean = np.mean(rms)
        
        return {
            'tempo': float(tempo),
            'duration': float(duration),
            'spectral_centroid': float(spectral_centroid_mean),
            'rms_energy': float(rms_mean),
            'beat_count': len(beat_frames),
            'sample_rate': int(sr)
        }
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        return None

@app.route('/')
def index():
    """Main page with file upload interface."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and audio analysis."""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the uploaded audio
        analysis = analyze_audio(filepath)
        
        if analysis:
            flash(f'File uploaded successfully: {filename}')
            return jsonify({
                'success': True,
                'filename': filename,
                'analysis': analysis
            })
        else:
            flash('Error analyzing audio file')
            os.remove(filepath)  # Clean up failed file
            return jsonify({'success': False, 'error': 'Audio analysis failed'})
    
    flash('Invalid file type. Please upload MP3, WAV, FLAC, M4A, or OGG files.')
    return jsonify({'success': False, 'error': 'Invalid file type'})

@app.route('/files')
def list_files():
    """List all uploaded files with their analysis data."""
    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    
    for filename in os.listdir(upload_dir):
        if allowed_file(filename):
            filepath = os.path.join(upload_dir, filename)
            analysis = analyze_audio(filepath)
            if analysis:
                files.append({
                    'filename': filename,
                    'analysis': analysis
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
        # Analyze both files
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2)
        
        analysis1 = analyze_audio(filepath1)
        analysis2 = analyze_audio(filepath2)
        
        if not analysis1 or not analysis2:
            return jsonify({'success': False, 'error': 'Could not analyze one or both files'})
        
        # Calculate tempo difference and sync recommendation
        tempo_diff = abs(analysis1['tempo'] - analysis2['tempo'])
        sync_ratio = analysis1['tempo'] / analysis2['tempo']
        
        return jsonify({
            'success': True,
            'file1_analysis': analysis1,
            'file2_analysis': analysis2,
            'tempo_difference': tempo_diff,
            'sync_ratio': sync_ratio,
            'recommendation': f"Adjust {file2} speed by {sync_ratio:.2f}x to match {file1}"
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)