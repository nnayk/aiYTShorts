import os
import re
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# --- Configuration ---
image_folder = '.'  # Current directory
audio_folder = '.'  # Current directory
output_file = 'final_movie.mp4'
fps = 24  # Frames per second for the video

def extract_number(filename):
    """Extract number from filename like audio_1.mp3 or image_1.png"""
    match = re.search(r'_(\d+)\.', filename)
    if match:
        return int(match.group(1))
    return None

def get_audio_duration(audio_path):
    """Get the duration of an audio file in seconds"""
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()
    return duration

def create_movie():
    # 1. Find all audio files matching audio_{number}.mp3 pattern
    audio_files = {}
    for file in os.listdir(audio_folder):
        if file.startswith('audio_') and file.endswith('.mp3'):
            number = extract_number(file)
            if number is not None:
                audio_files[number] = os.path.join(audio_folder, file)
    
    if not audio_files:
        print("No audio files found matching pattern audio_{number}.mp3")
        return
    
    print(f"Found {len(audio_files)} audio files")
    print(f'audio_files: {audio_files}')
    
    # 2. Find corresponding PNG files and match them with audio files
    png_files = {}
    for file in os.listdir(image_folder):
        if file.endswith('.png'):
            print(f"file: {file}")
            number = extract_number(file)
            print(f"number: {number}")
            if number is not None and number in audio_files:
                png_files[number] = os.path.join(image_folder, file)
    
    if not png_files:
        print("No PNG files found matching the audio file numbers")
        return
    
    # 3. Sort by number to ensure correct order
    sorted_numbers = sorted(set(audio_files.keys()) & set(png_files.keys()))
    
    if not sorted_numbers:
        print("No matching audio and PNG file pairs found")
        return
    
    print(f"Found {len(sorted_numbers)} matching audio-PNG pairs")
    
    # 4. Create video clips with durations matching audio durations
    video_clips = []
    audio_clips = []
    
    for number in sorted_numbers:
        audio_path = audio_files[number]
        image_path = png_files[number]
        
        # Get audio duration
        audio_duration = get_audio_duration(audio_path)
        print(f"Processing pair {number}: image={os.path.basename(image_path)}, audio={os.path.basename(audio_path)}, duration={audio_duration:.2f}s")
        
        # Create ImageClip with duration matching audio
        image_clip = ImageClip(image_path).with_duration(audio_duration)
        video_clips.append(image_clip)
        
        # Load audio clip
        audio_clip = AudioFileClip(audio_path)
        audio_clips.append(audio_clip)
    
    # 5. Concatenate all video clips
    print("Concatenating video clips...")
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    # 6. Concatenate all audio clips
    print("Concatenating audio clips...")
    final_audio = concatenate_audioclips(audio_clips)
    
    # 7. Set the audio of the video clip
    print("Combining video and audio...")
    final_clip = final_video.with_audio(final_audio)
    
    # 8. Write the result to a file
    print(f"Writing final movie to {output_file}...")
    final_clip.write_videofile(output_file, fps=fps, codec="libx264", audio_codec="aac")
    
    # Clean up
    final_video.close()
    final_audio.close()
    final_clip.close()
    for clip in audio_clips:
        clip.close()
    
    print(f"Movie saved as {output_file}")

if __name__ == '__main__':
    create_movie()
