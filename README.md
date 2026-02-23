# El País Opinion Scraper – Selenium + BrowserStack

## 📌 Overview

This project automates the extraction of the first 5 articles from the **El País Opinion** section.

It performs:

- Article title extraction (Spanish)
- Content extraction
- Article image download
- Spanish → English title translation
- Word frequency analysis (English titles)
- Cross-browser parallel execution using BrowserStack

---

## 🚀 Tech Stack

- Python 3.9+
- Selenium
- BrowserStack SDK
- Requests
- Googletrans
- WebDriver Manager

---

## ⚙️ Features

✅ Runs locally  
✅ Runs on BrowserStack (parallel threads)  
✅ Automatic environment detection  
✅ Image downloading  
✅ Translation support  
✅ Word frequency analysis  
✅ Structured logging  

---

## 🖥️ Run Locally

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run script

```bash
python main.py
```

---

## ☁️ Run on BrowserStack

### 1️⃣ Set Environment Variables

**Windows (CMD):**
```bash
setx BROWSERSTACK_USERNAME "your_username"
setx BROWSERSTACK_ACCESS_KEY "your_access_key"
```

Restart terminal after setting.

---

### 2️⃣ Run with BrowserStack SDK

```bash
browserstack-sdk python main.py
```

This runs tests in parallel threads as configured in `browserstack.yml`.

---

## 📊 Output

The script will:

- Print article details
- Download images inside `/images`
- Print repeated meaningful words (>2 times)

---

## 🏗 Architecture

The driver is dynamically configured:

- If `BROWSERSTACK_HUB_URL` exists → runs on BrowserStack
- Otherwise → runs locally using ChromeDriver

This ensures flexibility and environment independence.

---

## 📂 Images

Downloaded images are stored in:

```
/images
```

---

## 👨‍💻 Author

Kashish Gupta  
Automation & Software Enthusiast