from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.DB.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(225), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ExerciseSession", back_populates="user")
    videos = relationship("Video", back_populates="user")


class ExerciseSession(Base):  # add weight youre squating(?)
    __tablename__ = "exercise_sessions"


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_type = Column(String(10), nullable=False)  # "squat" ex.
    final_score = Column(Float)
    rep_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    squat_metrics = relationship("SquatMetrics", back_populates="session", uselist=False)


class SquatMetrics(Base):
    __tablename__ = "squat_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exercise_sessions.id"), nullable=False)

    good_reps = Column(Integer)
    bad_reps = Column(Integer)
    total_frames = Column(Integer)

    session = relationship("ExerciseSession", back_populates="squat_metrics")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="videos")

    # Not sure if this will be useful~
    # Could have videos be associated with a certain exercise based on what its uploaded for.
    # Assuming that in order to upload a video you select an exercise
    # exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

class CorrectVideos(Base):
    """
    This is basically for the example videos that the user will see
    At most this will be a db of three videos for each exercise
    """
    __tablename__ = "correct_videos"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    exercise_type = Column(String(25), nullable=False)