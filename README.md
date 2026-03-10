# 👁️ Gaze Detection & Analysis for Stress Management

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
  <img src="https://img.shields.io/badge/dlib-19.x-008000?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  <em>A real-time computer vision system that tracks eye movements and blink patterns to detect stress, drowsiness, and attention levels in workplace environments.</em>
</p>

---

## 📸 System Preview

> The system overlays real-time gaze and blink data on a live webcam feed, with a floating Tkinter HUD and pop-up alerts.

```
┌──────────────────────────────────────┐   ┌─────────────────────────────┐
│         LIVE WEBCAM FEED             │   │   📊 LIVE OVERLAY HUD        │
│                                      │   │─────────────────────────────│
│  Gaze Ratio: 1.12  → [center]        │   │  Blink Count:     47         │
│  Blink Count: 47                     │   │  Avg Blink Rate:  16.3 /min  │
│  EAR: 0.28                           │   └─────────────────────────────┘
│                                      │
│  [Face bounding box + landmarks]     │   ┌─────────────────────────────┐
│  [Eye region masks highlighted]      │   │   ⚠️ ALERT POP-UP (Sample)   │
└──────────────────────────────────────┘   │  "Focus! Get back to work"  │
                                           └─────────────────────────────┘
```

---


## 📋 Table of Contents

- [Abstract](#-abstract)

- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Key Metrics Explained](#-key-metrics-explained)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [Alert Thresholds](#-alert-thresholds)
- [Results](#-results)
- [Conclusion](#-conclusion)
- [Future Directions](#-future-directions)
- [Project Structure](#-project-structure)
- [References](#-references)

---

## 📝 Abstract

This project explores using **gaze detection** to understand stress levels in office employees. By analysing gaze patterns during work tasks, the system identifies stress indicators — such as abnormal blink rates, drowsiness, and inattention — and proactively suggests breaks via on-screen alerts.

Insights from this project have the potential to **enhance employee well-being and productivity** in office environments.

---

## ✨ Features

-  **Real-time gaze direction detection** — determines if the user is looking at the screen or away
-  **Blink rate monitoring** — tracks blinks per minute and flags abnormal patterns
-  **Drowsiness detection** — uses Eye Aspect Ratio (EAR) to detect fatigue
-  **Stress level estimation** — correlates blink rate and EAR to stress indicators
-  **Floating HUD overlay** — always-on-top Tkinter window showing live stats
-  **Smart pop-up alerts** — triggers break reminders for focus loss, fatigue, or stress
-  **MySQL logging** — persists blink data with timestamps for further analysis

---

## ⚙️ How It Works

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────────┐
│  Webcam Feed │────▶│  Face Detection   │────▶│  Landmark Extraction │
│  (OpenCV)    │     │  (dlib HOG model) │     │  (68-point predictor)│
└──────────────┘     └───────────────────┘     └──────────┬───────────┘
                                                           │
                              ┌────────────────────────────▼────────────────────────────┐
                              │                   EYE ANALYSIS MODULE                    │
                              │                                                          │
                              │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
                              │  │  Gaze Ratio  │  │ Blink Ratio  │  │     EAR      │  │
                              │  │  (L/R mask)  │  │ (lid dist.)  │  │  (fatigue)   │  │
                              │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
                              └─────────┼─────────────────┼─────────────────┼──────────┘
                                        │                  │                 │
                              ┌─────────▼─────────────────▼─────────────────▼──────────┐
                              │                  DECISION ENGINE                         │
                              │     Focus Alert │ Drowsiness Alert │ Stress Alert        │
                              └─────────┬───────────────────────────────────────────────┘
                                        │
                              ┌─────────▼──────────┐     ┌───────────────────┐
                              │   Tkinter HUD +     │────▶│  MySQL Database   │
                              │   Pop-up Alerts     │     │  (blink_data)     │
                              └─────────────────────┘     └───────────────────┘
```

---

##  Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.8+ |
| Computer Vision | OpenCV, imutils |
| Face / Landmark Detection | dlib (`shape_predictor_68_face_landmarks.dat`) |
| Face Recognition | face_recognition |
| Numerical Computing | NumPy |
| Data Visualization | Matplotlib |
| GUI / HUD | Tkinter |
| Database | MySQL (via `mysql-connector-python`) |

---

##  Key Metrics Explained

### 1.  Gaze Ratio
Determines if the user is looking **at the screen** or **away**.

```
           White pixels (left half of eye)
Gaze Ratio = ─────────────────────────────────
           White pixels (right half of eye)
```

- `0.95 < ratio < 1.25` → **Looking at screen (center)**
- `ratio ≥ 1.25` or `ratio ≤ 0.95` → **Looking away**
- If looking away for **> 90 consecutive frames** → Alert triggered

---

### 2.  Blink Ratio (EAR — Eye Aspect Ratio)

```
         ||p2 - p6|| + ||p3 - p5||
EAR  =  ───────────────────────────
                2 × ||p1 - p4||
```

where `p1...p6` are the 6 eye landmark points.

- `EAR < 0.20` → **Blink detected**
- `avg_EAR < 0.24` for **> 60 frames** → **Drowsiness alert**

---

### 3.  Average Blink Rate

Calculated over every 10 blinks:

```
                    6
Blink Rate  =  ────────────  × 60   (blinks/min)
               time_for_5_blinks
```

| Blink Rate | Interpretation |
|---|---|
| < 10 blinks/min | Eye fatigue / overfocus risk |
| 10–20 blinks/min | Normal |
| > 90 blinks/min | High stress — break recommended |

---

##  Installation

### Prerequisites

- Python 3.8+
- MySQL Server running locally
- Webcam

### 1. Clone the repository

```bash
git clone https://github.com/your-username/gaze-stress-detection.git
cd gaze-stress-detection
```

### 2. Install dependencies

```bash
pip install opencv-python imutils numpy dlib face_recognition matplotlib mysql-connector-python
```

> **Note:** Installing `dlib` may require CMake and a C++ compiler. On Windows:
> ```bash
> pip install cmake
> pip install dlib
> ```

### 3. Download the dlib shape predictor

Download [`shape_predictor_68_face_landmarks.dat`](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) and place it in the project root directory.

### 4. Set up MySQL

```sql
CREATE DATABASE stress_management;
```

Update credentials in `gaze_detection.py`:

```python
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",   # ← change this
    database="stress_management"
)
```

---

##  Usage

```bash
python gaze_detection.py
```

- Press **`Q`** to quit the application.
- The floating HUD will appear on top of all windows showing live stats.
- Alerts will pop up automatically when thresholds are exceeded.

---

##  Database Schema

```sql
CREATE TABLE blink_data (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    timestamp     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blink_count   INT,
    avg_blink_rate FLOAT
);
```

Data is inserted whenever an **abnormal blink rate** is detected (too high or too low), enabling historical analysis of stress episodes.

---

##  Alert Thresholds

| Condition | Threshold | Alert Message |
|---|---|---|
| Looking away | > 90 consecutive frames | *"Focus! Get back to work"* |
| Drowsiness | avg EAR < 0.24 for > 60 frames | *"You are sleepy, take a break!"* |
| High stress blink rate | avg blink rate > 90/min | *"Abnormal blink rate — stress too high"* |
| Eye fatigue risk | avg blink rate < 10/min | *"Danger of eye fatigue — take a break"* |

---

## 📁 Project Structure

```
gaze-stress-detection/
│
├── gaze_detection.py                    # Main application script
├── shape_predictor_68_face_landmarks.dat  # dlib landmark model (download separately)
├── README.md                            # This file
└── AP_Lab_Project_Report.docx           # Full project report
```

---

## 🔬 Background & Research Basis

Research suggests that stress and emotional states can be inferred from eye movements:

- **Pupil dilation** → higher cognitive load or emotional stress
- **Rapid/erratic eye movements** → agitation or discomfort
- **Reduced blink rate** → overfocus or fatigue
- **Elevated blink rate** → anxiety or high stress

This project operationalises these findings into a real-time monitoring system using accessible webcam hardware and open-source libraries.

---

## 📊 Results

The model successfully determines the user's gaze direction — **left**, **right**, or **centre** — based on the distribution of white and coloured areas within the eye regions. Real-time classification runs frame-by-frame with low latency, enabling timely alert delivery.

---

## 🏁 Conclusion

This project demonstrated that gaze detection and analysis using OpenCV, Dlib, and Python is a viable, non-intrusive approach to assessing workplace stress in real time.

### Key Findings

| # | Finding |
|---|---|
| 1 | **Gaze Detection Accuracy** — Pre-trained dlib models effectively captured eye movements and identified fixation points, producing reliable gaze analysis. |
| 2 | **Stress Indicators** — Prolonged fixations, avoidance behaviours, and specific gaze patterns were successfully correlated with stress indicators. |
| 3 | **Real-time Monitoring** — The system delivers immediate feedback, enabling prompt intervention for both employees and employers. |
| 4 | **OpenCV Integration** — OpenCV proved highly effective for image segmentation, feature extraction, and overall eye image manipulation. |
| 5 | **User-Friendly Design** — The system operates seamlessly with minimal user interaction, making it practical for daily workplace use. |

###  Challenges & Considerations

- **Model Limitations** — Performance may degrade under poor lighting conditions or for individuals with unique eye characteristics. A more diverse training dataset could improve robustness.
- **Ethical Considerations** — Employee awareness and explicit consent are essential before deploying gaze tracking in real workplace environments.
- **Interdisciplinary Collaboration** — Combining gaze analysis with input from mental health professionals would enable a more holistic stress management approach.

---

## Future Directions

1. **Machine Learning Enhancement** — Explore adaptive ML techniques that learn individual gaze pattern variations over time for personalised accuracy.
2. **Long-Term Stress Monitoring** — Extend the system to support longitudinal tracking, potentially integrating additional biometric indicators for a comprehensive stress profile.
3. **User Feedback Loop** — Continuously collect user feedback to improve UI, detection accuracy, and overall effectiveness of stress interventions.

---

## Project Structure

```
gaze-stress-detection/
│
├── gaze_detection.py                      # Main application script
├── shape_predictor_68_face_landmarks.dat  # dlib landmark model (download separately)
├── README.md                              # This file
└── AP_Lab_Project_Report.docx             # Full project report
```

---

##References

1. C. Jyotsna and J. Amudha, *"Eye Gaze as an Indicator for Stress Level Analysis in Students,"* 2018 International Conference on Advances in Computing, Communications, and Informatics (ICACCI), Bangalore, India, 2018, pp. 1588–1593. DOI: [10.1109/ICACCI.2018.8554715](https://doi.org/10.1109/ICACCI.2018.8554715)

2. Z. A. Haq and Z. Hasan, *"Eye-blink rate detection for fatigue determination,"* 2016 1st India International Conference on Information Processing (IICIP), Delhi, India, 2016, pp. 1–5. DOI: [10.1109/IICIP.2016.7975348](https://doi.org/10.1109/IICIP.2016.7975348)

3. Dlib C++ Library — http://dlib.net/python/index.html

4. OpenCV Documentation — https://docs.opencv.org/4.x/modules.html

---

<p align="center">Made with ❤️ for AP Lab 2023</p>
