#!/usr/bin/env python
"""
Example usage of the Google Image Search API
"""

from image_search import GoogleImageAPI
import os
import json
import sys


def basic_search_example():
    """
    Basic search example
    """
    print("\n=== Basic Search Example ===\n")
    
    # Initialize the API
    api = GoogleImageAPI()
    
    # Search for images
    results = api.search(
        query="beautiful landscapes",
        num_images=3,
        safe_search=True
    )
    
    # Print results
    print(f"Found {len(results)} results")
    for i, result in enumerate(results, 1):
        print(f"\nImage {i}:")
        print(f"  URL: {result['url']}")
        print(f"  Size: {result['width']}x{result['height']}")
        print(f"  File name: {result['file_name']}")
        print(f"  File size: {result['file_size']} bytes")


def download_images_example():
    """
    Download images example
    """
    print("\n=== Download Images Example ===\n")
    
    # Initialize the API
    api = GoogleImageAPI()
    
    # Create download directory
    download_dir = "example_downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Search for images and download them
    results = api.search(
        query="cute cats",
        num_images=2,
        safe_search=True,
        download_directory=download_dir,
        custom_file_names=["cat1", "cat2"]
    )
    
    # Print results
    print(f"Downloaded {len(results)} images")
    for i, result in enumerate(results, 1):
        print(f"\nImage {i}:")
        print(f"  URL: {result['url']}")
        print(f"  Downloaded to: {result['local_path']}")


def resize_image_example():
    """
    Resize image example
    """
    print("\n=== Resize Image Example ===\n")
    
    # Check if we have downloaded images from the previous example
    download_dir = "example_downloads"
    if not os.path.exists(download_dir) or not os.listdir(download_dir):
        print("No downloaded images found. Run the download_images_example first.")
        return
    
    # Initialize the API
    api = GoogleImageAPI()
    
    # Get the first image in the download directory
    image_path = os.path.join(download_dir, os.listdir(download_dir)[0])
    output_path = os.path.join(download_dir, "resized_" + os.path.basename(image_path))
    
    # Resize the image
    try:
        api.resize_image(
            image_path=image_path,
            output_path=output_path,
            width=300,
            height=200,
            maintain_aspect_ratio=True
        )
        
        print(f"Image resized successfully:")
        print(f"  Original: {image_path}")
        print(f"  Resized: {output_path}")
    except Exception as e:
        print(f"Error resizing image: {str(e)}")


def run_all_examples():
    """
    Run all examples
    """
    basic_search_example()
    download_images_example()
    resize_image_example()


if __name__ == "__main__":
    # Check if API credentials are set
    import config
    if config.DEVELOPER_KEY == "YOUR_DEVELOPER_KEY" or config.CX == "YOUR_CUSTOM_SEARCH_ENGINE_ID":
        print("ERROR: You need to set your Google API credentials in config.py")
        print("Please update the DEVELOPER_KEY and CX values in config.py with your actual credentials.")
        sys.exit(1)
    
    # Run all examples
    run_all_examples()
