import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.DB import SessionLocal, User, ExerciseSession
from backend.DB.database import Base, engine, dbSession
from backend.auth.account_auth import create_user, login_user, HTTPcred, change_pass, change_username, RegisterRequest, PassChange, UsernameChange, CurrentUser
from backend.vision.calculations import pose_estimation, create_landmarker, proccess_frame, get_joint_pos, extract_frame_features
from backend.scores.scoring import RepCounter, score_session, save_session

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Align API",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/register")
async def register(cred: RegisterRequest, db: dbSession):
    return create_user(cred.username, cred.password, db)

@app.post("/login")
async def login(cred: HTTPcred, db: dbSession):
    return login_user(db, cred)

@app.post("/change-password")
async def change_password(cred: HTTPcred, new_pass: PassChange, db: dbSession):
    return change_pass(db, cred, new_pass)

@app.post("/change-username")
async def change_username_endpoint(cred: HTTPcred, new_name: UsernameChange, db: dbSession):
    return change_username(db, cred, new_name)

@app.get("/history/{user_id}")
def get_history(user: CurrentUser, db: dbSession):
    """returns the last five Exercise Sessions of the user starting from most recent session"""
    return db.query(ExerciseSession).filter(ExerciseSession.user_id == user.id).order_by(ExerciseSession.created_at.desc()).limit(5).all()


@app.websocket("/ws/workout")
async def stream_workout(websocket: WebSocket):
    await websocket.accept()

    username = websocket.query_params.get("username")
    if not username:
        await websocket.close(code=1008, reason="Missing username")
        return

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return

    queue = asyncio.Queue()
    time = 0
    frame_count = 0
    rep_counter = RepCounter()

    def on_pose_detected(result, output_image, timestamp):
        nonlocal frame_count
        print(f"Callback fired. Landmarks found: {bool(result.pose_landmarks)}")
        if result.pose_landmarks:
            frame_count += 1
            landmarks = result.pose_landmarks[0]
            joints = get_joint_pos(landmarks)
            features = extract_frame_features(joints)
            rep_counter.on_frame(features)
            display_joints = {k: v for k, v in joints.items()
                              if k not in ("l_elbow", "r_elbow", "l_wrist", "r_wrist")}
            queue.put_nowait({
                "joints": display_joints,
                "rep_count": rep_counter.rep_count,
                **{k: v for k, v in features.items() if k != "ml_angles"},
            })

    landmarker = create_landmarker(on_pose_detected)

    try:
        while True:
            data = await websocket.receive_json()

            # check for stop action
            if data.get("action") == "stop":
                scores = score_session(rep_counter)
                session_id = save_session(scores, user.id, total_frames=frame_count)
                rep_count = scores["rep_count"]
                good_reps = scores["good_reps"]
                final_score = round((good_reps / rep_count * 100) if rep_count > 0 else 0.0, 1)
                await websocket.send_json({
                    "summary": True,
                    "session_id": session_id,
                    "frames_analyzed": frame_count,
                    "final_score": final_score,
                    **scores,
                })
                break

            frame = proccess_frame(data["frame"])
            print(f"Frame received, shape: {frame.shape}")
            pose_estimation(landmarker, frame, time)
            time += 33  # ~30fps in milliseconds

            # wait briefly for the async callback to fire
            await asyncio.sleep(0.05)

            # send results back if ready, otherwise send empty ack
            if not queue.empty():
                while not queue.empty():
                    result = queue.get_nowait()
                    await websocket.send_json(result)
            else:
                await websocket.send_json({
                    "joints": {},
                    "l_knee_angle": 0.0,
                    "r_knee_angle": 0.0,
                    "rep_count": rep_counter.rep_count,
                })

    except WebSocketDisconnect:
        pass
    finally:
        landmarker.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)