import os
import tempfile
import shutil
import pyttsx3
from flask import Flask, render_template, request, jsonify, send_file
from PyPDF2 import PdfReader
import winsound
from gtts import gTTS

app = Flask(__name__)

# Initialize text-to-speech engine (pyttsx3 for offline)
engine = pyttsx3.init()

# Temporary directory for audio files
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'tts_app')
os.makedirs(TEMP_DIR, exist_ok=True)

# Supported languages for gTTS (extend this list as needed)
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-cn"
}

@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html', languages=SUPPORTED_LANGUAGES.keys())

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    """Convert text to speech and save it as an audio file using pyttsx3 or gTTS."""
    try:
        data = request.json
        text = data.get('text', '').strip()
        voice_type = data.get('voice', 'default')
        rate = data.get('rate', 150)
        language = data.get('language', 'en')

        if not text:
            return jsonify({'error': 'Text is required for conversion'}), 400

        # Check if we use pyttsx3 or gTTS for speech synthesis
        if language in SUPPORTED_LANGUAGES.values():
            # Use gTTS for online synthesis if language is supported
            tts = gTTS(text=text, lang=language, slow=False)
            audio_path = os.path.join(TEMP_DIR, 'output.mp3')
            tts.save(audio_path)
        else:
            # Use pyttsx3 for offline synthesis
            available_voices = engine.getProperty('voices')
            if voice_type == 'male':
                voice = next((v for v in available_voices if 'david' in v.name.lower()), None)
            elif voice_type == 'female':
                voice = next((v for v in available_voices if 'zira' in v.name.lower()), None)
            else:
                voice = available_voices[0]

            engine.setProperty('voice', voice.id)
            engine.setProperty('rate', rate)

            audio_path = os.path.join(TEMP_DIR, 'output.wav')
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

        # Return URL for the audio file
        audio_file_url = f"/audio/{os.path.basename(audio_path)}"
        return jsonify({'message': 'Conversion successful', 'audio_url': audio_file_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve the audio file."""
    audio_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(audio_path):
        mime_type = "audio/mp3" if filename.endswith(".mp3") else "audio/wav"
        return send_file(audio_path, mimetype=mime_type)
    return jsonify({'error': 'Audio file not found'}), 404

@app.route('/play', methods=['POST'])
def play_audio():
    """Play the generated audio file."""
    audio_file = os.path.join(TEMP_DIR, 'output.wav')
    if os.path.exists(audio_file):
        winsound.PlaySound(audio_file, winsound.SND_FILENAME)
        return jsonify({'message': 'Playing audio'}), 200
    return jsonify({'error': 'Audio file not found'}), 404

@app.route('/download', methods=['GET'])
def download_audio():
    """Download the generated audio file."""
    audio_file = os.path.join(TEMP_DIR, 'output.wav')
    if os.path.exists(audio_file):
        return send_file(audio_file, as_attachment=True, download_name='output.wav')
    return jsonify({'error': 'Audio file not found'}), 404

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Extract text from a PDF file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file format. Please upload a PDF'}), 400

    try:
        # Save and read the uploaded PDF
        pdf_path = os.path.join(TEMP_DIR, file.filename)
        file.save(pdf_path)

        pdf_text = extract_text_from_pdf(pdf_path)
        os.remove(pdf_path)  # Clean up the file after processing

        return jsonify({'text': pdf_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        return ''.join(page.extract_text() for page in reader.pages)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files."""
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            os.makedirs(TEMP_DIR, exist_ok=True)
        return jsonify({'message': 'Temporary files cleaned up'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
