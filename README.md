# Align

An Android mobile application that uses AI and computer vision to analyze and provide real-time feedback on weightlifting form — starting with the squat.

## Overview

Align helps gym-goers perform exercises safely and effectively by comparing their movement against an optimal biomechanical model. Using pose estimation, the app tracks joint angles in real time, classifies reps as good or bad, and gives users performance feedback over time.

## Features

- **Real-time pose tracking** via MediaPipe — detects joint positions and calculates angles during exercise
- **Rep detection** — automatically identifies the start and end of each repetition based on joint angle thresholds
- **ML-based form scoring** — supervised model classifies each rep snapshot as a success or failure, producing an overall accuracy score per set
- **Performance history** — graphical display of scores over time with per-rep breakdowns
- **User accounts** — login, registration, and credential management backed by a remote database
- **Exercise selection hub** — navigate between exercises, account settings, and performance history

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Kotlin + Jetpack Compose |
| Backend | FastAPI |
| Computer Vision | MediaPipe Pose |
| ML Model | Supervised classifier (angle snapshots → JSON weights) |
| Database | PostgreSQL via SQLAlchemy |
| CI/CD | GitLab Pipelines |
| Platform | Android |

## How It Works

1. User selects an exercise and enters the starting position
2. MediaPipe tracks body landmarks and calculates joint angles in real time
3. When the user breaks out of the start position, a rep begins recording
4. At each frame, a snapshot of angles is fed into the ML model
5. On rep completion the model returns a pass/fail; this repeats until recording ends
6. Overall score = percentage of successful snapshots across all reps
7. Results are saved to the database and displayed in the performance graph

## ML Model

- Input: tuple of joint angles at a given moment in the movement
- Output: binary classification (good form / bad form) per snapshot
- Weights stored in a JSON file
- Training data collected from labeled video recordings of correct and incorrect squat performances

## Contributors

| Name | Role |
|---|---|
| Justin Forbes | Backend, MediaPipe integration, camera features, DB connectivity, performance chart |
| Jordan Alonzo | Frontend UI (login, exercise selection, performance graph), DB schema |
| Radion Radion | ML model development, password systems, video hosting |
| Wilbert DeJesus | System architecture, account management, DevOps, ML fast-forwarding |

## Future Work

- Expand model to classify specific squat faults (not just good/bad) for targeted feedback
- Add support for bench press and deadlift
- Use user metadata (body proportions) to adjust model for different body types
- Improve overall UI/UX
- Incorporate user rep data into model retraining pipeline
