# 📚 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. For production, implement JWT tokens.

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running and all services are operational.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "nlp": true,
    "image": true,
    "voice": true,
    "translation": true
  }
}
```

---

### 2. Chat

**POST** `/api/chat`

Send a message to the chatbot and receive a response.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "user_id": "user123",
  "personality_mode": "friendly",
  "auto_translate": false,
  "context": []
}
```

**Parameters:**
- `message` (required): User's message
- `user_id` (optional): Unique user identifier, default: "anonymous"
- `personality_mode` (optional): "friendly", "professional", or "creative", default: "friendly"
- `auto_translate` (optional): Enable auto-translation, default: false
- `context` (optional): Previous conversation history

**Response:**
```json
{
  "response": "Hello! I'm doing great, thank you! How can I help you today? 😊",
  "personality_mode": "friendly",
  "detected_language": "en",
  "confidence": 0.95,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me a joke",
    "personality_mode": "friendly"
  }'
```

---

### 3. Image Generation

**POST** `/api/generate-image`

Generate images from text descriptions using Stable Diffusion.

**Request Body:**
```json
{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blurry, distorted",
  "width": 512,
  "height": 512,
  "num_steps": 20,
  "user_id": "user123"
}
```

**Parameters:**
- `prompt` (required): Image description
- `negative_prompt` (optional): Things to avoid
- `width` (optional): Image width, default: 512
- `height` (optional): Image height, default: 512
- `num_steps` (optional): Inference steps (10-50), default: 20
- `user_id` (optional): User identifier

**Response:**
Returns PNG image data (binary)

**Example:**
```bash
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a futuristic city at night",
    "width": 512,
    "height": 512
  }' \
  --output generated_image.png
```

---

### 4. Speech to Text

**POST** `/api/speech-to-text`

Convert audio/voice messages to text using Whisper.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Audio file

**Query Parameters:**
- `language` (optional): Language code (e.g., "en", "es"), default: "en"

**Response:**
```json
{
  "text": "This is the transcribed text from the audio",
  "language": "en"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/speech-to-text?language=en \
  -F "audio=@voice_message.mp3"
```

---

### 5. Text to Speech

**POST** `/api/text-to-speech`

Convert text to speech audio using gTTS.

**Query Parameters:**
- `text` (required): Text to convert
- `language` (optional): Language code, default: "en"
- `slow` (optional): Speak slowly, default: false

**Response:**
Returns MP3 audio data (binary)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/text-to-speech?text=Hello%20World&language=en" \
  --output speech.mp3
```

---

### 6. Translation

**POST** `/api/translate`

Translate text between languages.

**Query Parameters:**
- `text` (required): Text to translate
- `target_language` (required): Target language code
- `source_language` (optional): Source language or "auto", default: "auto"

**Response:**
```json
{
  "original": "Hello, how are you?",
  "translated": "Hola, ¿cómo estás?",
  "source_language": "en",
  "target_language": "es"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/translate?text=Hello&target_language=es&source_language=en"
```

---

### 7. Get Supported Languages

**GET** `/api/languages`

Get list of supported languages for translation.

**Response:**
```json
{
  "languages": {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    ...
  }
}
```

---

### 8. Switch Personality

**POST** `/api/personality`

Get information about a personality mode.

**Request Body:**
```json
"friendly"
```

**Response:**
```json
{
  "mode": "friendly",
  "description": "Warm, casual, and engaging. Uses emojis and friendly language.",
  "sample_response": "Hey there! I'm here to help and chat! What's on your mind today? 😊"
}
```

---

### 9. Analytics

**GET** `/api/analytics`

Get usage analytics and statistics.

**Query Parameters:**
- `user_id` (optional): Filter by specific user
- `days` (optional): Number of days to include, default: 7

**Response:**
```json
{
  "total_conversations": 150,
  "total_messages": 450,
  "total_images_generated": 25,
  "active_users": 30,
  "popular_personality": "friendly",
  "language_distribution": {
    "en": 120,
    "es": 20,
    "fr": 10
  },
  "daily_stats": [
    {
      "date": "2024-01-15",
      "conversations": 25,
      "messages": 75,
      "images": 5,
      "active_users": 10
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/analytics?days=7
```

---

## Error Handling

All endpoints return errors in the following format:

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

Currently no rate limiting. For production:
- Implement rate limiting per user
- Suggested: 60 requests/minute for chat
- 10 requests/minute for image generation

---

## WebSocket Support (Future)

For real-time streaming responses:
```
ws://localhost:8000/ws/chat
```

---

## Usage Examples

### Python Client

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "Hello!",
        "personality_mode": "friendly"
    }
)
print(response.json())

# Generate Image
response = requests.post(
    "http://localhost:8000/api/generate-image",
    json={
        "prompt": "a sunset",
        "width": 512,
        "height": 512
    }
)
with open("image.png", "wb") as f:
    f.write(response.content)
```

### JavaScript Client

```javascript
// Chat
const chatResponse = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello!',
    personality_mode: 'friendly'
  })
});
const data = await chatResponse.json();
console.log(data.response);

// Generate Image
const imageResponse = await fetch('http://localhost:8000/api/generate-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'a sunset',
    width: 512,
    height: 512
  })
});
const blob = await imageResponse.blob();
const imageUrl = URL.createObjectURL(blob);
```

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- Test all endpoints
- See request/response schemas
- Try different parameters
- View examples

Alternative: `http://localhost:8000/redoc` for ReDoc documentation.
