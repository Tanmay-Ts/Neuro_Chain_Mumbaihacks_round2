import hashlib
import json

def compute_hash(prev_hash, debunk_data):
    # Sort keys to ensure consistent hashing
    # Convert non-serializable objects to string if needed
    safe_data = {k: str(v) for k, v in debunk_data.items()}
    data_str = json.dumps(safe_data, sort_keys=True)
    payload = f"{prev_hash}{data_str}".encode('utf-8')
    return hashlib.sha256(payload).hexdigest()