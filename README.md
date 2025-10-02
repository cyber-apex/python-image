# Placeholder Image Generator API

A lightweight Flask server that generates colorful placeholder images from text descriptions using PIL.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### GET `/`
Returns API information and available endpoints.

### GET `/health`
Health check endpoint.

### POST `/generate`
Generate an image from a text prompt.

**Request Body:**
```json
{
  "prompt": "a beautiful sunset over mountains",
  "width": 800,
  "height": 600,
  "return_file": false
}
```

**Parameters:**
- `prompt` (required): Text to display on the placeholder image
- `width` (optional, default: 1200): Image width in pixels (max 2000)
- `height` (optional, default: 1200): Image height in pixels (max 2000)
- `return_file` (optional, default: false): Return image file instead of base64

**Response (base64):**
```json
{
  "success": true,
  "prompt": "a beautiful sunset over mountains",
  "image": "data:image/png;base64,..."
}
```

## Example Usage

### Using curl:
```bash
curl -X POST http://localhost:5000/placeholder \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cute cat wearing a hat"}'
```

### Using Python:
```python
import requests
import base64
from PIL import Image
import io

response = requests.post('http://localhost:5000/placeholder', json={
    'prompt': 'a beautiful landscape with mountains'
})

data = response.json()
img_data = base64.b64decode(data['image'].split(',')[1])
image = Image.open(io.BytesIO(img_data))
image.show()
```

## Notes

- Each text prompt generates a unique color based on the text hash
- Images include a gradient effect and centered text
- Very lightweight - no AI models or heavy dependencies required

