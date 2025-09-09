# Subsurface - Music Sample Synchronization Web UI

A Python web application for uploading and synchronizing music samples. Built with a clean, responsive interface for musicians and audio producers.

## Features

- **File Upload Interface**: Upload music samples in various formats (MP3, WAV, FLAC, M4A, OGG, AAC)
- **Audio Analysis**: Automatic tempo detection, duration calculation, and basic audio properties analysis
- **Sync Tools**: Compare two samples and get recommendations for tempo matching
- **Playback Controls**: Built-in audio players for preview and synchronized playback
- **Responsive Design**: Clean, mobile-friendly interface using Bootstrap

## Quick Start

### Option 1: Basic HTTP Server (Recommended for Demo)
```bash
python3 server.py
```
Then open http://localhost:8000 in your browser.

### Option 2: Full Flask Application (Requires Dependencies)
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python3 app.py
```
Then open http://localhost:5000 in your browser.

## Usage

1. **Upload Samples**: 
   - Navigate to the main page
   - Click "Choose File" and select your audio file
   - Click "Upload & Analyze" to process the file

2. **Sync Samples**:
   - Navigate to the "Sync" page
   - Select two uploaded samples from the dropdown menus
   - Click "Analyze Sync" to compare tempo and get sync recommendations
   - Use playback controls to preview and test synchronization

## File Structure

```
subsurface/
├── app.py              # Full Flask application with audio analysis
├── server.py           # Basic HTTP server for demo
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── index.html     # Main upload page
│   └── sync.html      # Sample synchronization page
├── static/            # CSS and static assets
│   └── style.css      # Application styling
└── uploads/           # Directory for uploaded files
```

## Technologies Used

- **Backend**: Python 3, Flask (optional), HTTP server
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Audio**: HTML5 Audio API for playback
- **Analysis**: librosa and pydub for advanced audio processing (in full version)

## Development

The application includes two versions:
- `server.py`: Lightweight HTTP server with mock audio analysis (no dependencies)
- `app.py`: Full Flask application with real audio analysis (requires librosa, pydub)

Start with the basic server for testing, then upgrade to the Flask version for production use with real audio analysis capabilities.