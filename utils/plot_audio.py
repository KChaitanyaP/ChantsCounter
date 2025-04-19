import base64
import os

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np


def plot_audio_waves(full_audio_path, chant_audio_path=None, frame_length=2048):
    """
    Plots the audio waves of a full MP3 file and an optional single chant MP3 file in subplots.

    Args:
        full_audio_path (str): Path to the full MP3 file.
        chant_audio_path (str, optional): Path to the single chant MP3 file. Defaults to None.
    
    """
    try:
        y_full, sr_full = librosa.load(full_audio_path)
    except Exception as e:
        print(f"Error loading full audio file: {e}")
        return False

    fig, axs = plt.subplots(3 if chant_audio_path and os.path.exists(chant_audio_path) else 2, 1, figsize=(12, 14), sharex=True)
    if not (isinstance(axs, np.ndarray)):
        axs = [axs]

    # Detect onsets
    onset_frames = librosa.onset.onset_detect(y=y_full, sr=sr_full)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr_full)

    # Group onsets (Improved Logic)
    group_threshold = 0.3  # seconds
    grouped_onsets = []
    current_group = []
    for time in onset_times:
        if not current_group:
            current_group.append(time)
        elif any(abs(time - t) <= group_threshold for t in current_group):
            current_group.append(time)
        else:
            grouped_onsets.append(np.mean(current_group))
            current_group = [time]
    if current_group:
        grouped_onsets.append(np.mean(current_group))

    # Plot full audio and grouped onsets
    wave = librosa.display.waveshow(y_full, sr=sr_full, ax=axs[0])
    axs[0].vlines(grouped_onsets, ymin=-1, ymax=1, color='orange', linestyles='dashed', linewidth=1)
    axs[0].set(title='Full Audio')

    wave_times = wave.times
    wave_samples = wave.samples
    axs[1].plot(wave_times,wave_samples)
    axs[1].set(title='Waveform Samples')

    

    if chant_audio_path and os.path.exists(chant_audio_path):
        try:
            y_chant, sr_chant = librosa.load(chant_audio_path)
        except Exception as e:
            print(f"Error loading chant audio file: {e}")
            y_chant = None        
        if y_chant is not None:
            librosa.display.waveshow(y_chant, sr=sr_chant, ax=axs[2])
            axs[2].set_title('Single Chant')

    else:
        axs[2].set_visible(False)


    plt.tight_layout()
    plt.savefig("plot.png")    
    plt.close()


def get_plot_as_base64():   
    """
    Reads the plot.png file and returns it as a base64 encoded string.

    Returns:
        str: The base64 encoded image data.
    """

    try:
        with open("../docs/plot.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"Error reading plot.png: {e}")
        return None

def main():
    full_audio = "uploads/test1.mp3"
    
    if not os.path.exists(full_audio):
        print(f"Error: Full audio file not found at {full_audio}")     
        return
    
    # Find the latest chant folder if it exists
    chant_folder = None
    if os.path.exists("../uploads"):
      subfolders = [f.path for f in os.scandir("../uploads") if f.is_dir()]
      chant_folders = [f for f in subfolders if os.path.exists(os.path.join(f, "chant", "chant.mp3"))]
      if chant_folders:
          chant_folders.sort(key=os.path.getmtime, reverse=True)
          chant_folder = os.path.join(chant_folders[0], "chant", "chant.mp3")
    plot_audio_waves(full_audio, chant_folder)
    base64_image = get_plot_as_base64()    

    if base64_image:      
        print("Image could be displayed")
    else: print("image could not be displayed")

if __name__ == "__main__":
    main()