from pathlib import Path
from uuid import uuid4
from io import BytesIO
from PIL import Image

POST_FOLDER = Path("media/post_covers")
POST_FOLDER.mkdir(parents=True, exist_ok=True)

def process_post_image(content: bytes) -> str:
    image = Image.open(BytesIO(content))
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGB")
    image.thumbnail((1200, 800))
    filename = f"{uuid4().hex}.jpg"
    image.save(
        POST_FOLDER / filename,
        format="JPEG",
        quality=90,
        optimize=True,
    )
    return filename

def delete_post_image(filename: str):
    if not filename:
        return
    if filename == "default_cover.jpg":
        return
    file_path = POST_FOLDER / filename
    if file_path.exists():
        file_path.unlink()