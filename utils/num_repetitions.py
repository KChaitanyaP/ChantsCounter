import librosa
import librosa.display
import matplotlib.pyplot as plt
import logging
import numpy as np
import base64
from scipy import signal
from scipy import ndimage
import os
from io import BytesIO

# Configure logging
log_file = '../app.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def clean_signal(y_full):
    logging.info("cleaning signal")

    # Use RMS threshold
    rms = np.sqrt(np.mean(y_full**2))
    threshold = 0.5 * rms  # You can tune this factor (e.g., 0.3 - 0.7)
    return np.where(np.abs(y_full) < threshold, 0, y_full)

def detect_grouped_onsets(y_full, sr_full):
    # Detect onsets
    logging.info("detecting grouped onsets")
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
    
    return grouped_onsets

def filter_onsets_by_distance(y, sr, min_distance_sec=0.5):    
    logging.info("filtering onsets by distance")
    # Detect onsets 
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # Count number of repeating waveforms
    logging.info(f"Number of repeating waveforms: {len(onset_times)}")
    # Filter out onsets that are too close to each other
    # min_distance_sec = 0.5  # set your desired minimum distance (in seconds)

    filtered_onsets = []
    last_onset = -np.inf

    for onset in onset_times:
        if onset - last_onset >= min_distance_sec:
            filtered_onsets.append(onset)
            last_onset = onset

    logging.info(f"Filtered onset count: {np.ceil(len(filtered_onsets)/2)}")
    return filtered_onsets

def detect_rising_edge_onsets(y, sr):
    logging.info("detecting rising edge onsets")
    # Compute amplitude envelope
    hop_length = 512
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    # Smooth the envelope
    onset_env_smooth = ndimage.gaussian_filter1d(onset_env, sigma=1)

    # Compute derivative and keep only positive slope
    delta_env = np.diff(onset_env_smooth)
    delta_env = np.concatenate([[0], delta_env])  # pad to match length
    delta_env[delta_env < 0] = 0  # zero out falling slopes

    # Ensure dtype is float32 (peak_pick is sensitive to this)
    delta_env = delta_env.astype(np.float32)
    # Peak picking
    # toDO experiment with some parameter tuning, especially for the beginning of the signal
    onset_frames = librosa.util.peak_pick(
        delta_env,
        pre_max=3, post_max=3,
        pre_avg=3, post_avg=3,
        delta=0.2 * np.max(delta_env),
        wait=50
    )

    # Convert to time
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
    logging.info(f"Detected {len(onset_times)} rising-edge onsets.")
    return onset_times
    

def plot_audio_waves(full_audio_path):
    """
    Plots the audio waves of a full MP3 file and an optional single chant MP3 file in subplots.
    Reads only wav files now.
    Args:
        full_audio_path (str): Path to the full wav file.
        chant_audio_path (str, optional): Path to the single chant MP3 file. Defaults to None.

    
    """
    logging.info(f"Plotting audio waves for file {full_audio_path}")
    try:
        y_full, sr_full = librosa.load(full_audio_path)
    except Exception as e:
        logging.error(f"Error loading full audio file: {e}")
        return False

    fig, axs = plt.subplots(2, 1, figsize=(12, 14), sharex=True)
    if not (isinstance(axs, np.ndarray)):
        axs = [axs]


    # Plot full audio
    wave = librosa.display.waveshow(y_full, sr=sr_full, ax=axs[0])
    # grouped_onsets = detect_grouped_onsets(y_full, sr_full)
    # axs[0].vlines(grouped_onsets, ymin=-1, ymax=1, color='orange', linestyles='dashed', linewidth=1)
    axs[0].set(title='Actual Audio')

    wave_times = wave.times
    y_clean = clean_signal(y_full)
    axs[1].plot(wave_times, y_clean)
    axs[1].set(title='Waveform Samples cleaned')

    # filtered_onsets_by_dist = filter_onsets_by_distance(y_clean, sr_full)
    # axs[1].vlines(filtered_onsets_by_dist, -1, 1, color='orange', linestyle='--', label='Detected Repeats')

    rising_edge_onsets = detect_rising_edge_onsets(y_clean, sr_full)
    axs[1].vlines(rising_edge_onsets, -0.5, 0.5, color='magenta', linestyle='--', label='Detected Rising edge onsets')

    plt.tight_layout()
    plt.savefig("plot.png")
    logging.info('plot saved to plot.png')
    plt.close()

def count_repetitions_based_on_energy(wav_file_path):
    logging.info(f"counting repetitions based on energy for {wav_file_path}")
    try:
        y_full, sr_full = librosa.load(wav_file_path)
        logging.info(f"Loaded audio from {wav_file_path}")
    except Exception as e:
        logging.error(f"Error loading full audio file: {e}")
        return False
    
    y_clean = clean_signal(y_full)
    rising_edge_onsets = detect_rising_edge_onsets(y_clean, sr_full)
    logging.info(f"Counted {len(rising_edge_onsets)} repetitions.")
    return len(rising_edge_onsets)


def main():
    full_audio = "uploads/test1.wav"
    
    logging.info(f"Looking at full_audio: {full_audio}")
    # if not os.path.exists(full_audio):
    #     logging.error(f"Error: Full audio file not found at {full_audio}")     
    #     return
    
    plot_audio_waves(full_audio)
    count_reps = count_repetitions_based_on_energy(full_audio)
    # caveat: this looks at the profile of signal energy, but isn't looking at the actual signal
    #   like we can't use energy based method to identify or compare the phrase/chant
    # todo identify a single rep start time and end time, based on ML or further signal processing,
    #   then we can isolate a single occurence and use to identify/compare the phrase being repeated.
    # todo try and compare: count reps based on speach to text
    logging.info(f"count_reps: {count_reps}")

if __name__ == "__main__":
    main()
