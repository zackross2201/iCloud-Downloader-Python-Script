# Required packages: pyicloud, tqdm
# Install them using: pip install pyicloud tqdm

import os
import sys
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException
from tqdm import tqdm

# --- Configuration ---
DOWNLOAD_DIR = "icloud_photo_backup"
# Set preferred size: 'original', 'medium', or 'thumb'
# Use 'original' to get the full resolution photo/video file.
DOWNLOAD_SIZE = 'original'
# --- End Configuration ---


def setup_auth(api):
    """
    Handles authentication when a second factor (2FA/2SA) is required.
    We prioritize the modern 2FA flow (just the code) to avoid the
    device selection process of 2SA.
    """
    
    if api.requires_2fa or api.requires_2sa:
        print("\n--- Two-Factor Authentication Required ---")
        
        # NOTE: Even if the account is technically 2SA, we bypass device selection
        # and ask for the code directly, as the user confirmed they get a code pop-up.
        
        code = input("Enter the 6-digit code that appeared on one of your trusted Apple devices: ")
        
        # Try validating as 2FA first (modern and simpler)
        if api.requires_2fa and api.validate_2fa_code(code):
            print("2FA code verified.")
        
        # If that failed, or if it was 2SA, try validating as 2SA
        elif api.requires_2sa and api.validate_verification_code(api.trusted_devices[0], code):
            # We assume the first device (index 0) is the SMS target,
            # as we need to pass a device object to validate_verification_code.
            print("2SA code verified (via direct code input).")
        
        else:
            print("Failed to verify security code. Exiting.")
            sys.exit(1)
        
        # Establish session trust if needed
        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            api.trust_session()
            print("Session trust established.")


def download_photos(api):
    """Downloads all photos from the iCloud Photo Library."""
    print("\n--- Starting Photo Download ---")
    
    # Ensure the download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"Download directory: ./{DOWNLOAD_DIR}")

    # Use tqdm for a professional progress bar
    photos = api.photos.all
    total_photos = len(photos)
    downloaded_count = 0
    skipped_count = 0

    print(f"Found {total_photos} items in the iCloud Photo Library.")
    
    # FIX: Iterate directly over the 'photos' object (which is the main 'All Photos' album)
    for photo in tqdm(photos, total=total_photos, desc="Downloading"):
        filename = photo.filename
        
        # Create a folder structure based on year and month the photo was taken (asset_date)
        try:
            asset_date = photo.created
            # Format: YYYY/MM/
            sub_dir = asset_date.strftime("%Y/%m")
            full_path_dir = os.path.join(DOWNLOAD_DIR, sub_dir)
            os.makedirs(full_path_dir, exist_ok=True)
            full_path_file = os.path.join(full_path_dir, filename)
        except Exception:
            # Fallback for assets with no creation date metadata (e.g., some system files)
            tqdm.write(f"\nSkipping item with missing date metadata: {filename}")
            skipped_count += 1
            continue


        # Skip if the file already exists locally (simple de-duplication)
        if os.path.exists(full_path_file):
            skipped_count += 1
            continue

        try:
            # Fetch the actual file data
            # The photo object acts as a dictionary for different sizes
            download = photo.download(DOWNLOAD_SIZE)
            
            # Write the binary content to the file
            with open(full_path_file, 'wb') as f:
                # Write in chunks to handle very large files (like videos) efficiently
                for chunk in download.iter_content(chunk_size=1048576): 
                    f.write(chunk)
            
            downloaded_count += 1
            # tqdm automatically updates the status bar
        
        except Exception as e:
            tqdm.write(f"\n[ERROR] Failed to download {filename}: {e}")
            skipped_count += 1

    print(f"\n--- Download Complete ---")
    print(f"Total files processed: {total_photos}")
    print(f"Files downloaded this session: {downloaded_count}")
    print(f"Files skipped (already existed or error): {skipped_count}")
    print(f"All files saved in the '{DOWNLOAD_DIR}' folder.")


def main():
    """Main function for the iCloud Downloader."""
    try:
        # 1. Get credentials from user
        apple_id = input("Enter your Apple ID (email): ")
        password = input("Enter your Apple ID Password (or App-Specific Password): ")
        
        # We still clean the password just in case the user pastes a space
        cleaned_password = password.replace(" ", "").replace("-", "")

        # 2. Attempt login
        print("\nAttempting login...")
        # Use the cleaned password for the service initiation
        api = PyiCloudService(apple_id, cleaned_password)

        # 3. Handle 2FA/2SA
        setup_auth(api)

        # 4. Start download
        download_photos(api)

    except PyiCloudFailedLoginException:
        print("\n[CRITICAL ERROR] Failed to log in. Check your Apple ID and password.")
        print("Note: If using your main password, you must accept the 2FA code on your device.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
