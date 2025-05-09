"""
Flask-based REST API for Google Image Search
"""

from flask import Flask, request, jsonify, send_file
import os
import json
from dotenv import load_dotenv
from image_search import GoogleImageAPI
import tempfile
import shutil
from werkzeug.utils import secure_filename

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the Google Image API
google_api = GoogleImageAPI()

@app.route('/', methods=['GET'])
def home():
    """
    API home page with basic information
    """
    return jsonify({
        'name': 'Google Image Search API',
        'version': '1.0.0',
        'endpoints': {
            '/': 'This information page',
            '/search': 'Search for images',
            '/download': 'Download and optionally resize an image',
            '/cleanup': 'Clean up temporary downloaded files',
            '/health': 'Health check endpoint'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Railway
    """
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

# Create a temporary directory for storing downloaded images
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'google_images_search')
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route('/search', methods=['GET'])
def search_images():
    """
    Search for images using Google Images Search API
    
    Query Parameters:
    - q: Search query (required)
    - num: Number of images to return (default: 5)
    - safe: Enable safe search (default: true)
    - file_type: File type to search for (jpg, png, etc.)
    - color_type: Color type (color, gray, etc.)
    - image_size: Image size (large, medium, etc.)
    - image_type: Image type (photo, clip-art, etc.)
    - download: Whether to download images (default: false)
    
    Returns:
        JSON object containing image results
    """
    try:
        # Get query parameters
        query = request.args.get('q')
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
            
        num_images = int(request.args.get('num', 5))
        safe_search = request.args.get('safe', 'true').lower() == 'true'
        file_type = request.args.get('file_type')
        color_type = request.args.get('color_type')
        image_size = request.args.get('image_size')
        image_type = request.args.get('image_type')
        download = request.args.get('download', 'false').lower() == 'true'
        
        # Create a unique download directory if downloading is requested
        download_dir = None
        if download:
            download_dir = os.path.join(TEMP_DIR, secure_filename(query))
            os.makedirs(download_dir, exist_ok=True)
        
        # Search for images
        results = google_api.search(
            query=query,
            num_images=num_images,
            safe_search=safe_search,
            file_type=file_type,
            color_type=color_type,
            image_size=image_size,
            image_type=image_type,
            download_directory=download_dir
        )
        
        # Return results as JSON
        return jsonify({
            'query': query,
            'num_results': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['GET'])
def download_image():
    """
    Download an image from a URL and optionally resize it
    
    Query Parameters:
    - url: Image URL (required)
    - width: Target width for resizing
    - height: Target height for resizing
    - maintain_aspect_ratio: Whether to maintain aspect ratio (default: true)
    
    Returns:
        The image file
    """
    try:
        # Get query parameters
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'Query parameter "url" is required'}), 400
            
        width = request.args.get('width')
        if width:
            width = int(width)
            
        height = request.args.get('height')
        if height:
            height = int(height)
            
        maintain_aspect_ratio = request.args.get('maintain_aspect_ratio', 'true').lower() == 'true'
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
        
        # Download the image
        filename = os.path.basename(url.split('?')[0])  # Remove query parameters
        if not filename:
            filename = 'image.jpg'
            
        # Secure the filename
        filename = secure_filename(filename)
        filepath = os.path.join(temp_dir, filename)
        
        # Use the GoogleImageAPI to download and optionally resize the image
        custom_search_result = google_api.search(
            query='',  # Empty query because we're just using the download functionality
            num_images=1,
            download_directory=temp_dir,
            custom_file_names=[os.path.splitext(filename)[0]]
        )
        
        # If width or height is specified, resize the image
        if (width or height) and custom_search_result:
            local_path = custom_search_result[0].get('local_path')
            if local_path:
                google_api.resize_image(
                    image_path=local_path,
                    width=width,
                    height=height,
                    maintain_aspect_ratio=maintain_aspect_ratio
                )
                
                return send_file(local_path, mimetype=f'image/{os.path.splitext(filename)[1][1:]}')
        
        # If resize failed or wasn't requested, return original image
        if custom_search_result and custom_search_result[0].get('local_path'):
            return send_file(custom_search_result[0]['local_path'], 
                             mimetype=f'image/{os.path.splitext(filename)[1][1:]}')
        else:
            return jsonify({'error': 'Failed to download the image'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary directory
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.route('/cleanup', methods=['POST'])
def cleanup_temp_files():
    """
    Clean up temporary downloaded files
    
    Returns:
        Success message
    """
    try:
        # Remove the temporary directory
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            os.makedirs(TEMP_DIR, exist_ok=True)
            
        return jsonify({'message': 'Temporary files cleaned up successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Get port from environment variable for Railway deployment
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(debug=False, host='0.0.0.0', port=port)
