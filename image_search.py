"""
Google Image Search API Implementation
"""

from google_images_search import GoogleImagesSearch
from io import BytesIO
from PIL import Image
import os
import shutil
from typing import List, Dict, Optional, Union, Tuple
import config


class GoogleImageAPI:
    """Google Image Search API wrapper class"""

    def _get_image_dimensions_from_url(self, url: str) -> Tuple[int, int]:
        """
        Get the dimensions of an image from its URL without downloading the entire image.
        
        Args:
            url (str): The URL of the image
            
        Returns:
            Tuple[int, int]: Width and height of the image, or None if it cannot be determined
        """
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            # Make a HEAD request first to check content type
            head_response = requests.head(url, timeout=5)
            if not head_response.headers.get('content-type', '').startswith('image'):
                return None
                
            # Stream just enough of the image to get dimensions
            response = requests.get(url, stream=True, timeout=5)
            content = BytesIO()
            
            # Get just the beginning of the file
            for chunk in response.iter_content(chunk_size=1024):
                content.write(chunk)
                try:
                    img = Image.open(content)
                    return img.size  # (width, height)
                except Exception:
                    # Not enough data yet, continue downloading
                    continue
                    
            # If we get here, we couldn't determine the size
            return None
            
        except Exception as e:
            print(f"Error getting image dimensions: {str(e)}")
            return None

    def __init__(self, developer_key: str = None, cx: str = None):
        """
        Initialize the Google Image Search API
        
        Args:
            developer_key (str, optional): Google API developer key. Defaults to config.DEVELOPER_KEY.
            cx (str, optional): Google Custom Search Engine ID. Defaults to config.CX.
        """
        self.developer_key = developer_key or config.DEVELOPER_KEY
        self.cx = cx or config.CX
        self.gis = GoogleImagesSearch(self.developer_key, self.cx)
        
    def search(self, 
               query: str, 
               num_images: int = 5, 
               safe_search: bool = True, 
               file_type: str = None,
               color_type: str = None,
               image_size: str = None,
               image_type: str = None,
               download_directory: str = None,
               custom_file_names: List[str] = None) -> List[Dict]:
        """
        Search for images using Google Images Search API
        
        Args:
            query (str): Search query
            num_images (int, optional): Number of images to return. Defaults to 5.
            safe_search (bool, optional): Whether to enable safe search. Defaults to True.
            file_type (str, optional): File type to search for (jpg, png, etc.)
            color_type (str, optional): Color type (color, gray, etc.)
            image_size (str, optional): Image size (large, medium, etc.)
            image_type (str, optional): Image type (photo, clip-art, etc.)
            download_directory (str, optional): Directory to download images to.
            custom_file_names (List[str], optional): Custom file names for downloaded images.
            
        Returns:
            List[Dict]: List of dictionaries containing image details
        """
        # Define search parameters
        search_params = {
            'q': query,
            'num': num_images,
            'safe': 'active' if safe_search else 'off',
        }
        
        # Add optional parameters if provided
        if file_type:
            search_params['fileType'] = file_type
        if color_type:
            search_params['colorType'] = color_type
        if image_size:
            search_params['imgSize'] = image_size
        if image_type:
            search_params['imgType'] = image_type
            
        # Search for images
        self.gis.search(search_params=search_params)
        
        # Process results
        results = []
        for i, image in enumerate(self.gis.results()):
            # The results are GSImage objects with limited attributes
            # We need to extract what we can, default the rest
            
            # Use BytesIO to get image dimensions without saving to disk
            image_dimensions = self._get_image_dimensions_from_url(image.url)
            
            image_data = {
                'url': image.url,
                'referrer_url': image.referrer_url,
                'width': image_dimensions[0] if image_dimensions else 0,
                'height': image_dimensions[1] if image_dimensions else 0,
                'file_name': os.path.basename(image.url.split('?')[0]),
                'file_size': 0  # We can't get this without downloading
            }
            
            # Download the image if a directory is specified
            if download_directory:
                os.makedirs(download_directory, exist_ok=True)
                
                # Set custom filename if provided
                if custom_file_names and i < len(custom_file_names):
                    # Extract extension from the URL
                    img_url = image.url
                    extension = os.path.splitext(os.path.basename(img_url.split('?')[0]))[1]
                    if not extension:
                        extension = '.jpg'  # Default to jpg if no extension found
                    filename = custom_file_names[i] + extension
                else:
                    # Generate a filename based on index if none provided
                    img_url = image.url
                    basename = os.path.basename(img_url.split('?')[0])
                    filename = basename if basename else f'image_{i}.jpg'
                
                # The GSImage download method doesn't support custom filenames
                # We need to download it first and then rename it
                try:
                    # Download the image with default name
                    image.download(download_directory)
                    
                    # Get the downloaded path
                    downloaded_path = image.path
                    
                    # If the download worked and we want a custom filename
                    if downloaded_path and os.path.exists(downloaded_path):
                        # Rename to our desired filename
                        new_path = os.path.join(download_directory, filename)
                        if downloaded_path != new_path:
                            shutil.move(downloaded_path, new_path)
                            filepath = new_path
                        else:
                            filepath = downloaded_path
                    else:
                        # Use manual download if we couldn't get the file
                        filepath = os.path.join(download_directory, filename)
                        import requests
                        response = requests.get(image.url, stream=True)
                        if response.status_code == 200:
                            with open(filepath, 'wb') as f:
                                for chunk in response.iter_content(1024):
                                    f.write(chunk)
                except Exception as e:
                    print(f"Error downloading image: {str(e)}")
                    continue
                image_data['local_path'] = os.path.join(download_directory, filename)
                
            results.append(image_data)
            
        return results
    
    def resize_image(self, 
                    image_path: str, 
                    output_path: str = None, 
                    width: int = None, 
                    height: int = None,
                    maintain_aspect_ratio: bool = True) -> str:
        """
        Resize an image
        
        Args:
            image_path (str): Path to the image
            output_path (str, optional): Path to save the resized image. Defaults to overwriting original.
            width (int, optional): Target width
            height (int, optional): Target height
            maintain_aspect_ratio (bool, optional): Whether to maintain aspect ratio. Defaults to True.
            
        Returns:
            str: Path to the resized image
        """
        if not width and not height:
            raise ValueError("At least one of width or height must be specified")
            
        if not output_path:
            output_path = image_path
            
        img = Image.open(image_path)
        original_width, original_height = img.size
        
        if maintain_aspect_ratio:
            if width and height:
                # Calculate which dimension to use based on aspect ratio
                original_ratio = original_width / original_height
                target_ratio = width / height
                
                if original_ratio > target_ratio:
                    # Image is wider than target, use width as constraint
                    new_width = width
                    new_height = int(new_width / original_ratio)
                else:
                    # Image is taller than target, use height as constraint
                    new_height = height
                    new_width = int(new_height * original_ratio)
            elif width:
                # Calculate height based on aspect ratio
                new_width = width
                new_height = int(original_height * (width / original_width))
            else:
                # Calculate width based on aspect ratio
                new_height = height
                new_width = int(original_width * (height / original_height))
        else:
            # No aspect ratio maintenance, just use the specified dimensions
            new_width = width or original_width
            new_height = height or original_height
            
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to RGB if it's RGBA mode and we're saving as JPEG
        if resized_img.mode == 'RGBA' and output_path.lower().endswith(('.jpg', '.jpeg')):
            resized_img = resized_img.convert('RGB')
        
        resized_img.save(output_path)
        
        return output_path


if __name__ == "__main__":
    # Example usage
    api = GoogleImageAPI()
    
    # Search for images
    results = api.search(
        query="cute puppies",
        num_images=3,
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
        print()
