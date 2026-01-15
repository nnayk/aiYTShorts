# Using curl to call Gemini 3 Pro Image Preview API

## Simple curl command

Replace `YOUR_API_KEY` with your actual API key from the `GEMINI_KEY` environment variable:

```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "A beautiful sunset over mountains"
      }]
    }]
  }'
```

## Using environment variable

```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=${GEMINI_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "A beautiful sunset over mountains"
      }]
    }]
  }'
```

## Complete script with image extraction

Use the provided `curl_generate_image.sh` script:

```bash
# Make it executable (if not already)
chmod +x curl_generate_image.sh

# Run with default prompt
./curl_generate_image.sh

# Or with a custom prompt
./curl_generate_image.sh "Your custom prompt here"
```

## Response format

The API returns JSON with the image data in base64 format:

```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "inlineData": {
          "mimeType": "image/png",
          "data": "base64_encoded_image_data_here"
        }
      }]
    }
  }]
}
```

## Extracting and saving the image

### Using jq (if installed):
```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=${GEMINI_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Your prompt"}]}]}' \
  | jq -r '.candidates[0].content.parts[0].inlineData.data' \
  | base64 -d > output.png
```

### Using Python one-liner:
```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=${GEMINI_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Your prompt"}]}]}' \
  | python3 -c "import json, sys, base64; data=json.load(sys.stdin); print(base64.b64decode(data['candidates'][0]['content']['parts'][0]['inlineData']['data']), file=open('output.png','wb'))"
```
