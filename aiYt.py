import os
from google import genai
from PIL import Image

# 1. SETUP
# Replace with your actual API key or set it as an environment variable
API_KEY = os.environ["GEMINI_KEY"]

client = genai.Client(api_key=API_KEY)

# 2. DEFINE PROMPT
# prompt = "A German Shepherd dog winning a boxing match, wearing boxing gloves, raising paws in victory, cinematic lighting, highly detailed, photorealistic, 8k"
# prompt="Alphonso Davies, full of joy, raises his arms in triumph on a soccer pitch, surrounded by celebrating teammates. The stadium lights shine brightly, highlighting the exhilaration of qualifying for the World Cup after a long absence. Make it cartoon themed"
prompt = "Alphonso Davies stands on the penalty spot, his head slightly bowed, a look of profound disappointment on his face. The stadium lights illuminate the scene, emphasizing the weight of the missed opportunity in Canada's opening World Cup match. Make it cartoon themed"

print("Generating image with Nano Banana (Gemini 2.5 Flash Image)...")

# 3. CALL THE MODEL
# "Nano Banana" is the nickname for 'gemini-2.5-flash-image'
response = client.models.generate_content(
    # model="gemini-2.5-flash-image",
    model="gemini-3-pro-image-preview",
    contents=[prompt]
)

import pdb
pdb.set_trace()

# 4. SAVE THE IMAGE
# The model returns the image within the response parts
if response.parts:
    for part in response.parts:
        if part.inline_data:
            # The SDK provides a helper to convert the raw data to a PIL Image
            image = part.as_image()
            image.save("davies.png")
            print("Success! Image saved as 'german_shepherd_boxing.png'")
else:
    print("No image generated. Check your prompt or API quota.")

docker volume create n8n_data

docker run -it --rm \
 --name n8n \
 -p 5678:5678 \
 -e GENERIC_TIMEZONE="America/Los_Angeles" \
 -e TZ="America/Los_Angeles" \
 -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
 -e N8N_RUNNERS_ENABLED=true \
 -v n8n_data:/home/node/.n8n \
 docker.n8n.io/n8nio/n8n