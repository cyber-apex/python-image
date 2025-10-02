from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import os
import random
import hashlib

app = Flask(__name__)
CORS(app)

def generate_color_from_text(text):
    """Generate a consistent color based on text hash"""
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    r = int(hash_hex[0:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)
    return (r, g, b)

def create_placeholder_image(text, width=900, height=1200):
    """Create a placeholder image with the given text"""
    # Generate background color from text
    bg_color = generate_color_from_text(text)
    
    # Create image
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Add gradient effect
    for i in range(height):
        alpha = i / height
        darker = tuple(int(c * (1 - alpha * 0.3)) for c in bg_color)
        draw.line([(0, i), (width, i)], fill=darker)
    
    # Load font with CJK support
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_paths = [
        os.path.join(font_dir, "NotoSansSC-Bold.otf"),  # Noto Sans SC (Simplified Chinese)
        os.path.join(font_dir, "NotoSansJP-Bold.otf"),  # Noto Sans JP (Japanese)
    ]
    
    # Function to load font with specific size
    def load_font(size):
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        return ImageFont.load_default()
    
    # Function to wrap text to fit width
    def wrap_text(text, font, max_width):
        lines = []
        # Split by existing newlines first
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph:
                lines.append('')
                continue
                
            # For CJK text, we can break at any character
            # For mixed text, try to break at spaces when possible
            current_line = ''
            for char in paragraph:
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
                
                if line_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            
            if current_line:
                lines.append(current_line)
        
        return lines
    
    # Calculate appropriate font size and wrap text
    padding = int(min(width, height) * 0.08)  # 8% padding
    max_text_width = width - padding * 2
    max_text_height = height - padding * 2
    
    # Start with a reasonable font size and adjust
    font_size = int(min(width, height) * 0.15)  # Start with 15% of smallest dimension
    best_font_size = font_size
    
    for attempt in range(10):  # Try up to 10 times to find good size
        font = load_font(font_size)
        lines = wrap_text(text, font, max_text_width)
        
        # Calculate total text dimensions
        text_content = '\n'.join(lines)
        bbox = draw.textbbox((0, 0), text_content, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Check if text fits
        if text_width <= max_text_width and text_height <= max_text_height:
            best_font_size = font_size
            break
        else:
            # Reduce font size
            font_size = int(font_size * 0.85)
            if font_size < 12:  # Minimum font size
                font_size = 12
                break
    
    # Use the best font size found
    font = load_font(best_font_size)
    lines = wrap_text(text, font, max_text_width)
    text_content = '\n'.join(lines)
    
    # Calculate final text position (centered)
    bbox = draw.textbbox((0, 0), text_content, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text with shadow for better visibility
    shadow_color = (0, 0, 0)
    draw.text((x + 2, y + 2), text_content, font=font, fill=shadow_color)
    draw.text((x, y), text_content, font=font, fill=(255, 255, 255))
    
    return image

@app.route('/')
def home():
    return jsonify({
        "message": "Placeholder Image Generator API",
        "endpoints": {
            "/placeholder": "POST - Generate placeholder image from text",
            "/health": "GET - Health check"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/placeholder', methods=['GET'])
def generate_image():
    try:
        # Get the text prompt from query parameters
        prompt = request.args.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' query parameter"}), 400
        
        width = int(request.args.get('width', 900))
        height = int(request.args.get('height', 1200))
        
        # Validate dimensions
        if width > 2000 or height > 2000:
            return jsonify({"error": "Maximum dimensions are 2000x2000"}), 400
        
        print(f"Generating placeholder image for: {prompt}")
        
        # Generate the placeholder image
        image = create_placeholder_image(prompt, width, height)
        
        # Save image to bytes buffer
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        # Option 1: Return as file
        if request.args.get('return_file', 'true').lower() == 'true':
            return send_file(img_buffer, mimetype='image/jpeg')
        
        # Option 2: Return as base64 (default)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "dimensions": {"width": width, "height": height},
            "image": f"data:image/jpeg;base64,{img_base64}"
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5566))
    app.run(host='0.0.0.0', port=port, debug=True)

