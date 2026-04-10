import sys
sys.path.append('e:\\antigravity\\citms')
from backend.src.core.config import settings
print("Settings loaded successfully!")
print("DATABASE_URL:", settings.DATABASE_URL)
