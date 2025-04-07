#!/usr/bin/env python3
"""
JPEG to GIF Converter (written with Claude AI)

This script converts a directory of JPEG images into an animated GIF.
It sorts the images by filename to ensure proper sequence.

Usage:
    python jpeg_to_gif.py <input_directory> <output_file> [--fps 10] [--loop 0] [--quality 90] [--resize 800x600]

Example:
    python jpeg_to_gif.py ./my_images output.gif --fps 15 --resize 640x480

Arguments:
    input_directory  - Directory containing JPEG images
    output_file      - Output GIF filename
    --fps            - Frames per second (default: 10)
    --loop           - Number of times to loop (0 = infinite, default: 0)
    --quality        - Quality of output GIF (1-100, default: 90)
    --resize         - Resize images to this dimension (e.g., 800x600)
"""

import os
import glob
import argparse
from PIL import Image
import imageio

def create_gif(input_dir, output_file, fps=10, loop=0, quality=90, resize=None):
    """Convert a directory of JPEG images to an animated GIF."""
    print(f"Creating GIF from images in {input_dir}...")
    
    # Get all jpeg files
    image_files = glob.glob(os.path.join(input_dir, "*.jp*g"))
    image_files.extend(glob.glob(os.path.join(input_dir, "*.JP*G")))
    
    # Sort by numeric value in filename
    def extract_number(filename):
        """Extract the numeric part from a filename."""
        import re
        # Find all numbers in the filename
        numbers = re.findall(r'\d+', os.path.basename(filename))
        # Return the last number found (or 0 if none found)
        return int(numbers[-1]) if numbers else 0
    
    # Sort by the extracted number
    image_files = sorted(image_files, key=extract_number)
    
    if not image_files:
        print(f"No JPEG images found in {input_dir}")
        return False
    
    print(f"Found {len(image_files)} JPEG images")
    
    # Prepare images
    images = []
    for image_file in image_files:
        try:
            img = Image.open(image_file)
            
            # Resize if specified
            if resize:
                width, height = resize
                img = img.resize((width, height), Image.LANCZOS)
            
            # Convert to RGB to handle RGBA or CMYK images
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            images.append(img)
        except Exception as e:
            print(f"Error processing {image_file}: {e}")
    
    if not images:
        print("No valid images could be processed")
        return False
    
    # Save as GIF
    try:
        print(f"Creating GIF with {fps} frames per second...")
        with imageio.get_writer(output_file, mode='I', duration=1/fps, loop=loop, quality=quality) as writer:
            for img in images:
                # Convert PIL Image to numpy array
                writer.append_data(imageio.core.asarray(img))
        
        print(f"GIF successfully created: {output_file}")
        print(f"GIF contains {len(images)} frames at {fps} FPS")
        return True
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return False

def parse_resize(resize_str):
    """Parse the resize argument from string to tuple of integers."""
    if not resize_str:
        return None
    try:
        width, height = resize_str.lower().split('x')
        return (int(width), int(height))
    except:
        raise argparse.ArgumentTypeError("Resize must be in format WIDTHxHEIGHT (e.g., 800x600)")

def main():
    parser = argparse.ArgumentParser(description='Convert JPEG images to an animated GIF')
    parser.add_argument('input_dir', help='Directory containing JPEG images')
    parser.add_argument('output_file', help='Output GIF filename')
    parser.add_argument('--fps', type=int, default=10, help='Frames per second (default: 10)')
    parser.add_argument('--loop', type=int, default=0, help='Number of times to loop (0 = infinite, default: 0)')
    parser.add_argument('--quality', type=int, default=90, help='Quality of output GIF (1-100, default: 90)')
    parser.add_argument('--resize', type=parse_resize, help='Resize images to this dimension (e.g., 800x600)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.isdir(args.input_dir):
        print(f"Error: {args.input_dir} is not a valid directory")
        return
    
    if args.fps <= 0:
        print("Error: FPS must be greater than 0")
        return
        
    if args.quality < 1 or args.quality > 100:
        print("Error: Quality must be between 1 and 100")
        return
    
    # Create the GIF
    create_gif(
        args.input_dir, 
        args.output_file, 
        fps=args.fps, 
        loop=args.loop, 
        quality=args.quality,
        resize=args.resize
    )

if __name__ == "__main__":
    main()