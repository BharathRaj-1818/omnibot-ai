# 🧪 Testing Guide

## Pre-Deployment Testing Checklist

### 1. Backend API Tests

#### Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status": "healthy", "services": {...}}`

#### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "personality_mode": "friendly"
  }'
```
**Expected:** JSON response with bot reply

#### Personality Modes
Test all three personalities:
- friendly: Casual, uses emojis
- professional: Formal tone
- creative: Imaginative responses

```bash
# Test each mode
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about AI", "personality_mode": "professional"}'
```

#### Image Generation (if GPU available)
```bash
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset",
    "width": 512,
    "height": 512
  }' \
  --output test_image.png
```

#### Translation
```bash
curl -X POST "http://localhost:8000/api/translate?text=Hello&target_language=es&source_language=en"
```
**Expected:** Translated text in Spanish

#### Analytics
```bash
curl http://localhost:8000/api/analytics
```
**Expected:** Statistics about usage

---

### 2. Frontend Tests

#### Open Web Interface
1. Navigate to `http://localhost:3000`
2. **Check:** Page loads without errors

#### Basic Chat
1. Type "Hello" and press Enter
2. **Check:** Bot responds within 3 seconds
3. **Check:** Message appears in chat

#### Personality Switching
1. Click each personality button (Friendly, Professional, Creative)
2. Send same message with each personality
3. **Check:** Responses have different tones

#### Image Generation
1. Click image icon
2. Enter prompt: "a sunset over mountains"
3. **Check:** Image generates and displays

#### Voice Input (Chrome/Edge only)
1. Click microphone icon
2. Allow microphone access
3. Speak a message
4. **Check:** Speech is transcribed and sent

#### Settings
1. Click settings icon
2. Toggle auto-translate
3. **Check:** Setting is saved

#### Analytics
1. Click analytics icon
2. **Check:** Statistics display correctly

---

### 3. Platform Bot Tests

#### Telegram Bot

**Setup:**
```bash
cd bots/telegram
python bot.py
```

**Tests:**
1. Search for your bot on Telegram
2. Send `/start`
   - **Check:** Welcome message appears
3. Send `/friendly`
   - **Check:** Personality switches
4. Send `Hello!`
   - **Check:** Bot responds in friendly mode
5. Send `/image sunset`
   - **Check:** Image generates and sends
6. Send `/help`
   - **Check:** Help message displays

**Voice Test:**
1. Send a voice message
2. **Check:** Bot transcribes and responds

#### Discord Bot

**Setup:**
```bash
cd bots/discord
python bot.py
```

**Tests:**
1. Invite bot to your server
2. Send `!start`
   - **Check:** Welcome embed appears
3. Mention bot: `@YourBot hello`
   - **Check:** Bot responds
4. Send `!friendly`
   - **Check:** Mode switches
5. Send `!image sunset`
   - **Check:** Image generates
6. Send `!stats`
   - **Check:** Statistics display

---

### 4. Error Handling Tests

#### Invalid Input
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{}'
```
**Expected:** Error message about missing fields

#### Invalid Personality
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "test",
    "personality_mode": "invalid"
  }'
```
**Expected:** Defaults to "friendly" mode

#### Long Messages
Test with 1000+ character message
**Expected:** Handles gracefully

---

### 5. Performance Tests

#### Response Time
- **Chat:** Should respond in < 2 seconds
- **Image:** Should generate in < 30 seconds
- **Translation:** Should translate in < 1 second

#### Concurrent Users
Open 5 browser tabs and send messages simultaneously
**Expected:** All receive responses

#### Memory Usage
Monitor backend memory while running
**Expected:** Stable memory usage

---

### 6. Cross-Browser Tests

Test web interface on:
- ✅ Chrome
- ✅ Firefox
- ✅ Safari
- ✅ Edge

**Check:**
- Layout renders correctly
- Voice input works (Chrome/Edge)
- All features functional

---

### 7. Mobile Tests

Test on mobile devices:
- Responsive design
- Touch interactions
- Platform bots (Telegram/Discord apps)

---

## Common Issues & Fixes

### Issue: "Port already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows
```

### Issue: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Models downloading slowly
- First run downloads ~1-2GB of models
- They're cached for future use
- Be patient!

### Issue: Image generation fails
- Requires GPU or will be very slow on CPU
- Fallback to placeholder images available

### Issue: Bot not responding
- Check .env has correct tokens
- Verify backend is running
- Check bot logs for errors

---

## Automated Testing Script

```python
# test_api.py
import requests
import time

API_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_chat():
    response = requests.post(
        f"{API_URL}/api/chat",
        json={"message": "Hello", "personality_mode": "friendly"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
    print("✅ Chat test passed")

def test_personalities():
    for mode in ["friendly", "professional", "creative"]:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"message": "Tell me about AI", "personality_mode": mode}
        )
        assert response.status_code == 200
        print(f"✅ {mode} personality test passed")

def test_analytics():
    response = requests.get(f"{API_URL}/api/analytics")
    assert response.status_code == 200
    print("✅ Analytics test passed")

if __name__ == "__main__":
    print("Starting automated tests...\n")
    
    test_health()
    test_chat()
    test_personalities()
    test_analytics()
    
    print("\n🎉 All tests passed!")
```

Run with: `python test_api.py`

---

## Pre-Submission Checklist

- [ ] All API endpoints working
- [ ] Web interface loads and functions
- [ ] At least one platform bot working (Telegram or Discord)
- [ ] Documentation complete (README, setup guide)
- [ ] Code committed to Git
- [ ] .env.example provided
- [ ] Requirements.txt up to date
- [ ] Screenshots/demo video prepared
- [ ] Presentation slides ready

---

## Performance Benchmarks

**Expected Performance (on average laptop):**

| Feature | CPU Only | With GPU |
|---------|----------|----------|
| Chat Response | 1-2s | 0.5-1s |
| Image Generation | 60-120s | 15-30s |
| Voice STT | 2-3s | 1-2s |
| Translation | 0.5-1s | 0.2-0.5s |

**Memory Usage:**
- Backend: ~2-4 GB (with models loaded)
- Frontend: ~200 MB
- Database: ~10-50 MB

---

## Load Testing (Optional)

```python
# load_test.py
import asyncio
import aiohttp
import time

async def send_message(session, i):
    async with session.post(
        "http://localhost:8000/api/chat",
        json={"message": f"Test message {i}"}
    ) as response:
        return await response.json()

async def load_test(num_requests=100):
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [send_message(session, i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    end = time.time()
    print(f"Completed {num_requests} requests in {end-start:.2f}s")
    print(f"Average: {(end-start)/num_requests:.3f}s per request")

if __name__ == "__main__":
    asyncio.run(load_test(100))
```

---

## Final Verification

Before submission, verify:
1. ✅ Project runs on fresh clone
2. ✅ All dependencies install correctly
3. ✅ Documentation is clear
4. ✅ No hardcoded secrets
5. ✅ Code is well-commented
6. ✅ Git history is clean

**You're ready to submit! 🚀**
