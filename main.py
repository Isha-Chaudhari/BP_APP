from flask import Flask, jsonify, request
import cv2
import numpy as np
import scipy.signal as sig
import cloudinary
import cloudinary.uploader
import requests
import logging

app = Flask(__name__)


def fetch_video_from_cloudinary(video_url):
    try:
        # Configure Cloudinary settings
        cloudinary.config(
            cloud_name="dggwc2zze",
            api_key="382656316639283",
            api_secret="jWnbVvXkRSxzgWFfdZbSshOt6kQ"
)
        public_id=video_url.split("/")[-1].split(".")[0]
        response = cloudinary.uploader.download(public_id)
        video_file = response["secure_url"]
        cap = cv2.VideoCapture(video_file)
        # Check if the video capture is successful
        if not cap.isOpened():
            raise Exception("Error opening video file")
        return cap
    
    except Exception as e:
        return {"error": str(e)}
    
def calculate_blood_pressure(ppg_data):
    try:
        fs = 100   # Sampling rate in Hz
        lowpass_fc = 8   # Low-pass filter cutoff frequency in Hz
        ppg_data = sig.detrend(ppg_data)
        b, a = sig.butter(4, lowpass_fc / (fs / 2), 'low')
        ppg_data = sig.filtfilt(b, a, ppg_data)
        systolic_peak_idx = np.argmax(ppg_data)
        diastolic_notch_idx = np.argmin(ppg_data[systolic_peak_idx:])
        diastolic_notch_idx += systolic_peak_idx
        time_delay = (diastolic_notch_idx - systolic_peak_idx) / fs
        arterial_distance = 0.7  # Distance in meters (sample value)
        pwv = arterial_distance / time_delay
        systolic_pressure = 9.6 * pwv + 120
        diastolic_pressure = 2.0 * pwv + 80
        return systolic_pressure, diastolic_pressure
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return jsonify({"error": "An error occurred during video processing"}), 500

@app.route("/process_video", methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON data"})
        video_url = data.get('video_url')

        if not video_url:
            return jsonify({"error": "No video URL provided"})

        cap = fetch_video_from_cloudinary(video_url)

        if cap is None:
            return jsonify({"error": "Failed to fetch the video from Cloudinary"})

        print_count = 0
        ppg_data = []

        while print_count < 500:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                mean_brightness = cv2.mean(gray)[0]
                ppg_data.append(mean_brightness)

                print_count += 1

        cap.release()
        systolic_pressure, diastolic_pressure = calculate_blood_pressure(ppg_data)

        if systolic_pressure is not None and diastolic_pressure is not None:
            response = {
                "Estimated systolic pressure": systolic_pressure,
                "Estimated diastolic pressure": diastolic_pressure
            }
            return jsonify(response)
        else:
            return jsonify({"error": "Blood pressure estimation failed"})
    except Exception as e:
        return jsonify({"error": "An error occurred during video processing"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
