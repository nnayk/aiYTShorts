import os
import subprocess
from flask import Flask, request, jsonify
from google import genai
from PIL import Image
from datetime import datetime

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

# add a new endpoint "/image" which adds an image link to a given file name
@app.route('/image', methods=['POST'])
def add_image():
    """Add an image link to a given file name"""
    data = request.get_json()
    print(f"Received data: {data}")
    if not data or 'filename' not in data or 'image_url' not in data:
        return jsonify({'error': 'Missing "filename" or "image_url" in request body'}), 400
    
    filename = data['filename']
    image_url = data['image_url']
    
    # Add the image link to the file
    with open(filename, 'a+') as f:
        f.write(f"{image_url}\n")
    
    return jsonify({'status': 'Image added'}), 200

# add a new endpoint "/video" which is a POST endpoint which takes a file name and generates a video from the images in the file.
@app.route('/video', methods=['POST'])
def generate_video():
    """Generate a video from a given file name"""
    data = request.get_json()
    print(f"Received data: {data}")
    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing "filename" in request body'}), 400
    
    filename = data['filename']
    
    # Generate the video
    # create_slideshow(filename)
    
    return jsonify({'status': 'Video generated'}), 200

# add a new endpoint which returns the get

if __name__ == '__main__':
    print("Starting Flask server...")
    print("API endpoint: POST http://localhost:5000/generateImage")
    print("Example request body: {\"prompt\": \"A beautiful sunset over mountains\"}")
    app.run(debug=True, port=5000)

