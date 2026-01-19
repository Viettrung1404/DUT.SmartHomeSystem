import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT Authentication
SECRET_KEY = os.getenv("SECRET_KEY", '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3')
ALGORITHM = os.getenv("ALGORITHM", 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
