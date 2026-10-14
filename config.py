import os
'''
# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_very_secret_123'
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/users_chat.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     # Custom Data Paths
#     BASE_DIR = os.path.abspath(os.path.dirname(__file__))
#     DATA_DIR = os.path.join(BASE_DIR, 'data')
#     DB_PATH = os.path.join(DATA_DIR, 'rdguru.db')
#     MODEL_PATH = os.path.join(DATA_DIR, 'ddqn_rdgurupp.pt')
#     HPO_PATH = os.path.join(DATA_DIR, 'hp.obo')
'''
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_very_secret_123'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Keep rdguru.db for medical data (don't touch it)
    DB_PATH = os.path.join(DATA_DIR, 'rdguru.db')
    
    # Use separate database for users and conversations
    USERS_DB_PATH = os.path.join(DATA_DIR, 'users.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{USERS_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MODEL_PATH = os.path.join(DATA_DIR, 'ddqn_rdgurupp.pt')
    HPO_PATH = os.path.join(DATA_DIR, 'hp.obo')

    # API Keys
    GROQ_API_KEY = "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"
    GROQ_MODEL = "openai/gpt-oss-120b"
