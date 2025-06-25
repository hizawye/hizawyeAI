import os
import shutil

# Define the path to the AI's mind directory
mind_directory = "hizawye_mind"

print("--- Initiating Full Mind Wipe Protocol ---")
print("This will delete the entire hizawye_mind directory and all its contents.")

# Check if the mind directory exists
if os.path.exists(mind_directory):
    try:
        # Use shutil.rmtree to recursively delete the directory and all its contents
        shutil.rmtree(mind_directory)
        print(f"✅ SUCCESS: The directory '{mind_directory}' and all its contents have been deleted.")
        print("Hizawye's mind is now a blank slate. Run birth.py to create a new one.")
    except OSError as e:
        print(f"❌ ERROR: Could not delete the mind directory. Reason: {e}")
else:
    print("No mind directory found to delete. The mind is already clear.")

print("\n--- Protocol Complete ---")