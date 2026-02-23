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

### 🖥️ Run Locally

## Setup Instructions 

1. Clone the repository 
2. Create virtual environment: python -m venv venv 
3. Activate: venv\Scripts\activate (Windows) 
4. Install dependencies: pip install -r requirements.txt 
5. Run locally: python main.py 

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

## 📂 Output Artifacts

- Extracted article details are printed in the console.
- Translated English titles are used for word frequency analysis.
- Downloaded images are stored inside the `/images` directory.

---

## 🏁 Conclusion

This project demonstrates end-to-end web automation including dynamic content extraction, cloud-based parallel execution, translation processing, and structured result analysis using Selenium and BrowserStack.