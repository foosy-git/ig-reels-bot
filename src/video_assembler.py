import os
import sys
import json
from google import genai

def translate_segments_to_chinese(segments_text_list):
    """Translates a list of English phrases into Chinese using Gemini."""
    from config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing.")
        
    # Add a strict 30 second timeout (in milliseconds) to prevent the API call from hanging
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={'timeout': 30000}
    )
    
    prompt = "You are a professional translator. I will provide a JSON array of English subtitle segments. Translate each segment into natural, cinematic Chinese (Standard Mandarin). Return a JSON array of strings in the exact same order. Do not merge or split segments. Respond STRICTLY with the JSON array.\n\n"
    prompt += json.dumps(segments_text_list)
    
    print(f"  -> Sending {len(segments_text_list)} segments to Gemini for translation...")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        print("  -> Received response from Gemini.")
    except Exception as e:
        print(f"Gemini API request failed or timed out: {e}")
        return [""] * len(segments_text_list)
    
    text = response.text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
        
    try:
        translated_list = json.loads(text.strip())
        if len(translated_list) != len(segments_text_list):
            print("Translation array length mismatch! Falling back to English only.")
            return [""] * len(segments_text_list)
        return translated_list
    except Exception as e:
        print(f"Error parsing Gemini translation: {e}")
        return [""] * len(segments_text_list)

def transcribe_audio(audio_path):
    """Uses faster-whisper to get phrase-level timestamps."""
    from faster_whisper import WhisperModel
    print("Transcribing audio for phrase-level timestamps...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, word_timestamps=False)
    
    chunks = []
    for segment in segments:
        chunks.append({
            "text": segment.text.strip(),
            "start": segment.start,
            "end": segment.end
        })
        
    # Now translate to Chinese
    english_texts = [c["text"] for c in chunks]
    print("Translating phrases to Chinese...")
    chinese_texts = translate_segments_to_chinese(english_texts)
    
    for i, c in enumerate(chunks):
        c["chinese_text"] = chinese_texts[i]
        
    return chunks

def assemble_video(video_path, audio_path, output_filename="final_reel.mp4"):
    """Merges video, audio, and adds dynamic text overlay."""
    import platform
    if platform.system() == "Windows":
        os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
    else:
        # In Linux (Docker), MoviePy usually finds it automatically if installed
        os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
    
    # Fix for Pillow >= 10.0 compatibility with MoviePy
    import PIL.Image
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
        
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, CompositeAudioClip
    from moviepy.video.fx.all import loop, resize, crop

    print("Assembling final video...")
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    # Match video duration to audio duration
    if video_clip.duration < audio_clip.duration:
        video_clip = loop(video_clip, duration=audio_clip.duration)
    else:
        video_clip = video_clip.subclip(0, audio_clip.duration)
        
    # Mix voiceover with background music
    bg_music_path = os.path.join(os.getcwd(), "background_music.mp3")
    if os.path.exists(bg_music_path):
        from moviepy.audio.fx.all import volumex, audio_loop
        bg_music = AudioFileClip(bg_music_path).fx(volumex, 0.12) # Very quiet to not overpower voice
        if bg_music.duration < audio_clip.duration:
            bg_music = audio_loop(bg_music, duration=audio_clip.duration)
        else:
            bg_music = bg_music.subclip(0, audio_clip.duration)
            
        final_audio = CompositeAudioClip([audio_clip, bg_music])
    else:
        final_audio = audio_clip
        
    # Apply cinematic slow zoom (Ken Burns effect)
    # Zooms from 1.0x to 1.1x over the duration
    def zoom(t):
        return 1 + 0.1 * (t / video_clip.duration)
    video_clip = resize(video_clip, zoom)
    
    # After resizing, crop back to center to maintain 1080x1920
    video_clip = crop(video_clip, x_center=video_clip.w/2, y_center=video_clip.h/2, width=1080, height=1920)

    video_clip = video_clip.set_audio(final_audio)
    
    # Get sentence timestamps
    chunks = transcribe_audio(audio_path)
    
    # Darken video slightly for text readability
    dark_overlay = ColorClip(size=(1080, 1920), color=(0,0,0)).set_opacity(0.4).set_duration(video_clip.duration)
    
    import platform
    if platform.system() == "Windows":
        chinese_font = r"C:\Windows\Fonts\msyh.ttc"
    else:
        chinese_font = "WenQuanYi-Zen-Hei"

    # Create phrase-level dual-language text clips
    text_clips = []
    for i, c in enumerate(chunks):
        duration = c['end'] - c['start']
        # Prevent micro-flashes for very fast speech
        if duration < 0.5:
            duration = 0.5
            
        try:
            # Render English (Top)
            en_clip = TextClip(
                c['text'], 
                fontsize=75, 
                color='white', 
                font='Arial-Bold', 
                stroke_color='black', 
                stroke_width=3,
                method='caption',
                align='center',
                size=(1080 * 0.85, None)
            )
            # Position English higher up to allow room for word wrapping
            en_clip = en_clip.set_position(('center', 1920/2 - 160))\
                             .set_start(c['start'])\
                             .set_end(c['start'] + duration)
            text_clips.append(en_clip)
            
            # Render Chinese (Bottom)
            if c.get("chinese_text"):
                zh_clip = TextClip(
                    c['chinese_text'], 
                    fontsize=60, 
                    color='#F9E076', 
                    font=chinese_font, 
                    stroke_color='black', 
                    stroke_width=3,
                    method='caption',
                    align='center',
                    size=(1080 * 0.85, None)
                )
                # Position Chinese lower down so it never touches the English text
                zh_clip = zh_clip.set_position(('center', 1920/2 + 60))\
                                 .set_start(c['start'])\
                                 .set_end(c['start'] + duration)
                text_clips.append(zh_clip)
                
        except Exception as e:
            print(f"Error creating TextClip: {e}")
            raise e
        
    final_clip = CompositeVideoClip([video_clip, dark_overlay] + text_clips, size=(1080, 1920))
    
    output_path = os.path.join(os.getcwd(), output_filename)
    final_clip.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac",
        threads=4,
        logger=None # Suppress moviepy logging if it's too noisy
    )
    print(f"Final video saved to {output_path}")
    return output_path
