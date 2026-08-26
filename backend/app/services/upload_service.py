import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/heic",
    "image/heif",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif"}
MAX_IMAGE_SIZE = 15 * 1024 * 1024
DETECTED_IMAGE_TYPES = {
    "jpeg": ({"image/jpeg"}, ".jpg"),
    "png": ({"image/png"}, ".png"),
    "gif": ({"image/gif"}, ".gif"),
    "webp": ({"image/webp"}, ".webp"),
    "heic": ({"image/heic", "image/heif"}, ".heic"),
}


def detect_image_type(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "webp"
    if len(content) >= 12 and content[4:8] == b"ftyp" and content[8:12] in {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"}:
        return "heic"
    return None


async def save_image(file: UploadFile) -> dict[str, str | int]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传的图片为空")
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="图片大小不能超过 15MB")

    detected_type = detect_image_type(content)
    if detected_type is None:
        raise HTTPException(status_code=400, detail="仅支持有效图片文件")

    detected_content_types, default_extension = DETECTED_IMAGE_TYPES[detected_type]
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="仅支持图片文件")
    if file.content_type in ALLOWED_CONTENT_TYPES and file.content_type not in detected_content_types:
        raise HTTPException(status_code=400, detail="图片类型与文件内容不匹配")
    detected_content_type = sorted(detected_content_types)[0]

    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS or extension not in {default_extension, ".jpeg" if default_extension == ".jpg" else default_extension}:
        extension = default_extension

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}{extension}"
    (upload_dir / filename).write_bytes(content)

    return {
        "filename": filename,
        "url": f"/uploads/{filename}",
        "size": len(content),
        "contentType": detected_content_type,
    }
