# 🧠 AI-Powered Mind Map Generator  

This project converts **text, images, PDFs, and videos** into **interactive, zoomable mind maps**.  
It combines **OCR, NLP, and data visualization** to help users organize complex information into structured visual knowledge.  

---

## 🚀 Features  
- 📄 **Text to Mind Map** – Enter structured text and instantly generate a mind map  
- 🖼️ **Image/PDF OCR** – Extracts text using **Tesseract OCR + OpenCV**  
- 🎥 **Video Support** – Process YouTube links or uploaded videos (audio → text → mind map)  
- ✨ **AI-Powered Summarization** – Uses **OpenAI API** for transcription and summarization  
- 🌐 **Interactive Frontend** – Built with **D3.js** for zoomable, collapsible, and fullscreen mind maps  
- 💾 **Export Option** – Save mind maps as images for sharing  

---

## 🛠️ Tech Stack  
- **Backend:** Python (Flask), OpenCV, Tesseract OCR, Pytube  
- **AI/NLP:** OpenAI API (via OpenRouter)  
- **Frontend:** HTML, CSS, JavaScript (D3.js, DOM-to-Image)  
- **Other:** Configurable APIs, YouTube Data API  

---

## ⚙️ Setup Instructions  
## Install Python Dependencies
```
pip install flask openai pytube werkzeug pytesseract opencv-python pillow numpy
```
## Install Tesseract OCR
```
brew install tesseract
```
## Configure API Keys
```
const CONFIG = {
    OPENAI_API_KEY: "your-openai-api-key",
    YOUTUBE_API_KEY: "your-youtube-api-key",
    API_ENDPOINT: "http://localhost:5000"
};
```
## Run the file
```
python app.py
```
