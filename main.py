import logging
import os
import tempfile
import uuid

from flask import Flask, request, jsonify
from flask import render_template
from pydub import AudioSegment

from utils import plot_audio, num_repetitions

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temporary'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# Configure logging
log_file = 'app.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logging.info(f"Created folder: {UPLOAD_FOLDER}")

# Create temporary folder if it doesn't exist
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
    logging.info(f"Created folder: {TEMP_FOLDER}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/create_folder', methods=['POST'])
def create_folder_endpoint():
    """Creates a new unique folder and returns its ID."""
    folder_id = str(uuid.uuid4())
    folder_path = os.path.join(UPLOAD_FOLDER, folder_id)
    os.makedirs(folder_path, exist_ok=True)
    # chunks_folder_path = os.path.join(folder_path")
    # os.makedirs(chunks_folder_path, exist_ok=True)

    logging.info(f"Created folder: {folder_path}")
    # logging.info(f"Created chunks folder: {chunks_folder_path}")
    return jsonify({'folder_id': folder_id}), 200

@app.route('/chunks', methods=['POST'])
def upload_audio_chunk():
    """
    Handles the upload of audio chunks.
    """
    if 'audio' not in request.files or 'folder_id' not in request.form:
        logging.error("Missing audio file or folder_id")
        return jsonify({'error': 'Missing audio file or folder_id'}), 400
    
    audio_file = request.files['audio']
    folder_id = request.form['folder_id']
    chunk_start_time = request.form.get('chunkStartTime')
    chunk_end_time = request.form.get('chunkEndTime')
    file_name = f"{chunk_start_time}-{chunk_end_time}.wav"

    # Construct the full path for saving the chunk inside the chunks folder 
    chunks_folder_path = os.path.join(UPLOAD_FOLDER, folder_id)
    file_path = os.path.join(chunks_folder_path, file_name)
    
    logging.info(f"Received chunk: {file_name} for folder: {folder_id} at path: {file_path}")
    
    # Save audio file as wav, using librosa
    try:
        # Create a temporary file to save the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, dir=app.config['TEMP_FOLDER'], suffix=".webm") as temp_audio_file:
            audio_file.save(temp_audio_file.name)
            temp_audio_path = temp_audio_file.name
            logging.info(f"temp_audio_file.name: {temp_audio_file.name}")

        audio = AudioSegment.from_file(temp_audio_path, format="webm")
        audio.export(file_path, format="wav")

    except Exception as e:
        logging.error(f"Error saving or loading chunk: {e}")
        return jsonify({'error': f'Error saving or loading chunk: {e}'}), 500
    finally:
        # Clean up the temporary file
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    logging.info(f"Saved chunk: {file_path}")

    # Process the chunk and count repetitions
    try:
        repetitions = num_repetitions.count_repetitions_based_on_energy(file_path)
        logging.info(f"Processed chunk: {file_path}, Repetitions: {repetitions}")
        
    except Exception as e:
        logging.error(f"Error processing audio chunk for repetitions: {e}")
        repetitions = -1
    
    return jsonify({'message': 'Audio chunk received, saved and processed', "repetitions": repetitions}), 200

def main():
    logging.info("Starting the app")
    app.run(port=int(os.environ.get('PORT', 8080)))
    logging.info("Stopping the app")

if __name__ == "__main__":
    main()
