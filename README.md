# Audio Repetition Counter

This application is a web-based tool that allows users to record audio and detect the number of repetitions within it. Currently the algorithm detects the number of distinct beats or words with gap between them (not exactly repetitions), but we do have plans to update it further. It's built using a combination of Flask (Python) for the backend and HTML, CSS, and JavaScript for the frontend. It's built with help from (Firebase Studio)[https://studio.firebase.google.com/] and (ChatGPT)[https://chatgpt.com]

## Technical Structure

The application is structured as follows:

**Frontend (Web Browser):**

*   **HTML (`src/index.html`):** Provides the user interface, including buttons to start and stop recording, and a display area for the repetition count.
*   **CSS (`src/style.css`):** Styles the user interface elements for a clean and user-friendly look.
*   **JavaScript (`src/index.html`):**
    *   Uses the browser's `MediaRecorder` API to capture audio from the user's microphone.
    *   Sends the recorded audio in chunks to the backend server.
    *   Handles UI updates, such as enabling/disabling buttons and displaying the repetition count.
    * Stores the chunks into a `Blob` object and sends them to the server.

**Backend (Flask Server):**

*   **Python (`main.py`):**
    *   Uses the Flask framework to handle HTTP requests.
    *   Receives audio chunks from the frontend.
    *   Uses the `librosa` library to load audio data, transcode files, and write them to disk.
    *   Saves the audio chunks to the filesystem.
    *   Implements the repetition detection logic, using `num_repetitions.py`.
    *   Returns the repetition count to the frontend.
    *   Defines endpoints for the UI to use:
        * `/`: Returns the frontend.
        * `/chunks`: handles the audio chunks.
        * `/upload`: Handles the end of the recording, with the last chunk.
        * `/create_folder`: creates a new folder for the recording.
    * It uses a `/temporary` folder for temporary files.
    * it uses a `/upload` folder for storing the chunks.
*   **`num_repetitions.py`:** Implements the algorithm for detecting repetitions within an audio file. It calculates the energy in each chunk, and uses this energy to count the repetitions.
*   **`requirements.txt`**: list of the python dependencies.

## How to Run

1.  **Clone the Repository:**

```bash
git clone <repository_url> cd <repository_directory>
```

2.  **Create a Virtual Environment:**

```bash
python3 -m venv venv
```

3.  **Activate the Virtual Environment:**
    *   On macOS/Linux:

```bash
source venv/bin/activate
```

4.  **Install Dependencies:**

```bash
pip install -r requirements.txt
```

5.  **Run the Flask Application:**

```bash
python main.py
```

6.  **Access the Web App:** Open your web browser and go to `http://127.0.0.1:8080/`.

## Caveats of the Current Implementation

* **Every word Detection:** The detection algorithm is relatively simple and might not be accurate in all cases. It works better with clear, distinct words.
* **Error Handling:** While some error handling is present, it could be more robust. For example, more specific error messages could be provided to the user.
* **Browser Support:** The `MediaRecorder` API has varying levels of support across different browsers and versions. While the current code works in Chrome, compatibility with other browsers should be tested.
* **Audio Transcoding**: The current implementation transcode every chunk into wav format.
* **Server-Side Processing:** All the audio processing is done on the server. For very long audio recordings, this could lead to performance bottlenecks.
* **No authentication**: Any user can use the app.

## Next Steps

*   **Detect the repeated group of words:**
    * Currently this implementation detects every signal that has a gap before that, not only repetitions. So this actual counts words if we speak any sentence. So, we need to update it to count only repetitions by detecting the repeated word or phrase.
    *   Explore more sophisticated audio analysis techniques (e.g., using machine learning) to improve the detection of repeeated phrase/chant and the accuracy of repetition count.
*   **Improve accuracy:**
    * Once we have detected repeated word or group of words, the algorithm should only count if that's repeated.
    * One idea here is to count the energy increases only if the previous energy is zero, not if its already positive.
*   **Refine Error Handling:**
    *   Add more detailed error messages and provide better feedback to the user.
* **Optimize Transcoding**:
    * Explore if it is possible to transcode the files only once.
*   **Client-Side Processing:**
    *   Consider moving some of the audio processing to the client-side (using JavaScript and WebAssembly) to reduce server load.
*   **Cross-Browser Testing:**
    *   Thoroughly test the application in different browsers (Firefox, Safari, Edge) to ensure consistent behavior.
*   **User Authentication:**
    *   Implement user accounts and login features to control access to the application.
    * Give the option to save the audio with a name, along with metadata like time taken and repetition count. This helps as user could check how much time it would take for a particular phrase/chant and a target count.
*   **UI Enhancements:**
    *   Improve the UI/UX, such as providing a progress bar during audio processing or better feedback to the user.
    * Show audio signal along with detected edges to enhance UX.
    * Show timer with time elapsed for a particular user session. 
    * User should be able to input a target number and the system would 'speak' when the target is reached (and maybe when half of the target is reached).
*   **Deployment:**
    *   Deploy the application to a production server so that it can be accessed publicly.
* **Database:**
    * Add a database to store the results.
