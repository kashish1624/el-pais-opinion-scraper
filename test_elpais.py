import os
import re
import requests
from collections import Counter
from googletrans import Translator

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ==========================================================
# DRIVER SETUP
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


# ==========================================================
# TEST FUNCTION
# ==========================================================
def test_elpais_scraper():

    driver = create_driver()
    wait = WebDriverWait(driver, 30)
    translator = Translator()
    translated_titles = []

    os.makedirs("images", exist_ok=True)

    try:
        # STEP 1: Open Opinion Section
        print("[STEP 1] Opening Opinion Section...")
        driver.get("https://elpais.com/opinion/")

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

        print("[SUCCESS] Opinion page loaded")


        # STEP 2: Get first 5 article links safely
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article h2 a")))

        article_elements = driver.find_elements(By.CSS_SELECTOR, "article h2 a")

        links = []
        for a in article_elements:
            href = a.get_attribute("href")
            if href:
                links.append(href)

        links = links[:5]

        if len(links) < 5:
            print("[WARNING] Less than 5 articles found")

        print(f"[SUCCESS] Collected {len(links)} article links")


        # STEP 3: Process each article
        for index, link in enumerate(links[:5]):
            print(f"\n[ARTICLE {index+1}]")

            driver.get(link)

            # Wait for full page load
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

            try:
                title_element = wait.until(
                    EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                )

                # IMPORTANT: use innerText (better for Safari & Mobile)
                title = title_element.get_attribute("innerText").strip()

                if not title:
                    print("[WARNING] Title empty. Skipping article.")
                    continue

            except Exception:
                print("[WARNING] Could not load title. Skipping article.")
                continue

            print(f"[TITLE - ES] {title}")

            # Extract paragraphs
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "p")))
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            content = " ".join([p.text for p in paragraphs if p.text.strip()])
            print(f"[CONTENT PREVIEW] {content[:300]}")

            # Download Image
            try:
                image = driver.find_element(By.CSS_SELECTOR, "figure img")
                image_url = image.get_attribute("src")

                if image_url:
                    img_data = requests.get(image_url, timeout=10).content
                    image_name = re.sub(r'[^a-zA-Z0-9]', '_', title[:25])
                    with open(f"images/{image_name}.jpg", "wb") as f:
                        f.write(img_data)
                    print("[IMAGE] Downloaded")
            except Exception:
                print("[IMAGE] Not available")

            # Translate Title
            try:
                translated = translator.translate(title, src='es', dest='en')
                translated_text = translated.text.strip()
                translated_titles.append(translated_text)
                print(f"[TITLE - EN] {translated_text}")
            except Exception as e:
                print(f"[TRANSLATION ERROR] {e}")
                translated_titles.append(title)

        # STEP 4: Word Frequency Analysis
        print("\n[STEP 4] Word Frequency Analysis")

        stop_words = {"the", "is", "a", "an", "of", "and", "to", "in", "on", "for", "with"}
        all_words = []

        for t in translated_titles:
            words = re.findall(r'\b[a-zA-Z]+\b', t.lower())
            all_words.extend([w for w in words if w not in stop_words])

        word_count = Counter(all_words)
        repeated_words = {word: count for word, count in word_count.items() if count > 2}

        if repeated_words:
            for word, count in repeated_words.items():
                print(f"{word} -> {count} times")
        else:
            print("No words repeated more than 2 times.")

    finally:
        driver.quit()
        print("\nExecution Finished")