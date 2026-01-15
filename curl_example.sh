#!/bin/bash

# Example curl command to generate an image using Gemini 3 Pro Image Preview
# Replace YOUR_API_KEY with your actual GEMINI_KEY

API_KEY="${GEMINI_KEY:-YOUR_API_KEY}"
PROMPT="Alphonso Davies stands on the penalty spot, his head slightly bowed, a look of profound disappointment on his face. The stadium lights illuminate the scene, emphasizing the weight of the missed opportunity in Canada's opening World Cup match. Make it cartoon themed"

curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [{
        \"text\": \"${PROMPT}\"
      }]
    }]
  }" \
  -o response.json

# The response will contain base64-encoded image data
# You'll need to parse the JSON and extract/decode the image data
echo "Response saved to response.json"
echo "You'll need to parse the JSON response to extract the base64 image data"
