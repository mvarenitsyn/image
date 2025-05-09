"""
Google Image Search API Implementation
"""

from google_images_search import GoogleImagesSearch
from io import BytesIO
from PIL import Image
import os
from typing import List, Dict, Optional, Union, Tuple
import config


class GoogleImageAPI:
    """Google Image Search API wrapper class"""

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
            image_data = {
                'url': image.url,
                'referrer_url': image.referrer_url,
                'width': image.width,
                'height': image.height,
                'file_name': image.filename,
                'file_size': image.filesize
            }
            
            # Download the image if a directory is specified
            if download_directory:
                os.makedirs(download_directory, exist_ok=True)
                
                # Set custom filename if provided
                if custom_file_names and i < len(custom_file_names):
                    # Extract extension from original filename
                    extension = os.path.splitext(image.filename)[1]
                    filename = custom_file_names[i] + extension
                else:
                    filename = image.filename
                
                # Download the image
                image.download(download_directory, filename=filename)
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
