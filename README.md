# 📄 PDF2Image Web App

一个基于 **FastAPI + pdf2image** 的在线 PDF 转图片工具，支持 **批量上传、多页转换、手机端相册式预览、ZIP 一键下载**，并已部署上线，可直接使用。

👉 在线体验地址：  
**https://render-pdf2image.onrender.com**

---

## ✨ 功能特性

- 📤 **支持单个 / 多个 PDF 批量上传**
- 🖼 **PDF 每一页转换为 PNG 图片**
- 🔍 **支持配置缩放系数（控制清晰度）**
- 📱 **手机端友好界面**
  - 横向滑动预览（相册式）
  - 点击图片可全屏放大查看
- 📦 **一键下载 ZIP**
  - 按 PDF 分目录打包
- 🚀 **Blob 流传输**
  - 避免 base64，性能更好
- 🌐 **在线部署**
  - 无需本地环境，打开即用

---

## 📱 使用说明

### 1️⃣ 打开网页
访问：  
https://render-pdf2image.onrender.com

### 2️⃣ 上传 PDF
- 点击「选择 PDF」
- 可一次选择多个文件

### 3️⃣ 设置缩放系数
- 推荐值：`2.0`
- 数值越大，图片越清晰（同时文件也更大）

### 4️⃣ 转换并预览
- 点击「转换」
- 页面下方会显示每个 PDF 的图片结果
- 支持左右滑动浏览

### 5️⃣ 下载
- 点击「下载 ZIP」
- 获取全部转换后的图片压缩包

---

## 🧱 技术栈

### 后端
- **FastAPI**
- **uvicorn**
- **pdf2image**
- **poppler**

### 前端
- 原生 HTML / CSS / JavaScript
- JSZip（前端解压 ZIP 用于预览）
- 移动端优先布局（Mobile-first）

### 部署
- **Render**
- Web Service（免费实例）

---

## 📂 项目结构示例

```text
.
├── main.py                # FastAPI 后端
├── static/
│   ├── manifest.json      # PWA 配置
│   ├── sw.js              # Service Worker
│   ├── icon-192.png
│   └── icon-512.png
├── requirements.txt
└── README.md
