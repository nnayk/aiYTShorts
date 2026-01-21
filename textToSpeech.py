import os
import pdb
# from pydub import AudioSegment
import io

# def textToSpeech(text):
#     # use elevenlabs to convert text to speech
#     import requests
#     url = "https://api.elevenlabs.io/v1/text-to-speech/21r0q3k0115r8111ck01"
#     headers = {
#         "Accept": "audio/mpeg",
#         "Content-Type": "application/json",
#         "xi-api-key": "sk_d9f18142885ee4345340a7a13610a76a3d3fd7b1eb62f937"
#     }
#     data = {
#         "text": text,
#         "model_id": "eleven_monolingual_v1",
#         "voice_settings": {
#             "stability": 0.5,
#             "similarity_boost": 0.5
#         }
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response.content

# data = textToSpeech("Hello World")
# pdb.set_trace()

from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

client = ElevenLabs(
    api_key=os.environ["ELEVENLABS_KEY"]
)

texts = [
    "Morocco was set to host the 2025 Africa Cup of Nations, promising a summer tournament to avoid clashes with club seasons.",
    "But then, FIFA announced its brand new, expanded Club World Cup... scheduled for the exact same time.",
    "This put Africa's biggest stars in an impossible position: choose between their country and their club.",
    "Behind the scenes, tense negotiations began. The football calendar was gridlocked, and something had to give.",
    "For months, fans were left in the dark, with rumors and uncertainty swirling around the tournament's fate.",
    "Finally, the decision was made. The Africa Cup of Nations was officially postponed to early 2026, solving the scheduling crisis."
]

audios = []

import time
for num, text in enumerate(texts):
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    start = time.time()
    # play(audio)
    end = time.time()
    print(f"Time to play audio {num}: {end - start}")
    audios.append(audio)
    with open(f"audio_{num}.mp3", "wb") as f:
        f.write(b"".join(audio))
    pdb.set_trace()

# audio = client.text_to_speech.convert(
#     text="Morocco was set to host the 2025 Africa Cup of Nations, promising a summer tournament to avoid clashes with club seasons.",
#     voice_id="JBFqnCBsd6RMkjVDRZzb",
#     model_id="eleven_multilingual_v2",
#     output_format="mp3_44100_128",
# )
# play(audio)

merged_audio = AudioSegment.empty()


for audio in audios:
    # ElevenLabs returns a generator → convert to bytes
    audio_bytes = b"".join(audio)

    # Load into AudioSegment
    segment = AudioSegment.from_file(
        io.BytesIO(audio_bytes),
        format="mp3"
    )

    merged_audio += segment

# Export final merged file
merged_audio.export("final_audio.mp3", format="mp3")


# merge all audios in audios list into one audio file. keep in mind each audio element is a TextToSpeechClient generator.
