from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import List
import fitz  # PyMuPDF
import io
import zipfile

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#2563eb">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF → Image</title>

<style>
:root {
  --bg: #f5f6f8;
  --card: #ffffff;
  --primary: #2563eb;
  --border: #e5e7eb;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: #111;
}

/* ===== Header ===== */
header {
  padding: 16px;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

/* ===== Layout ===== */
.container {
  padding: 16px;
  max-width: 720px;
  margin: 0 auto;
}

/* ===== Card ===== */
.card {
  background: var(--card);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

/* ===== Controls ===== */
.controls label {
  font-size: 14px;
  color: #555;
  display: block;
  margin-bottom: 6px;
}

input[type="file"] {
  width: 100%;
}

.scale-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.scale-row input[type="range"] {
  flex: 1;
}

.scale-row input[type="number"] {
  width: 72px;
  padding: 6px;
}

/* ===== Buttons ===== */
.actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

button {
  flex: 1;
  height: 44px;
  border-radius: 10px;
  border: none;
  font-size: 16px;
}

.primary {
  background: var(--primary);
  color: #fff;
}

.secondary {
  background: #eef2ff;
  color: var(--primary);
}

button:disabled {
  opacity: 0.5;
}

/* ===== Result ===== */
.pdf-block {
  margin-bottom: 24px;
}

.pdf-title {
  font-weight: 600;
  margin-bottom: 8px;
}

/* ===== Gallery ===== */
.gallery {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.gallery img {
  height: 220px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: #fff;
  cursor: zoom-in;
}

/* ===== Viewer ===== */
#viewer {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  display: none;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

#viewer img {
  max-width: 100%;
  max-height: 100%;
}
</style>

<script src="https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js"></script>
</head>

<body>

<header>PDF → Image</header>

<div class="container">

  <!-- 控制区 -->
  <div class="card controls">
    <label>选择 PDF（可多选）</label>
    <input type="file" id="pdfs" accept="application/pdf" multiple>

    <label style="margin-top:14px;">缩放系数</label>
    <div class="scale-row">
      <input type="range" id="scale" min="0.25" max="4" step="0.25" value="1"
             oninput="scaleValue.value=this.value">
      <input type="number" id="scaleValue" value="1" step="0.25">
    </div>

    <div class="actions">
      <button class="primary" onclick="convert()">转换</button>
      <button class="secondary" onclick="downloadZip()" id="dl" disabled>
        下载 ZIP
      </button>
    </div>
  </div>

  <!-- 结果区 -->
  <div id="result"></div>
</div>

<!-- 全屏查看 -->
<div id="viewer" onclick="closeViewer()">
  <img id="viewerImg">
</div>

<script>
let zipBlob = null;

async function convert() {
  const files = document.getElementById("pdfs").files;
  if (!files.length) {
    alert("请选择 PDF");
    return;
  }

  const scale = document.getElementById("scaleValue").value;
  const fd = new FormData();
  for (const f of files) fd.append("files", f);
  fd.append("scale", scale);

  const res = await fetch("/pdf2image_batch_zip", {
    method: "POST",
    body: fd
  });

  zipBlob = await res.blob();
  document.getElementById("dl").disabled = false;

  const zip = await JSZip.loadAsync(zipBlob);
  const container = document.getElementById("result");
  container.innerHTML = "";

  const groups = {};
  for (const name in zip.files) {
    if (!name.endsWith(".png")) continue;
    const [pdf] = name.split("/");
    groups[pdf] = groups[pdf] || [];
    groups[pdf].push(zip.files[name]);
  }

  for (const pdf in groups) {
    const card = document.createElement("div");
    card.className = "card pdf-block";

    const title = document.createElement("div");
    title.className = "pdf-title";
    title.innerText = pdf;
    card.appendChild(title);

    const gallery = document.createElement("div");
    gallery.className = "gallery";

    for (const f of groups[pdf]) {
      const blob = await f.async("blob");
      const url = URL.createObjectURL(blob);
      const img = document.createElement("img");
      img.src = url;
      img.onclick = () => openViewer(url);
      gallery.appendChild(img);
    }

    card.appendChild(gallery);
    container.appendChild(card);
  }
}

function downloadZip() {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(zipBlob);
  a.download = "pdf_images.zip";
  a.click();
}

function openViewer(url) {
  document.getElementById("viewerImg").src = url;
  document.getElementById("viewer").style.display = "flex";
}

function closeViewer() {
  document.getElementById("viewer").style.display = "none";
}
</script>

<script>
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/sw.js");
}
</script>
</body>
</html>
"""


@app.post("/pdf2image_batch_zip")
async def pdf2image_batch_zip(
    files: List[UploadFile] = File(...),
    scale: float = Form(1.0)
):

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            pdf_bytes = await file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            trans = fitz.Matrix(scale, scale)

            base = file.filename.rsplit(".", 1)[0]
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=trans)
                zf.writestr(
                    f"{base}/page_{i+1}.png",
                    pix.tobytes("png")
                )

    mem.seek(0)
    return StreamingResponse(
        mem,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=pdf_images.zip"}
    )
