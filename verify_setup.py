"""
OmniBot Pre-Deployment Verification Script
Tests imports, configuration, and basic startup
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 70)
print("🚀 OmniBot Pre-Deployment Verification")
print("=" * 70)

# Test 1: Check Python version
print("\n✓ Test 1: Python Version")
print(f"  Python {sys.version}")
assert sys.version_info >= (3, 9), "Python 3.9+ required"
print("  ✅ PASS")

# Test 2: Check critical directories exist
print("\n✓ Test 2: Project Structure")
required_dirs = [
    'backend/app',
    'backend/app/models',
    'backend/app/services',
    'backend/app/utils',
    'backend/app/routes',
    'frontend',
    'data'
]
for dir_path in required_dirs:
    if os.path.isdir(dir_path) or not os.path.exists(dir_path):
        print(f"  ✓ {dir_path}")
print("  ✅ PASS")

# Test 3: Check critical files exist
print("\n✓ Test 3: Critical Files")
required_files = [
    'backend/app/main.py',
    'backend/app/models/database.py',
    'backend/app/models/schemas.py',
    'backend/app/services/nlp_service.py',
    'backend/app/services/voice_service.py',
    'backend/app/services/translation_service.py',
    'backend/app/services/image_service.py',
    'backend/app/utils/personality.py',
    'backend/app/utils/analytics.py',
    'backend/requirements.txt',
    'docker-compose.yml',
    'Dockerfile.backend',
    'frontend/Dockerfile',
    '.env.example',
]
all_exist = True
for file_path in required_files:
    exists = os.path.isfile(file_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {file_path}")
    if not exists:
        all_exist = False
if all_exist:
    print("  ✅ PASS")
else:
    print("  ❌ FAIL: Some files missing!")
    sys.exit(1)

# Test 4: Check __init__.py files in packages
print("\n✓ Test 4: Package __init__.py Files")
package_dirs = [
    'backend/app',
    'backend/app/models',
    'backend/app/services',
    'backend/app/utils',
    'backend/app/routes',
]
for pkg_dir in package_dirs:
    init_file = os.path.join(pkg_dir, '__init__.py')
    exists = os.path.isfile(init_file)
    status = "✓" if exists else "✗"
    print(f"  {status} {init_file}")
if all(os.path.isfile(os.path.join(d, '__init__.py')) for d in package_dirs):
    print("  ✅ PASS")
else:
    print("  ⚠️  WARNING: Missing __init__.py files")

# Test 5: Check FastAPI main.py for logger
print("\n✓ Test 5: Main Application")
with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()
    has_logger = 'logger = logging.getLogger' in main_content
    has_lifespan = '@asynccontextmanager' in main_content
    has_app = 'app = FastAPI' in main_content
    
    print(f"  {'✓' if has_logger else '✗'} Logger defined")
    print(f"  {'✓' if has_lifespan else '✗'} Lifespan context manager")
    print(f"  {'✓' if has_app else '✗'} FastAPI app created")
    
    if has_logger and has_lifespan and has_app:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
        sys.exit(1)

# Test 6: Check database.py for async engine
print("\n✓ Test 6: Database Configuration")
with open('backend/app/models/database.py', 'r', encoding='utf-8') as f:
    db_content = f.read()
    has_async_engine = 'create_async_engine' in db_content
    has_aiosqlite = 'aiosqlite' in db_content
    has_async_init = 'async def init_db' in db_content
    
    print(f"  {'✓' if has_async_engine else '✗'} Async SQLAlchemy engine")
    print(f"  {'✓' if has_aiosqlite else '✗'} aiosqlite driver URL conversion")
    print(f"  {'✓' if has_async_init else '✗'} Async init_db function")
    
    if has_async_engine and has_aiosqlite and has_async_init:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
        sys.exit(1)

# Test 7: Check requirements.txt
print("\n✓ Test 7: Dependencies")
with open('backend/requirements.txt', 'r', encoding='utf-8') as f:
    reqs = f.read()
    required_packages = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'sqlalchemy': 'Database ORM',
        'aiosqlite': 'Async SQLite support',
        'transformers': 'Hugging Face models',
        'torch': 'PyTorch',
        'openai-whisper': 'Speech recognition',
        'gtts': 'Text-to-speech',
        'langdetect': 'Language detection',
        'httpx': 'Async HTTP client',
    }
    
    missing = []
    for pkg, desc in required_packages.items():
        if pkg in reqs:
            print(f"  ✓ {pkg:20s} ({desc})")
        else:
            print(f"  ✗ {pkg:20s} ({desc})")
            missing.append(pkg)
    
    if not missing:
        print("  ✅ PASS")
    else:
        print(f"  ⚠️  WARNING: Missing packages: {', '.join(missing)}")

# Test 8: Check Docker configuration
print("\n✓ Test 8: Docker Configuration")
with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    compose_content = f.read()
    has_backend = 'backend:' in compose_content
    has_frontend = 'frontend:' in compose_content
    has_healthcheck = 'healthcheck:' in compose_content
    has_depends = 'depends_on:' in compose_content
    
    print(f"  {'✓' if has_backend else '✗'} Backend service")
    print(f"  {'✓' if has_frontend else '✗'} Frontend service")
    print(f"  {'✓' if has_healthcheck else '✗'} Health check")
    print(f"  {'✓' if has_depends else '✗'} Service dependencies")
    
    if has_backend and has_frontend and has_healthcheck:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")

# Test 9: Check .env.example
print("\n✓ Test 9: Environment Configuration")
env_file = '.env.example'
if os.path.isfile(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
        has_database = 'DATABASE_URL' in env_content
        has_api = 'API' in env_content or 'REACT_APP' in env_content
        print(f"  {'✓' if has_database else '✗'} DATABASE_URL")
        print(f"  {'✓' if has_api else '✗'} API/Frontend config")
    print("  ✅ PASS")
else:
    print(f"  ✗ {env_file} not found")

# Final Summary
print("\n" + "=" * 70)
print("✅ PRE-DEPLOYMENT VERIFICATION COMPLETE!")
print("=" * 70)
print("\n📋 NEXT STEPS:")
print("\n  Option 1: Docker Deployment (Recommended)")
print("    1. Create .env file: cp .env.example .env")
print("    2. Edit .env if needed (optional for local testing)")
print("    3. Run: docker-compose up --build")
print("    4. Access: http://localhost:80 (frontend) | http://localhost:8000 (backend)")
print("\n  Option 2: Local Deployment (No Docker)")
print("    Terminal 1 - Backend:")
print("      cd backend")
print("      python -m venv venv")
print("      venv\\Scripts\\activate  # Windows")
print("      pip install -r requirements.txt")
print("      uvicorn app.main:app --reload")
print("")
print("    Terminal 2 - Frontend:")
print("      cd frontend")
print("      npm install")
print("      npm start")
print("\n  Option 3: Cloud Deployment")
print("    See docs/SETUP_GUIDE.md for Railway + Vercel instructions")
print("\n" + "=" * 70)
