from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "https://frontend-4zgb.onrender.com"}})

@app.route('/fastdl-download', methods=['POST'])
def fastdl_download():
    url = request.json.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Initialize Selenium WebDriver (example with Chrome)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    try:
        # Visit the FastDL page
        driver.get('https://fastdl.app/en')

        # Wait for the page to load (adjust this to wait for a specific element to appear)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="url"]'))
        )

        # Find the input field for the URL (adjust selector as necessary)
        input_element = driver.find_element(By.CSS_SELECTOR, 'input[name="url"]')
        input_element.send_keys(url)

        # Submit the form (adjust the selector as necessary)
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for the result page to load (adjust this to wait for a specific media element)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.media-image-class'))
        )

        # Extract the media URLs (adjust the selectors based on FastDL's response)
        media_urls = []
        images = driver.find_elements(By.CSS_SELECTOR, '.media-image-class')  # Replace with actual selector
        videos = driver.find_elements(By.CSS_SELECTOR, '.media-video-class')  # Replace with actual selector

        for image in images:
            media_urls.append({"url": image.get_attribute("src"), "type": "image"})
        
        for video in videos:
            media_urls.append({"url": video.get_attribute("src"), "type": "video"})

        # Check if media was found
        if not media_urls:
            return jsonify({"error": "No media found for this URL."}), 404

        return jsonify({"media": media_urls}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
