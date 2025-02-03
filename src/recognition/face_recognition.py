import threading
import time

# Simulated current profile variable at the module level.
_current_profile = "guest"

def recognition_loop(update_callback):
    global _current_profile  # Declare that we’re using the module-level variable.
    while True:
        # For simulation: alternate between "guest" and "user1".
        new_profile = "user1" if _current_profile == "guest" else "guest"
        
        if new_profile != _current_profile:
            _current_profile = new_profile
            update_callback(_current_profile)
        time.sleep(5)  # Adjust the interval as needed.

def start_recognition(update_callback):
    thread = threading.Thread(target=recognition_loop, args=(update_callback,), daemon=True)
    thread.start()
