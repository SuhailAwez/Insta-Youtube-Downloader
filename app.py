from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# Function to get download link from Y2Mate
def get_youtube_download_link(video_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.y2mate.com/")

    # Find input box and submit video URL
    search_box = driver.find_element(By.NAME, "query")
    search_box.send_keys(video_url)
    search_box.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for the page to load

    # Extract download link
    try:
        download_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Download')]")
        download_url = download_button.get_attribute("href")
    except:
        download_url = None

    driver.quit()
    return download_url

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    video_url = request.form.get("video_url")
    
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400
    
    download_link = get_youtube_download_link(video_url)
    
    if not download_link:
        return jsonify({"error": "Failed to fetch download link"}), 500
    
    return jsonify({"download_link": download_link})

if __name__ == "__main__":
    app.run(debug=True)
