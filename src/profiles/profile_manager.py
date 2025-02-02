import json
import os

PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'profiles_data')

def load_profile(profile_name):
    path = os.path.join(PROFILE_DIR, f'{profile_name}.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_profile(profile_name, profile_data):
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)
    path = os.path.join(PROFILE_DIR, f'{profile_name}.json')
    with open(path, 'w') as f:
        json.dump(profile_data, f, indent=4)