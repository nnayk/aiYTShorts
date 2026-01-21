import os
from moviepy import ImageClip, concatenate_videoclips

# --- Configuration ---
image_folder = '.'  # Current directory
output_file = 'my_slideshow.mp4'
image_duration = 2  # Seconds to show each image
fps = 24            # Frames per second for the video

def create_slideshow():
    # Download all images from myFile.txt
    with open('myFile.txt', 'r') as f:
        image_urls = f.readlines()
        for url in image_urls:
            url = url.strip()  # Remove newline and whitespace
            if not url:  # Skip empty lines
                continue
            filename = url.split('/')[-1]
            print(f"Downloading {url}")
            os.system(f"curl -L '{url}' -o '{filename}'")

    # 1. Get all .png files from the directory
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    
    # 2. Sort the images to ensure they appear in the correct order
    # (defaults to alphabetical order: image01.png, image02.png...)
    images.sort()

    if not images:
        print("No PNG files found in the directory.")
        return

    print(f"Found {len(images)} images. Creating slideshow...")

    # 3. Create ImageClip objects for each file
    clips = []
    for image in images:
        # Create the clip and set how long it stays on screen
        clip = ImageClip(os.path.join(image_folder, image)).with_duration(image_duration)
        clips.append(clip)

    # 4. Combine all clips into one video
    # method="compose" is robust and handles different image sizes reasonably well
    final_video = concatenate_videoclips(clips, method="compose")

    # 5. Write the result to a file
    final_video.write_videofile(output_file, fps=fps)
    print(f"Slideshow saved as {output_file}")

if __name__ == '__main__':
    create_slideshow()