# Google Image Search API

A Python library and REST API for searching and downloading images from Google using the `Google-Images-Search` package. Prepared for deployment on Railway.

## Features

- Search for images with various filtering options
- Download images to local storage
- Resize images while maintaining aspect ratio
- REST API with Flask
- Command-line interface
- Python API for integration into other projects

## Installation

### Prerequisites

- Python 3.6+
- Google API Key
- Google Custom Search Engine ID

### Setup

1. Clone this repository:

```bash
git clone https://github.com/mvarenitsyn/image.git
cd image
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your Google API credentials:

Create a `.env` file based on the `.env.example` file:

```bash
cp .env.example .env
```

Then edit the `.env` file to add your Google API key and Custom Search Engine ID:

```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

#### How to Get Google API Credentials

1. **Google API Key**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the "Custom Search API"
   - Create credentials (API Key)

2. **Custom Search Engine ID**:
   - Go to the [Google Programmable Search Engine](https://programmablesearchengine.google.com/about/)
   - Create a new search engine
   - Set it to search the entire web
   - Get your Search Engine ID (cx)

## Usage

### Python API

```python
from image_search import GoogleImageAPI

# Initialize the API
api = GoogleImageAPI()

# Search for images
results = api.search(
    query="cute puppies",
    num_images=5,
    safe_search=True,
    download_directory="downloaded_images"
)

# Print results
for i, result in enumerate(results, 1):
    print(f"Image {i}:")
    print(f"  URL: {result['url']}")
    print(f"  Size: {result['width']}x{result['height']}")
    if 'local_path' in result:
        print(f"  Saved to: {result['local_path']}")

# Resize an image
api.resize_image(
    image_path="downloaded_images/image.jpg",
    output_path="downloaded_images/resized_image.jpg",
    width=800,
    height=600,
    maintain_aspect_ratio=True
)
```

### Command-Line Interface

The CLI provides three main commands: `search`, `resize`, and `run`.

#### Search for Images

```bash
python cli.py search "cute puppies" -n 10 --download ./images
```

Options:
- `-n, --num`: Number of images to return (default: 5)
- `--no-safe-search`: Disable safe search filtering
- `--file-type`: File type filter (e.g., jpg, png)
- `--color-type`: Color type filter (e.g., color, gray)
- `--image-size`: Image size filter (e.g., large, medium)
- `--image-type`: Image type filter (e.g., photo, clip-art)
- `-d, --download`: Directory to download images to
- `-o, --output`: File to save results to (JSON format)
- `--quiet`: Only output JSON results, no additional information

#### Resize an Image

```bash
python cli.py resize ./images/image.jpg -w 800 -h 600
```

Options:
- `-o, --output`: Output path for the resized image
- `-w, --width`: Target width
- `-h, --height`: Target height
- `--no-aspect-ratio`: Do not maintain aspect ratio

#### Run the API Server

```bash
python cli.py run --debug
```

Options:
- `-H, --host`: Host to listen on (default: 0.0.0.0)
- `-p, --port`: Port to listen on (default: 5000)
- `--debug`: Enable debug mode

### REST API

Start the API server:

```bash
python api.py
```

Or use the CLI:

```bash
python cli.py run
```

#### Endpoints

##### GET /search

Search for images.

Query Parameters:
- `q`: Search query (required)
- `num`: Number of images to return (default: 5)
- `safe`: Enable safe search (default: true)
- `file_type`: File type to search for (jpg, png, etc.)
- `color_type`: Color type (color, gray, etc.)
- `image_size`: Image size (large, medium, etc.)
- `image_type`: Image type (photo, clip-art, etc.)
- `download`: Whether to download images (default: false)

Example:
```
GET /search?q=cute+puppies&num=10&safe=true
```

Response:
```json
{
  "query": "cute puppies",
  "num_results": 10,
  "results": [
    {
      "url": "https://example.com/image1.jpg",
      "referrer_url": "https://example.com/page1",
      "width": 800,
      "height": 600,
      "file_name": "image1.jpg",
      "file_size": 102400
    },
    ...
  ]
}
```

##### GET /download

Download an image from a URL and optionally resize it.

Query Parameters:
- `url`: Image URL (required)
- `width`: Target width for resizing
- `height`: Target height for resizing
- `maintain_aspect_ratio`: Whether to maintain aspect ratio (default: true)

Example:
```
GET /download?url=https://example.com/image.jpg&width=800&height=600
```

Response: The image file.

##### POST /cleanup

Clean up temporary downloaded files.

Example:
```
POST /cleanup
```

Response:
```json
{
  "message": "Temporary files cleaned up successfully"
}
```

## Example Use Cases

### Web Application

You can build a web application that uses the API to search for images:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Image Search</title>
    <script>
        async function searchImages() {
            const query = document.getElementById('query').value;
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';
            
            data.results.forEach(image => {
                const img = document.createElement('img');
                img.src = image.url;
                img.width = 200;
                resultsDiv.appendChild(img);
            });
        }
    </script>
</head>
<body>
    <h1>Image Search</h1>
    <input type="text" id="query" placeholder="Search for images">
    <button onclick="searchImages()">Search</button>
    <div id="results"></div>
</body>
</html>
```

### Integration with Other Projects

You can integrate the API into other Python projects:

```python
from image_search import GoogleImageAPI

def get_image_for_product(product_name):
    api = GoogleImageAPI()
    results = api.search(
        query=product_name,
        num_images=1,
        safe_search=True
    )
    if results:
        return results[0]['url']
    return None
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Google-Images-Search](https://pypi.org/project/Google-Images-Search/) package
- Google Custom Search API

## Deployment on Railway

This project is configured for easy deployment to [Railway](https://railway.app/).

### Deploy to Railway

1. Fork this repository to your GitHub account
2. Sign up for Railway and connect your GitHub account
3. Create a new project and select the forked repository
4. Add the following environment variables in the Railway dashboard:
   - `GOOGLE_API_KEY` - Your Google API key
   - `GOOGLE_CSE_ID` - Your Custom Search Engine ID
5. Deploy the project

Railway will automatically detect the Dockerfile and deploy the application.

### Local Testing for Railway

To test your Railway deployment locally:

```bash
# Set environment variables
export GOOGLE_API_KEY=your_google_api_key
export GOOGLE_CSE_ID=your_custom_search_engine_id
export PORT=8080

# Run the application
python api.py
```

The API will be available at http://localhost:8080.
