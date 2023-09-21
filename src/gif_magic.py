import os
import subprocess

def create_gif(input_dir, output_file, delay=10):
    # Check if the input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    # Get a list of image files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        print(f"No image files found in '{input_dir}'.")
        return

    # Construct the ImageMagick command
    convert_command = [
        'convert',                # The ImageMagick command
        '-delay', str(delay),     # Set the delay between frames in milliseconds
        os.path.join(input_dir, '*'),  # Input image files path
        output_file               # Output GIF file
    ]

    try:
        # Run the ImageMagick command
        subprocess.run(convert_command, check=True)
        print(f"GIF created: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating GIF: {e}")

if __name__ == "__main__":
    input_directory = "../img/mkgifs"  # Replace with your input directory
    output_filename = "output.gif"    # Replace with your output GIF filename
    frame_delay = 10                # Delay between frames in milliseconds

    create_gif(input_directory, output_filename, frame_delay)
