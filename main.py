import os
import shutil
from src.quote_generator import generate_content
from src.audio_generator import generate_audio
from src.video_sourcer import fetch_background_video
from src.video_assembler import assemble_video
from src.instagram_publisher import upload_to_temp_host, publish_reel

def cleanup(files):
    """Removes temporary files to save disk space."""
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Could not delete {file}: {e}")

def main():
    print("=== Instagram Reels Generator Bot Started ===")
    
    # Temp files to clean up later
    temp_files = []
    
    try:
        # Step 1: Generate Quote & Caption
        print("\n--- Step 1: Generating Content ---")
        quote, caption = generate_content()
        print(f"Quote: {quote}")
        
        # Step 2: Generate Voiceover
        print("\n--- Step 2: Generating Audio ---")
        audio_path = generate_audio(quote, "temp_audio.mp3")
        temp_files.append(audio_path)
        
        # Step 3: Fetch Background Video
        print("\n--- Step 3: Fetching Background Video ---")
        bg_video_path = fetch_background_video("temp_bg.mp4")
        temp_files.append(bg_video_path)
        
        # Step 4: Assemble Final Reel
        print("\n--- Step 4: Assembling Video ---")
        final_video_path = assemble_video(bg_video_path, audio_path, "final_reel.mp4")
        
        # Step 5: Publish
        print("\n--- Step 5: Publishing to Instagram ---")
        public_video_url = upload_to_temp_host(final_video_path)
        publish_reel(public_video_url, caption)
        
        print("\n=== Workflow Completed Successfully ===")
        
    except Exception as e:
        print(f"\n=== Workflow Failed: {e} ===")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up temporary files...")
        cleanup(temp_files)
        # We leave final_reel.mp4 so the user can inspect it if they want.
        
if __name__ == "__main__":
    import time
    import schedule
    
    print("Running initial bot execution...")
    main()
    
    print("\n" + "="*50)
    print("🤖 BOT IS NOW IN SCHEDULER MODE")
    print("It will automatically generate and post a new Reel every 3 hours.")
    print("IMPORTANT: Leave this terminal window open in the background!")
    print("="*50 + "\n")
    
    # Schedule to run every 3 hours
    schedule.every(3).hours.do(main)
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute if it's time to run
