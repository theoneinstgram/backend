from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import instaloader
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Folder to store downloaded media
MEDIA_FOLDER = './downloads'
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

@app.route('/api/download-media', methods=['POST'])
def download_media():
    try:
        url = request.json.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Instantiate Instaloader
        loader = instaloader.Instaloader()

        # Extract the shortcode from the URL
        shortcode = url.split("/")[-2]
        
        # Get the post from the shortcode
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        # If the post is private, skip it
        if post.owner_profile.is_private:
            return jsonify({"error": "The post is from a private account and cannot be accessed."}), 403

        photos = []
        videos = []
        reels = []
        
        # Check if it's a video or photo post
        if post.is_video:
            video_path = os.path.join(MEDIA_FOLDER, f'{post.shortcode}_video.mp4')
            video_url = post.video_url
            download_video(video_url, video_path)
            videos.append(f"/media/{post.shortcode}_video.mp4")
        else:
            photo_path = os.path.join(MEDIA_FOLDER, f'{post.shortcode}_photo.jpg')
            download_photo(post.url, photo_path)
            photos.append(f"/media/{post.shortcode}_photo.jpg")

        # Handle the media response
        return jsonify({
            "photos": photos,
            "videos": videos,
            "reels": reels
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def download_video(video_url, path):
    # Download the video
    response = requests.get(video_url)
    with open(path, 'wb') as file:
        file.write(response.content)

def download_photo(photo_url, path):
    # Download the photo
    response = requests.get(photo_url)
    with open(path, 'wb') as file:
        file.write(response.content)

@app.route('/media/<filename>')
def get_media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
