# test_elpais.py

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


def test_elpais_scraper():

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)
    translator = Translator()
    translated_titles = []

    os.makedirs("images", exist_ok=True)

    try:
        # STEP 1: Open Opinion Section
        print("\n[STEP 1] Opening Opinion Section...")
        driver.get("https://elpais.com/opinion/")

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

        print("[SUCCESS] Opinion page loaded")

        # STEP 2: Get article links
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article h2 a")))
        article_elements = driver.find_elements(By.CSS_SELECTOR, "article h2 a")

        links = [a.get_attribute("href") for a in article_elements if a.get_attribute("href")]

        # More stable assertion (important for mobile layouts)
        assert len(links) >= 1, "No articles found on Opinion page!"

        links = links[:5]  # Safely take up to 5
        print(f"[SUCCESS] Processing {len(links)} articles")

        # STEP 3: Process each article
        for index, link in enumerate(links):
            print(f"\n[ARTICLE {index + 1}]")

            try:
                driver.get(link)
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

                title_element = wait.until(
                    EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                )

                title = title_element.text.strip()
                print(f"[TITLE - ES] {title}")

                # Extract content
                content = driver.execute_script("""
                    return Array.from(document.querySelectorAll('p'))
                        .map(p => p.innerText)
                        .filter(text => text.trim() !== '')
                        .join(' ');
                """)

                print(f"[CONTENT PREVIEW] {content[:300]}")

                # Download image
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

                # Translate title
                try:
                    translated = translator.translate(title, src='es', dest='en')
                    translated_text = translated.text.strip()
                    translated_titles.append(translated_text)
                    print(f"[TITLE - EN] {translated_text}")
                except Exception as e:
                    print(f"[TRANSLATION ERROR] {e}")
                    translated_titles.append(title)

            except Exception as e:
                print(f"[WARNING] Error processing article: {e}")
                continue

        # STEP 4: Word Frequency
        print("\n[STEP 4] Word Frequency Analysis")

        stop_words = {"the", "is", "a", "an", "of", "and", "to", "in", "on", "for", "with"}
        all_words = []

        for t in translated_titles:
            words = re.findall(r'\b[a-zA-Z]+\b', t.lower())
            filtered_words = [w for w in words if w not in stop_words]
            all_words.extend(filtered_words)

        word_count = Counter(all_words)

        print("\nFull Word Count:")
        for word, count in word_count.items():
            print(f"{word} -> {count}")

        repeated_words = {word: count for word, count in word_count.items() if count > 2}

        print("\nRepeated Words (>2 times):")
        if repeated_words:
            for word, count in repeated_words.items():
                print(f"{word} -> {count} times")
        else:
            print("No words repeated more than 2 times.")

        print("\n=== FINAL SUMMARY ===")
        for t in translated_titles:
            print(t)

        # Stable final assertion
        assert len(translated_titles) >= 1, "No titles were processed successfully!"

    finally:
        driver.quit()
        print("\nExecution Finished")