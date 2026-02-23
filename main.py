import os
import re
import time
import requests
import threading
from collections import Counter
from googletrans import Translator

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ==========================================================
# DRIVER SETUP (Supports Local + BrowserStack Automatically)
# ==========================================================
def create_driver():
    if os.getenv("BROWSERSTACK_HUB_URL"):
        print("[INFO] Running on BrowserStack Cloud")
        return webdriver.Remote(
            command_executor=os.getenv("BROWSERSTACK_HUB_URL"),
            options=webdriver.ChromeOptions()
        )
    else:
        print("[INFO] Running Locally")
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )


driver = create_driver()
wait = WebDriverWait(driver, 15)

print(f"\nThread ID: {threading.get_ident()}")

translator = Translator()
translated_titles = []

os.makedirs("images", exist_ok=True)


try:
    # ==========================================================
    # STEP 1: Open Opinion Section
    # ==========================================================
    print("[STEP 1] Opening El País Opinion Section...")
    driver.get("https://elpais.com/opinion/")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    print("[SUCCESS] Opinion section loaded.")


    # ==========================================================
    # STEP 2: Fetch First 5 Articles
    # ==========================================================
    print("[STEP 2] Fetching first 5 article links...")

    articles = driver.find_elements(By.CSS_SELECTOR, "article h2 a")[:5]
    links = []

    for article in articles:
        link = article.get_attribute("href")
        if link:
            links.append(link)

    print(f"[INFO] Found {len(links)} articles.")


    # ==========================================================
    # STEP 3: Process Each Article
    # ==========================================================
    for index, link in enumerate(links):
        print(f"\n[ARTICLE {index+1}] Processing...")

        try:
            driver.get(link)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

            title = driver.find_element(By.TAG_NAME, "h1").text.strip()

            paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.a_c p")
            content = " ".join([p.text for p in paragraphs])

            print(f"[TITLE - ES] {title}")
            print(f"[CONTENT PREVIEW] {content[:500]}")

            # -------------------------
            # Download Image
            # -------------------------
            try:
                image = driver.find_element(By.CSS_SELECTOR, "figure img")
                image_url = image.get_attribute("src")

                if image_url:
                    img_data = requests.get(image_url, timeout=10).content
                    image_name = re.sub(r'[^a-zA-Z0-9]', '_', title[:25])

                    with open(f"images/{image_name}.jpg", "wb") as f:
                        f.write(img_data)

                    print("[IMAGE] Downloaded successfully.")
                else:
                    print("[IMAGE] No valid image URL found.")

            except Exception:
                print("[IMAGE] No image found for this article.")

            # -------------------------
            # Translate Title
            # -------------------------
            try:
                translated = translator.translate(title, src='es', dest='en')
                translated_text = translated.text.strip()
                translated_titles.append(translated_text)
                print(f"[TITLE - EN] {translated_text}")

            except Exception as e:
                print(f"[TRANSLATION ERROR] {e}")

        except Exception as e:
            print(f"[ERROR] Failed processing article {index+1}: {e}")


    # ==========================================================
    # STEP 4: Word Frequency Analysis
    # ==========================================================
    print("\n[STEP 4] Word Frequency Analysis (> 2 occurrences)\n")

    stop_words = {
        "the", "is", "a", "an", "of",
        "and", "to", "in", "on",
        "for", "with"
    }

    all_words = []

    for t in translated_titles:
        words = re.findall(r'\b[a-zA-Z]+\b', t.lower())
        filtered = [w for w in words if w not in stop_words]
        all_words.extend(filtered)

    word_count = Counter(all_words)

    found = False
    for word, count in word_count.items():
        if count > 2:
            print(f"{word} -> {count} times")
            found = True

    if not found:
        print("No meaningful words repeated more than 2 times.")


except Exception as main_error:
    print(f"[FATAL ERROR] {main_error}")

finally:
    driver.quit()
    print("\nExecution Completed Successfully")