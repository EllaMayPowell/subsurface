#!/usr/bin/env python3
"""
Subsurface - Music Sample Synchronization Web UI (Basic HTTP Version)
A simple HTTP server for demonstrating the upload interface.
"""

import os
import json
import urllib.parse
import mimetypes
import http.server
import socketserver
from pathlib import Path

class SubsurfaceHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_template('index.html')
        elif self.path == '/sync' or self.path == '/sync.html':
            self.serve_template('sync.html')
        elif self.path.startswith('/static/'):
            super().do_GET()
        elif self.path.startswith('/uploads/'):
            super().do_GET()
        elif self.path == '/files':
            self.serve_file_list()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/upload':
            self.handle_upload()
        elif self.path == '/sync_samples':
            self.handle_sync()
        else:
            self.send_error(404)
    
    def serve_template(self, template_name):
        """Serve HTML template"""
        try:
            template_path = Path(__file__).parent / 'templates' / template_name
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple template replacement for static files
            content = content.replace("{{ url_for('static', filename='style.css') }}", "/static/style.css")
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404)
    
    def serve_file_list(self):
        """Serve list of uploaded files as JSON"""
        uploads_dir = Path(__file__).parent / 'uploads'
        files = []
        
        if uploads_dir.exists():
            for filepath in uploads_dir.iterdir():
                if filepath.is_file() and self.is_audio_file(filepath.name):
                    stat = filepath.stat()
                    files.append({
                        'filename': filepath.name,
                        'analysis': {
                            'tempo': 120.0,
                            'duration': 180.0,
                            'beat_count': 360,
                            'sample_rate': 44100,
                            'spectral_centroid': 2000.0,
                            'rms_energy': 0.1
                        }
                    })
        
        response = json.dumps(files)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def handle_upload(self):
        """Handle file upload"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Simple response - in a real implementation, we'd parse the multipart data
        response = json.dumps({
            'success': True,
            'filename': 'demo-file.mp3',
            'analysis': {
                'tempo': 120.0,
                'duration': 180.0,
                'beat_count': 360,
                'sample_rate': 44100,
                'spectral_centroid': 2000.0,
                'rms_energy': 0.1
            }
        })
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def handle_sync(self):
        """Handle sync analysis request"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        response = json.dumps({
            'success': True,
            'file1_analysis': {
                'tempo': 120.0,
                'duration': 180.0,
                'beat_count': 360
            },
            'file2_analysis': {
                'tempo': 128.0,
                'duration': 200.0,
                'beat_count': 426
            },
            'tempo_difference': 8.0,
            'sync_ratio': 0.9375,
            'recommendation': 'Adjust sample 2 speed by 0.94x to match sample 1'
        })
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def is_audio_file(self, filename):
        """Check if file is an audio file"""
        return filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'))

def run_server(port=8000):
    """Run the development server"""
    with socketserver.TCPServer(("", port), SubsurfaceHandler) as httpd:
        print(f"Subsurface server running at http://localhost:{port}")
        print("Open your browser and navigate to the URL above")
        httpd.serve_forever()

if __name__ == '__main__':
    # Ensure uploads directory exists
    uploads_dir = Path(__file__).parent / 'uploads'
    uploads_dir.mkdir(exist_ok=True)
    
    run_server(8000)