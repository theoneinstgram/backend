from flask import Flask, request, jsonify
import instaloader

app = Flask(__name__)

# Initialize instaloader
L = instaloader.Instaloader()

# Fetch media from Instagram
def fetch_instagram_media(url):
    try:
        # Extract shortcode from the URL
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Separate media into photos, videos, and reels
        photos = []
        videos = []
        reels = []

        # Check if the post is private
        if post.is_private:
            return {"error": "The profile is private. Unable to fetch media."}

        # Loop through the media of the post
        for index, node in enumerate(post.get_posts()):
            if node.is_video:
                videos.append({
                    "url": node.video_url,
                    "caption": node.caption
                })
            else:
                photos.append({
                    "url": node.url,
                    "caption": node.caption
                })

            # Check if it's a reel (can be differentiated via 'is_video')
            if hasattr(post, 'is_reel') and post.is_reel:
                reels.append({
                    "url": node.url,
                    "caption": node.caption
                })

        # Check if we found any media
        if not photos and not videos and not reels:
            return {"error": "No media (photos/videos/reels) found."}
        
        # Return error if no photos, videos, or reels are found
        if not photos:
            return {"error": "No photos found."}
        if not videos:
            return {"error": "No videos found."}
        if not reels:
            return {"error": "No reels found."}

        return {"photos": photos, "videos": videos, "reels": reels}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "An error occurred while fetching the media."}

@app.route('/fetch-media', methods=['POST'])
def fetch_media():
    data = request.json
    instagram_url = data.get("url")

    if not instagram_url:
        return jsonify({"error": "Instagram URL is required"}), 400

    media_data = fetch_instagram_media(instagram_url)

    if 'error' in media_data:
        return jsonify(media_data), 400
    else:
        return jsonify(media_data), 200

if __name__ == "__main__":
    # Use gunicorn to run in production
    from gunicorn.app.base import BaseApplication

    class GunicornApplication(BaseApplication):
        def init(self, parser, opts, args):
            return {
                'bind': '0.0.0.0:5000',
                'workers': 2,
            }

        def load(self):
            return app

    GunicornApplication(None).run()
