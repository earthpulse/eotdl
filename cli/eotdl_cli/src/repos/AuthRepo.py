from pathlib import Path
import os 
import json 
import jwt

class AuthRepo():
    def __init__(self):
        self.algorithms = ['RS256']
        self.home = str(Path.home())
        self.creds_path = self.home + '/.etodl/creds.json'

    def save_creds(self, data):
        os.makedirs(self.home + '/.etodl', exist_ok=True)
        with open(self.creds_path, 'w') as f:
            json.dump(data, f)
        return self.creds_path
    
    def load_creds(self):
        if os.path.exists(self.creds_path):
            with open(self.creds_path, 'r') as f:
                creds = json.load(f)
            user = self.decode_token(creds)
            user['id_token'] = creds['id_token']
            return user
        return None
    
    def decode_token(self, token_data):
        return jwt.decode(token_data['id_token'], algorithms=self.algorithms, options={"verify_signature": False})
    
    def logout(self):
        os.remove(self.creds_path)
