from selenium import webdriver
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/fastdl-download', methods=['POST'])
def fastdl_download():
    url = request.json.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Initialize Selenium WebDriver (example with Chrome)
    driver = webdriver.Chrome()

    try:
        # Visit the FastDL page
        driver.get('https://fastdl.app/en')

        # Wait for the page to load
        time.sleep(5)

        # Find the input field for the URL (adjust selector as necessary)
        input_element = driver.find_element_by_css_selector('input[name="url"]')
        input_element.send_keys(url)

        # Submit the form (adjust the selector as necessary)
        submit_button = driver.find_element_by_css_selector('button[type="submit"]')
        submit_button.click()

        # Wait for the download to complete (adjust this part as necessary)
        time.sleep(10)

        # Extract the media URLs (you need to adjust the selectors based on FastDL's response)
        media_urls = []
        # Example: Find media elements
        images = driver.find_elements_by_css_selector('.media-image-class')  # Replace with actual selector
        videos = driver.find_elements_by_css_selector('.media-video-class')  # Replace with actual selector

        for image in images:
            media_urls.append({"url": image.get_attribute("src"), "type": "image"})
        
        for video in videos:
            media_urls.append({"url": video.get_attribute("src"), "type": "video"})

        return jsonify({"media": media_urls}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
