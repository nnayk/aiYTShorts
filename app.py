import os
import subprocess
from flask import Flask, request, jsonify
from google import genai
from PIL import Image
from datetime import datetime

app = Flask(__name__)

# Setup Gemini client
API_KEY = os.environ.get("GEMINI_KEY")
if not API_KEY:
    raise ValueError("GEMINI_KEY environment variable is not set")

client = genai.Client(api_key=API_KEY)

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
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing "prompt" in request body'}), 400
        
        prompt = data['prompt']
        
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

if __name__ == '__main__':
    print("Starting Flask server...")
    print("API endpoint: POST http://localhost:5000/generateImage")
    print("Example request body: {\"prompt\": \"A beautiful sunset over mountains\"}")
    app.run(debug=True, port=5000)
