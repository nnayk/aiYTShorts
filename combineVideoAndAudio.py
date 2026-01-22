from moviepy import VideoFileClip, AudioFileClip

# Load the video clip and the new audio clip
video_clip = VideoFileClip("my_slideshow.mp4")
audio_clip = AudioFileClip("final_audio.mp3")

# Set the audio of the video clip to the new audio clip
# The new audio will be automatically cut to the video's duration
final_clip = video_clip.with_audio(audio_clip)

# Write the result to a new file
final_clip.write_videofile("output_with_new_audio.mp4", codec="libx264", audio_codec="aac")
