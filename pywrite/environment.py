import os
from dotenv import load_dotenv

def set_env(host=None, port=None, password=None):
    if os.path.exists('.env'):
        load_dotenv()
    else:
        print("No .env file found. Creating one with provided values.")

    # Update or create .env file with provided values
    with open('.env', 'w') as f:
        if host:
            f.write(f"HOST={host}\n")
        if port:
            f.write(f"PORT={port}\n")
        if password:
            f.write(f"PASSWORD={password}\n")

    print(".env file updated successfully.")