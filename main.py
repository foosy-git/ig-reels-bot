import os
import shutil
from src.quote_generator import generate_content
from src.analytics_fetcher import get_top_performing_context
from src.image_assembler import generate_carousel_images
from src.instagram_publisher import publish_carousel

def cleanup(files):
    """Removes temporary files to save disk space."""
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Could not delete {file}: {e}")

def main():
    print("=== Instagram Carousel Generator Bot Started ===")
    
    # Temp files to clean up later
    temp_files = []
    
    try:
        # Step 0: Fetch Analytics Context
        print("\n--- Step 0: Analyzing Past Performance ---")
        analytics_context = get_top_performing_context()
        
        # Step 1: Generate Quote & Caption
        print("\n--- Step 1: Generating Content ---")
        quotes, caption = generate_content(analytics_context)
        for i, q in enumerate(quotes):
            print(f"Quote {i+1}: {q}")
            
        # Step 2: Assemble Images
        print("\n--- Step 2: Assembling Images ---")
        image_paths = generate_carousel_images(quotes)
        temp_files.extend(image_paths)
        
        # Step 3: Publish
        print("\n--- Step 3: Publishing to Instagram ---")
        publish_carousel(image_paths, caption)
        
        print("\n=== Workflow Completed Successfully ===")
        
    except Exception as e:
        print(f"\n=== Workflow Failed: {e} ===")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up temporary files...")
        cleanup(temp_files)
        
if __name__ == "__main__":
    import time
    import schedule
    
    print("Running initial bot execution...")
    main()
    
    print("\n" + "="*50)
    print("🤖 BOT IS NOW IN SCHEDULER MODE")
    print("It will automatically generate and post a new Image Carousel every 6 hours.")
    print("IMPORTANT: Leave this terminal window open in the background!")
    print("="*50 + "\n")
    
    # Schedule to run every 6 hours
    schedule.every(6).hours.do(main)
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute if it's time to run
