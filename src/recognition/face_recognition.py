import threading
import time

# Placeholder for the current profile name
current_profile = "guest"

def recognition_loop(update_callback):
    global current_profile
    while True:
        # Replace the following with Hailo SDK integration.
        # For now, simulate detection (e.g., always guest or alternate between names)
        detected_profile = "guest"  # placeholder
        
        if detected_profile != current_profile:
            current_profile = detected_profile
            update_callback(current_profile)
        time.sleep(2)  # Adjust the polling interval as needed

def start_recognition(update_callback):
    thread = threading.Thread(target=recognition_loop, args=(update_callback,), daemon=True)
    thread.start()
