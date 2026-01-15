#!/bin/bash

# Complete curl example to generate an image using Gemini 3 Pro Image Preview
# and save it to a file

# Get API key from environment variable
API_KEY="${GEMINI_KEY}"

if [ -z "$API_KEY" ]; then
    echo "Error: GEMINI_KEY environment variable is not set"
    exit 1
fi

# Prompt (you can modify this or pass as argument)
PROMPT="${1:-Alphonso Davies stands on the penalty spot, his head slightly bowed, a look of profound disappointment on his face. The stadium lights illuminate the scene, emphasizing the weight of the missed opportunity in Canada's opening World Cup match. Make it cartoon themed}"

echo "Generating image with prompt: $PROMPT"

# Make the API request
RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [{
        \"text\": \"${PROMPT}\"
      }]
    }]
  }")

# Save raw response for debugging
echo "$RESPONSE" > response_raw.json

# Extract base64 image data using jq (if available) or Python
if command -v jq &> /dev/null; then
    # Using jq to extract base64 data
    IMAGE_DATA=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].inlineData.data')
    MIME_TYPE=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].inlineData.mimeType')
    
    if [ "$IMAGE_DATA" != "null" ] && [ -n "$IMAGE_DATA" ]; then
        # Determine file extension from MIME type
        if [[ "$MIME_TYPE" == *"png"* ]]; then
            EXT="png"
        elif [[ "$MIME_TYPE" == *"jpeg"* ]] || [[ "$MIME_TYPE" == *"jpg"* ]]; then
            EXT="jpg"
        else
            EXT="png"
        fi
        
        FILENAME="generated_image_$(date +%Y%m%d_%H%M%S).${EXT}"
        echo "$IMAGE_DATA" | base64 -d > "$FILENAME"
        echo "Success! Image saved as '$FILENAME'"
        
        # Open the image (macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$FILENAME"
        fi
    else
        echo "Error: No image data found in response"
        echo "Response: $RESPONSE"
    fi
else
    # Fallback: Use Python to parse and save image
    python3 << EOF
import json
import base64
import sys
from datetime import datetime

try:
    response = json.loads('''$RESPONSE''')
    
    if 'candidates' in response and len(response['candidates']) > 0:
        parts = response['candidates'][0].get('content', {}).get('parts', [])
        for part in parts:
            if 'inlineData' in part:
                image_data = part['inlineData']['data']
                mime_type = part['inlineData'].get('mimeType', 'image/png')
                
                # Determine extension
                if 'png' in mime_type:
                    ext = 'png'
                elif 'jpeg' in mime_type or 'jpg' in mime_type:
                    ext = 'jpg'
                else:
                    ext = 'png'
                
                filename = f"generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                
                # Decode and save
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                
                print(f"Success! Image saved as '{filename}'")
                
                # Open image (macOS)
                import subprocess
                import os
                if os.uname().sysname == 'Darwin':
                    subprocess.run(['open', filename])
                
                sys.exit(0)
    
    print("Error: No image data found in response")
    print(f"Response: {json.dumps(response, indent=2)}")
    sys.exit(1)
except Exception as e:
    print(f"Error parsing response: {e}")
    print(f"Raw response: {response}")
    sys.exit(1)
EOF
fi
