import os
from fastapi import UploadFile, HTTPException
from backend.DB.database import dbSession
from backend.DB.models import Video
import uuid
from sqlalchemy.exc import IntegrityError

def validate_content_type(file: UploadFile) -> bool:
    """
    :param file: file being uploaded
    :return: True if video False if not
    """
    valid_content = file.content_type and (file.content_type.startswith("video"))

    return False if not valid_content else True

def unique_name(file: UploadFile) -> str:
    """
    :param file: file being handled
    :return: Provides file a unique id for clean formatting
    """
    if not validate_content_type(file):
        raise HTTPException(status_code=400, detail="Invalid content type")

    extension_types = {".mp4", ".webm", ".3gp"}
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in extension_types:
        raise HTTPException(status_code=400, detail="Invalid video format")

    unique_filename = f"{uuid.uuid4()}{extension}"

    return unique_filename

async def limit_size(file: UploadFile):
    """"
    :param file:
    :return: error if the file is too big else returns nothing
    """
    contents = await file.read()

    if len(contents) > 100 * 1024 * 1024: #100MB
        raise HTTPException(status_code=400, detail="File too large")
    await file.seek(0)
#This helps for when we deploy and need to check sizes of our files

async def save_video(video: UploadFile, user_id: int, db: dbSession) -> Video:
    unique_filename = unique_name(video)

    await limit_size(video)

    save_path = os.path.join("video", unique_filename)
    os.makedirs(os.path.join("video"), exist_ok=True)
    #This is saving videos to disk, probably in future want it to be in cloud

    with open(save_path, "wb") as f:
        f.write(await video.read())
    try:

        video = Video(
            user_id=user_id,
            url=unique_filename,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Video could not be saved")

    return video

def delete_video(video_id: int, user_id: int, db: dbSession) -> None:
    """

    :param video_id: Video to be deleted ID
    :param user_id: Current user ID
    :param db: db session
    :return: None, Video is deleted.
    """
    if video_id < 1:
        raise HTTPException(status_code=400, detail="No such video exists in the database")

    video = db.query(Video).filter(Video.id == video_id, Video.user_id == user_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found in the DB")

    os.remove(os.path.join("video", video.url))
    db.delete(video)
    db.commit()