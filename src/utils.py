import constants
from logger import logging

import os
import time
import re
import shutil
from urllib.parse import urlparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import Set
from pytube import YouTube


def create_directory(directory, overwrite=False):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif overwrite:
            logging.info(f"Directory '{directory}' already exists. Overwriting..")
            shutil.rmtree(
                directory
            )  # Delete the directory and its contents recursively
            os.makedirs(directory)
        else:
            logging.info(f"Directory '{directory}' already exists.")
    except Exception as e:
        logging.exception(f"Error creating directory: {e}")
        return False
    return True


def is_youtube_link(url):
    youtube_pattern = (
        r"(http(s)?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|v\/)|youtu\.be\/)"
    )
    match = re.search(youtube_pattern, url)
    return bool(match)


def collect_youtube_metadata(url):
    channel_name, title = None, None
    try:
        yt = YouTube(url)
        if yt:
            channel_name = yt.author
            title = yt.title
    except Exception as e:
        logging.exception(e)
    return channel_name, title


def collect_website_metadata(url):
    website_name = None
    try:
        website_name = urlparse(url).netloc
    except Exception as e:
        logging.exception(e)
    return website_name


def collect_youtube_content(url, dir_path):
    if not dir_path:
        return
    try:
        create_directory(dir_path, overwrite=True)
        video_id = re.search(r"(?<=v=)[^&#]+", url).group(0)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        with open(os.path.join(dir_path, constants.CONTENT_FILE), "w") as file:
            for segment in transcript:
                file.write(f"{segment['text']}\n")
    except Exception as e:
        logging.exception(e)


def collect_website_content(url, dir_path):
    if not dir_path:
        return
    try:
        create_directory(dir_path, overwrite=True)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text()
            # Remove empty lines
            text_content = "\n".join(
                line for line in text_content.splitlines() if line.strip()
            )
            with open(os.path.join(dir_path, constants.CONTENT_FILE), "w") as file:
                file.write(text_content)
        else:
            logging.error(
                f"Failed to fetch website content. Status code: {response.status_code}"
            )
    except Exception as e:
        logging.exception(e)


def collect_youtube_images(url, dir_path):
    images_path = None
    try:
        images_path = os.path.join(dir_path, "images")
        create_directory(images_path, overwrite=True)

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.set_window_size(1920, 1080)
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        time.sleep(2)
        duration = driver.execute_script(
            "return document.getElementsByTagName('video')[0].duration"
        )
        driver.find_element(By.CSS_SELECTOR, ".ytp-large-play-button").click()
        WebDriverWait(driver, 20).until(
            lambda _: driver.execute_script(
                "return document.getElementsByTagName('video')[0].currentTime > 0"
            )
        )
        current_time = (
            60 if duration > 60 else 0
        )  # skip first 60 seconds of typical YouTube jabber
        time_interval = 10
        while current_time < duration:
            image_path = os.path.join(images_path, f"image_{current_time}.png")
            driver.save_screenshot(image_path)
            current_time += time_interval
            driver.execute_script(
                f"document.getElementsByTagName('video')[0].currentTime = {current_time};"
            )
            time.sleep(2)
        driver.quit()
    except Exception as e:
        logging.exception(e)
    return images_path


def collect_website_images(images, dir_path):
    images_path = None
    try:
        images_path = os.path.join(dir_path, "images")
        create_directory(images_path, overwrite=True)

        for i, image in enumerate(images):
            with open(os.path.join(images_path, f"image_{i}.png"), "wb") as file:
                file.write(image.getbuffer())
    except Exception as e:
        logging.exception(e)

    return images_path


def get_overview_df(result):
    data = []
    if result:
        data.append(["Website", result.website_name])
        data.append(["Link", result.url])
        data.append(["Title", result.title])
        data.append(["Author", result.author])
        data.append(["Summary", result.summary])
    df = pd.DataFrame(data, index=None)
    return df


def get_benchmarks_df(benchmarks):
    unique_products: Set[str] = set()
    for benchmark in benchmarks:
        if benchmark.is_benchmark:
            for product in benchmark.products:
                unique_products.add(product.name)

    columns = ["Benchmark", "Type", "Metric"] + [
        product_name for product_name in unique_products
    ]
    data = []
    for benchmark in benchmarks:
        if benchmark.is_benchmark:
            row = [
                benchmark.name,
                benchmark.type,
                benchmark.metric,
            ]
            for product_name in unique_products:
                score = None
                for product in benchmark.products:
                    if product_name == product.name:
                        score = str(product.score)
                        break
                row.append(score)
            data.append(row)

    df = pd.DataFrame(data=data, columns=columns)

    # Handle anomalies
    df = df.drop_duplicates()

    return df
