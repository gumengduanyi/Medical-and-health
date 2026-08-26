import io

import qrcode
from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse, Response

from app.core.config import settings
from app.db.models import UploadAssetORM
from app.db.session import SessionLocal
from app.services.upload_service import save_image

router = APIRouter(prefix="/upload", tags=["upload"])
page_router = APIRouter(tags=["upload"])

UPLOAD_PAGE_HTML = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>健康助手 - 拍照上传</title><style>
body{margin:0;background:#f8fafc;color:#1e293b;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}.page{max-width:480px;margin:0 auto;padding:32px 20px}.title{font-size:24px;font-weight:700}.desc{margin:8px 0 28px;color:#64748b;font-size:14px;line-height:1.6}.actions{display:grid;grid-template-columns:1fr 1fr;gap:12px}button{height:52px;border:0;border-radius:6px;background:#0f766e;color:#fff;font-size:16px;font-weight:600}button.secondary{background:#2563eb}input{display:none}img{display:none;width:100%;margin-top:24px;border-radius:6px}.status{min-height:22px;margin-top:16px;text-align:center;font-size:14px}.success{color:#047857}.error{color:#b91c1c}a{display:none;margin-top:12px;color:#2563eb;text-align:center;font-size:14px}
</style></head><body><main class="page"><h1 class="title">拍照上传</h1><p class="desc">拍摄或选择健康报告、药盒等图片后上传。</p><div class="actions"><button id="camera">拍照</button><button class="secondary" id="album">从相册选择</button></div><input id="cameraFile" type="file" accept="image/*" capture="environment"><input id="albumFile" type="file" accept="image/*"><img id="preview" alt="图片预览"><div id="status" class="status"></div><a id="link" target="_blank">查看已上传图片</a></main><script>
const uploadUrl="{api_prefix}/upload/photo",status=document.getElementById("status"),preview=document.getElementById("preview"),link=document.getElementById("link");function upload(file){if(!file)return;preview.src=URL.createObjectURL(file);preview.style.display="block";link.style.display="none";status.className="status";status.textContent="正在上传...";const data=new FormData();data.append("file",file);fetch(uploadUrl,{method:"POST",body:data}).then(async response=>{const body=await response.json();if(!response.ok)throw new Error(body.detail||"上传失败");return body}).then(body=>{status.className="status success";status.textContent="上传成功";link.href=body.url;link.style.display="block"}).catch(error=>{status.className="status error";status.textContent=error.message})}document.getElementById("camera").onclick=()=>document.getElementById("cameraFile").click();document.getElementById("album").onclick=()=>document.getElementById("albumFile").click();document.getElementById("cameraFile").onchange=e=>upload(e.target.files[0]);document.getElementById("albumFile").onchange=e=>upload(e.target.files[0]);
</script></body></html>"""


@router.get("/qrcode")
def generate_qrcode(request: Request):
    base_url = settings.public_base_url or str(request.base_url)
    scan_url = f"{base_url.rstrip('/')}/upload/camera"
    image = qrcode.make(scan_url, image_factory=qrcode.image.pure.PyPNGImage)
    buffer = io.BytesIO()
    image.save(buffer)
    return Response(content=buffer.getvalue(), media_type="image/png", headers={"Cache-Control": "no-store"})


@page_router.get("/upload/camera", response_class=HTMLResponse)
def camera_page():
    return HTMLResponse(UPLOAD_PAGE_HTML.replace("{api_prefix}", settings.api_prefix))


@router.post("/photo")
async def upload_photo(file: UploadFile = File(...)):
    info = await save_image(file)
    with SessionLocal() as session:
        session.add(
            UploadAssetORM(
                id=info["filename"],
                filename=info["filename"],
                url=info["url"],
                size=info["size"],
                content_type=info["contentType"],
            )
        )
        session.commit()
    return info
