# vision

This folder handles everything related to looking at the camera feed and figuring out where a person's body is.

---

## calculations.py

The core of the pose estimation pipeline. Takes a raw camera frame and turns it into numbers you can actually use.

### Frame handling

**`proccess_frame(data)`**
The Android app sends camera frames as base64 strings (text). This decodes that back into an actual image that OpenCV can work with.

**`conv_frame(frame)`**
OpenCV uses BGR color order by default, but MediaPipe wants RGB. This just swaps the color channels.

### MediaPipe setup

**`create_landmarker(callback)`**
Sets up the MediaPipe pose detector in `LIVE_STREAM` mode. In this mode, you feed it frames and it fires a callback whenever it's done processing one — so it doesn't block the rest of the app while it thinks.

**`pose_estimation(landmarker, frame, timestamp)`**
Sends one frame to MediaPipe for async processing. The result comes back through the callback you gave `create_landmarker`.

### Pulling out joint positions

**`get_joint_pos(landmarks)`**
MediaPipe gives you 33 body landmarks. This function picks out the 12 you care about (shoulders, elbows, wrists, hips, knees, ankles) and returns them as named (x, y) coordinates between 0 and 1, where (0,0) is the top-left of the frame.

### Angle math

**`calc_angles(a, b, c)`**
Given three points, this calculates the angle at the middle point `b`. For example, to get the knee angle you'd pass in hip → knee → ankle. Uses arctan2 under the hood, returns degrees.

**`calc_hip_angle(joints)`**
Shoulder → hip → knee angle, averaged across both sides.

**`calc_spine_angle(joints)`**
How far forward you're leaning. 0° = perfectly upright, higher = more forward lean.

**`calc_knee_cave(joints)`**
Compares knee width to hip width. A ratio below 1.0 means your knees are caving inward (valgus), which is bad form.

### Bundled feature extraction

**`extract_frame_features(joints)`**
Runs all the above and packages everything into one dict per frame — knee angles, hip angle, spine angle, knee cave ratio, symmetry difference, and the ML angle list.

**`extract_ml_angles(joints)`**
Returns exactly 8 angles in the same order the ML model was trained on: left elbow, right elbow, left knee, right knee, left hip, right hip, left shoulder, right shoulder.

---

## upload.py

Handles video file uploads from users. Not currently wired up to any active routes but the logic is complete.

**`validate_content_type(file)`** — checks the file is actually a video (not a random file pretending to be one)

**`unique_name(file)`** — generates a random UUID filename so uploaded files never collide, and checks the extension is `.mp4`, `.webm`, or `.3gp`

**`limit_size(file)`** — rejects anything over 100MB

**`save_video(video, user_id, db)`** — validates, saves to disk in `video/`, and records the URL in the database

**`delete_video(video_id, user_id, db)`** — removes the file from disk and deletes the database record

---

## pose_landmarker.task

The actual MediaPipe model binary (~9.4MB). This is what does the heavy lifting of detecting body landmarks in each frame. Must be present in this folder for the backend to start.
