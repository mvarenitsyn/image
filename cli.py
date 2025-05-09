#!/usr/bin/env python
"""
Command-line interface for Google Image Search API
"""

import argparse
import json
import os
import sys
from image_search import GoogleImageAPI


def main():
    """
    Main entry point for the CLI application
    """
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Google Image Search CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for images')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', '--num', type=int, default=5, help='Number of images to return (default: 5)')
    search_parser.add_argument('--no-safe-search', action='store_true', help='Disable safe search filtering')
    search_parser.add_argument('--file-type', help='File type filter (e.g., jpg, png)')
    search_parser.add_argument('--color-type', help='Color type filter (e.g., color, gray)')
    search_parser.add_argument('--image-size', help='Image size filter (e.g., large, medium)')
    search_parser.add_argument('--image-type', help='Image type filter (e.g., photo, clip-art)')
    search_parser.add_argument('-d', '--download', help='Directory to download images to')
    search_parser.add_argument('-o', '--output', help='File to save results to (JSON format)')
    search_parser.add_argument('--quiet', action='store_true', help='Only output JSON results, no additional information')
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize an image')
    resize_parser.add_argument('image_path', help='Path to the image to resize')
    resize_parser.add_argument('-o', '--output', help='Output path for the resized image')
    resize_parser.add_argument('-w', '--width', type=int, help='Target width')
    resize_parser.add_argument('-h', '--height', type=int, help='Target height')
    resize_parser.add_argument('--no-aspect-ratio', action='store_true', help='Do not maintain aspect ratio')
    
    # Run command (start API server)
    run_parser = subparsers.add_parser('run', help='Run the API server')
    run_parser.add_argument('-H', '--host', default='0.0.0.0', help='Host to listen on (default: 0.0.0.0)')
    run_parser.add_argument('-p', '--port', type=int, default=5000, help='Port to listen on (default: 5000)')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the Google Image API
    api = GoogleImageAPI()
    
    # Execute the appropriate command
    if args.command == 'search':
        search_command(api, args)
    elif args.command == 'resize':
        resize_command(api, args)
    elif args.command == 'run':
        run_command(args)
    else:
        parser.print_help()
        return 1
    
    return 0


def search_command(api, args):
    """
    Execute the search command
    
    Args:
        api: GoogleImageAPI instance
        args: Command-line arguments
    """
    # Execute the search
    results = api.search(
        query=args.query,
        num_images=args.num,
        safe_search=not args.no_safe_search,
        file_type=args.file_type,
        color_type=args.color_type,
        image_size=args.image_size,
        image_type=args.image_type,
        download_directory=args.download
    )
    
    # Format the results
    output = {
        'query': args.query,
        'num_results': len(results),
        'results': results
    }
    
    # Output the results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        
        if not args.quiet:
            print(f"Results saved to {args.output}")
    else:
        if args.quiet:
            print(json.dumps(output))
        else:
            print(f"Found {len(results)} results for query: '{args.query}'")
            for i, result in enumerate(results, 1):
                print(f"\nImage {i}:")
                print(f"  URL: {result['url']}")
                print(f"  Size: {result['width']}x{result['height']}")
                if 'local_path' in result:
                    print(f"  Saved to: {result['local_path']}")


def resize_command(api, args):
    """
    Execute the resize command
    
    Args:
        api: GoogleImageAPI instance
        args: Command-line arguments
    """
    # Validate arguments
    if not args.width and not args.height:
        print("Error: At least one of --width or --height must be specified")
        return 1
    
    # Execute the resize
    try:
        output_path = api.resize_image(
            image_path=args.image_path,
            output_path=args.output,
            width=args.width,
            height=args.height,
            maintain_aspect_ratio=not args.no_aspect_ratio
        )
        
        print(f"Image resized successfully: {output_path}")
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return 1


def run_command(args):
    """
    Execute the run command (start API server)
    
    Args:
        args: Command-line arguments
    """
    try:
        # Import Flask app
        from api import app
        
        # Run the Flask app
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except ImportError:
        print("Error: Flask is not installed. Please install it with: pip install flask")
        return 1
    except Exception as e:
        print(f"Error starting API server: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
