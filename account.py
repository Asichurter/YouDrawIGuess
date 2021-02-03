import json

def load_account(pth):
    try:
        with open(pth, 'r') as f:
            accs = json.load(f)
            return accs
    except json.JSONDecodeError or FileNotFoundError:
        return None
