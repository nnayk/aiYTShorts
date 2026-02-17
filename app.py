import os
import subprocess
import re
from time import sleep
from flask import Flask, request, jsonify
from google import genai
from PIL import Image
from datetime import datetime
from elevenlabs.client import ElevenLabs
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

app = Flask(__name__)

# Setup Gemini client
# API_KEY = os.environ.get("GEMVINI_KEY")
# if not API_KEY:
#     raise ValueError("GEMINI_KEY environment variable is not set")

# client = genai.Client(api_key=API_KEY)

@app.route('/generateImage', methods=['POST'])
def generate_image():
    """
    Generate an image using Gemini 3 Pro Image Preview model.
    
    Expected JSON body:
    {
        "prompt": "Your image generation prompt here"
    }
    """
    try:
        # Get prompt from request
        # data = request.get_json()
        # if not data or 'prompt' not in data:
        #     return jsonify({'error': 'Missing "prompt" in request body'}), 400
        
        # prompt = data['prompt']
        prompt = "Leon Edwards knocks out Kamaru Usman"
        
        print(f"Generating image with prompt: {prompt}")
        
        # Call the Gemini model
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt]
        )
        
        # Save the image
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    # Convert to PIL Image
                    image = part.as_image()
                    
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_image_{timestamp}.png"
                    
                    # Save the image
                    image.save(filename)
                    print(f"Success! Image saved as '{filename}'")
                    
                    # Open the image locally (macOS)
                    try:
                        subprocess.run(['open', filename], check=True)
                        print(f"Image opened in default viewer")
                    except subprocess.CalledProcessError as e:
                        print(f"Warning: Could not open image automatically: {e}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Image generated successfully',
                        'filename': filename
                    }), 200
        
        return jsonify({'error': 'No image generated. Check your prompt or API quota.'}), 500
        
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

# add a test endpoint that just prints the payload it received.
@app.route('/test', methods=['POST'])
def test():
    """Test endpoint"""
    data = request.get_json()
    print(f"Received data: {data}")
    print(f'data.key: {data.keys()}')
    return jsonify({'status': 'received'}), 200

@app.route('/script', methods=['POST'])
def add_script():
    """Add an script link to a given file name"""
    data = request.get_json()
    print(f"Received data: {data}")
    if not data or 'filename' not in data or 'voiceoverPrompt' not in data:
        return jsonify({'error': 'Missing "filename" or "script" in request body'}), 400
    
    filename = data['filename']
    script = data['voiceoverPrompt']
    description = data['imagePrompt']
    
    # Add the script link to the file
    with open(filename, 'a+') as f:
        f.write(f"{script}\n---END OF SCRIPT---\n")

    # return the description upon success
    return jsonify({'status': 'Script added', 'description': description}), 200

    
# add a new endpoint "/image" which adds an image link to a given file name
@app.route('/image', methods=['POST'])
def add_image():
    """Add an image link to a given file name"""
    data = request.get_json()
    print(f"Received data: {data}")
    # return jsonify({'status': 'Image added'}), 200
    if not data or 'filename' not in data or 'image_url' not in data:
        return jsonify({'error': 'Missing "filename" or "image_url" in request body'}), 400
    
    filename = data['filename']
    image_url = data['image_url']
    
    # Add the image link to the file
    with open(filename, 'a+') as f:
        f.write(f"{image_url}\n")
    
    return jsonify({'status': 'Image added'}), 200

def parse_script_file(filename):
    """
    Parse a file with format:
    <Script for image 1>
    ---END OF SCRIPT---
    image 1 link
    <Script for image 2>
    ---END OF SCRIPT---
    image 2 link
    ...
    
    Returns: list of tuples (script_text, image_url)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found")
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    results = []
    current_script = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is the end marker
        if line == '---END OF SCRIPT---':
            # The script is everything before this marker
            script_text = '\n'.join(current_script).strip()
            current_script = []
            
            # The next non-empty line should be the image URL
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i < len(lines):
                image_url = lines[i].strip()
                if script_text and image_url:
                    results.append((script_text, image_url))
        else:
            # Accumulate script lines
            current_script.append(line)
        
        i += 1
    
    return results

def parse_scripts_only(filename):
    """
    Parse a file with format:
    <Script for image 1>
    ---END OF SCRIPT---
    image 1 link
    <Script for image 2>
    ---END OF SCRIPT---
    image 2 link
    ...
    
    Returns: list of script texts only (ignores image URLs)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found")
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    scripts = []
    current_script = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is the end marker
        if line == '---END OF SCRIPT---':
            # The script is everything before this marker
            script_text = '\n'.join(current_script).strip()
            current_script = []
            
            if script_text:
                scripts.append(script_text)
        else:
            # Accumulate script lines
            current_script.append(line)
        
        i += 1
    
    return scripts

def generate_audio_files(scripts, voice_id="JBFqnCBsd6RMkjVDRZzb", model_id="eleven_multilingual_v2"):
    """
    Generate audio files from scripts using ElevenLabs.
    Returns: list of audio file paths (audio_1.mp3, audio_2.mp3, ...)
    """
    api_key = os.environ.get("ELEVENLABS_KEY")
    # portugese
    voice_id = "IpCcRCVYm2nsZJjBFn4H"
    # argentine
    # voice_id = "QK4xDwo9ESPHA4JNUpX3"
    # uk younger
    # voice_id = "AmY1pcgcEc15wyuIj50p"
    # northern uk (slightly enthusiastic)
    # voice_id = "49TtX0KZLnuzDrAizTkN"
    # geroge uk default
    # voice_id = "JBFqnCBsd6RMkjVDRZzb"
    # hyper guy
    # voice_id = "QvlD90AkjGTCqc9685Rq"

    if not api_key:
        raise ValueError("ELEVENLABS_KEY environment variable is not set")
    
    client = ElevenLabs(api_key=api_key)
    audio_files = []

    
    for idx, script in enumerate(scripts, start=1):
        print(f"Generating audio {idx}/{len(scripts)}...")
        audio = client.text_to_speech.convert(
            text=script,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128",
        )
        
        audio_filename = f"audio_{idx}.mp3"
        with open(audio_filename, "wb") as f:
            f.write(b"".join(audio))
        
        audio_files.append(audio_filename)
        sleep(30)
        print(f"Saved {audio_filename}")
    
    return audio_files

def download_image(url, output_filename):
    """Download an image from URL to local file."""
    import urllib.request
    from urllib.error import HTTPError, URLError

    print(f"Downloading image from {url} to {output_filename}...")
    try:
        # Some CDNs return 403 without a browser-like User-Agent
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/122.0.0.0 Safari/537.36"
            },
        )
        with urllib.request.urlopen(req) as resp, open(output_filename, "wb") as out_f:
            out_f.write(resp.read())
        print(f"Downloaded {output_filename}")
    except HTTPError as e:
        print(f"download_image failed with HTTPError {e.code}: {e.reason}")
        raise
    except URLError as e:
        print(f"download_image failed with URLError: {e.reason}")
        raise

def find_existing_files(expected_count, prefix, extension):
    """
    Find existing files matching pattern {prefix}_{number}.{extension}
    Returns: list of file paths in order (image_1.png, image_2.png, ...)
    """
    existing_files = []
    for i in range(1, expected_count + 1):
        filename = f"{prefix}_{i}.{extension}"
        if os.path.exists(filename):
            existing_files.append(filename)
        else:
            # If any file is missing, return empty list
            return []
    return existing_files

def create_video_from_audio_and_images(audio_files, image_files, output_filename="final_movie.mp4", fps=24):
    """
    Create a video where each image is displayed for the duration of its corresponding audio.
    audio_files and image_files should be lists of file paths in matching order.
    Images are resized to fill the screen while maintaining 9:16 aspect ratio.
    """
    if len(audio_files) != len(image_files):
        raise ValueError(f"Mismatch: {len(audio_files)} audio files but {len(image_files)} image files")
    
    # Target video size for 9:16 aspect ratio (portrait)
    # Using 1080x1920 (Full HD portrait) - common for vertical videos
    target_width = 1080
    target_height = 1920
    
    video_clips = []
    audio_clips = []
    
    for audio_path, image_path in zip(audio_files, image_files):
        # Get audio duration
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        print(f"Processing: image={os.path.basename(image_path)}, audio={os.path.basename(audio_path)}, duration={audio_duration:.2f}s")
        
        # Create ImageClip with duration matching audio
        image_clip = ImageClip(image_path).with_duration(audio_duration)
        
        # Resize image to fill the target size (1080x1920 for 9:16) while maintaining aspect ratio
        # Strategy: Scale to fill the larger dimension, then crop to exact size
        img_w, img_h = image_clip.size
        
        # Calculate scale factors for both dimensions
        scale_w = target_width / img_w
        scale_h = target_height / img_h
        
        # Use the larger scale factor to ensure the image fills the frame
        scale = max(scale_w, scale_h)
        
        # Resize using the scale factor
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        image_clip = image_clip.resized((new_w, new_h))
        
        # Crop to exact target size from center
        x_center = new_w / 2
        y_center = new_h / 2
        image_clip = image_clip.cropped(x_center=x_center, y_center=y_center, width=target_width, height=target_height)
        
        video_clips.append(image_clip)
        audio_clips.append(audio_clip)
    
    # Concatenate all video clips with explicit size
    print("Concatenating video clips...")
    final_video = concatenate_videoclips(video_clips, method="compose")#, size=(target_width, target_height))
    
    # Concatenate all audio clips
    print("Concatenating audio clips...")
    final_audio = concatenate_audioclips(audio_clips)
    
    # Set the audio of the video clip
    print("Combining video and audio...")
    final_clip = final_video.with_audio(final_audio)
    
    # Write the result to a file
    print(f"Writing final movie to {output_filename}...")
    final_clip.write_videofile(output_filename, fps=fps, codec="libx264", audio_codec="aac")
    
    # Clean up
    final_video.close()
    final_audio.close()
    final_clip.close()
    for clip in audio_clips:
        clip.close()
    
    print(f"Movie saved as {output_filename}")
    # Rename myFile.txt to myFile2.txt
    os.rename('myFile.txt', 'myFile2.txt')
    return output_filename

# add a new endpoint "/video" which is a POST endpoint which takes a file name and generates a video from the images in the file.
@app.route('/video', methods=['POST'])
def generate_video():
    """Generate a video from a given file name"""
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        if not data or 'title' not in data:
            return jsonify({'error': 'Missing "title" in request body'}), 400
        
        title = data['title']
        image_source = data.get('imageSource', 'remote')  # Default to 'remote' if not specified
        
        filename = 'myFile.txt'
        
        # If imageSource is "local", only parse scripts and use local images
        if image_source == 'local':
            print("Using local images - parsing scripts only...")
            scripts = parse_scripts_only(filename)
            
            if not scripts:
                return jsonify({'error': 'No scripts found in file'}), 400
            
            print(f"Found {len(scripts)} scripts")
            
            # Find all local images (image_1.png, image_2.png, etc.)
            # Count how many exist starting from 1
            local_images = []
            idx = 1
            while True:
                image_filename = f"image_{idx}.png"
                if os.path.exists(image_filename):
                    local_images.append(image_filename)
                    idx += 1
                else:
                    break
            
            print(f"Found {len(local_images)} local image files")
            
            # Validate that # of scripts == # of local images
            if len(scripts) != len(local_images):
                return jsonify({
                    'error': f'Mismatch: {len(scripts)} scripts but {len(local_images)} local images found'
                }), 400
            
            image_files = local_images
            expected_count = len(scripts)
            
            # Check for existing audio files
            print("Checking for existing audio files...")
            existing_audios = find_existing_files(expected_count, "audio", "mp3")
            
            if existing_audios and len(existing_audios) == expected_count:
                print(f"Found {len(existing_audios)} existing audio files. Using them...")
                audio_files = existing_audios
            else:
                print("Existing audio files not found or don't match. Generating...")
                # Generate audio files from scripts
                audio_files = generate_audio_files(scripts)
        
        else:
            # Original logic: parse scripts and image URLs
            print("Using remote images - parsing scripts and image URLs...")
            script_image_pairs = parse_script_file(filename)
            
            if not script_image_pairs:
                return jsonify({'error': 'No script-image pairs found in file'}), 400
            
            print(f"Found {len(script_image_pairs)} script-image pairs")
            
            expected_count = len(script_image_pairs)
            
            # Check for existing image and audio files
            print("Checking for existing image and audio files...")
            existing_images = find_existing_files(expected_count, "image", "png")
            existing_audios = find_existing_files(expected_count, "audio", "mp3")
            
            if existing_images and existing_audios and len(existing_images) == len(existing_audios) == expected_count:
                print(f"Found {len(existing_images)} existing image files and {len(existing_audios)} existing audio files. Using them...")
                image_files = existing_images
                audio_files = existing_audios
            else:
                print("Existing files not found or don't match. Generating/downloading...")
                # Extract scripts and image URLs
                scripts = [pair[0] for pair in script_image_pairs]
                image_urls = [pair[1] for pair in script_image_pairs]
                
                # Generate audio files from scripts
                print("Generating audio files...")
                audio_files = generate_audio_files(scripts)
                
                # Download images
                print("Downloading images...")
                image_files = []
                for idx, url in enumerate(image_urls, start=1):
                    image_filename = f"image_{idx}.png"
                    download_image(url, image_filename)
                    image_files.append(image_filename)
        
        # Create video from audio and images
        output_video = data.get('output_filename', 'final_movie.mp4')
        print("Creating video...")
        video_filename = create_video_from_audio_and_images(audio_files, image_files, output_video)
        
        return jsonify({
            'status': 'success',
            'message': 'Video generated successfully',
            'filename': video_filename
        }), 200
        
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# add a new endpoint which returns the get

if __name__ == '__main__':
    print("Starting Flask server...")
    print("API endpoint: POST http://localhost:5000/generateImage")
    print("Example request body: {\"prompt\": \"A beautiful sunset over mountains\"}")
    app.run(debug=True, port=5000)

