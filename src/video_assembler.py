import os
import sys

def transcribe_audio(audio_path):
    """Uses faster-whisper to get sentence-level timestamps."""
    from faster_whisper import WhisperModel
    print("Transcribing audio for sentence-level timestamps...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, word_timestamps=False)
    
    chunks = []
    for segment in segments:
        chunks.append({
            "text": segment.text.strip(),
            "start": segment.start,
            "end": segment.end
        })
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
        
    # Removed cinematic zoom (Ken Burns) to save memory on 512MB cloud servers
    # It requires resizing every frame dynamically in RAM, which crashes small servers.
    
    # Just crop to center to maintain 1080x1920
    video_clip = crop(video_clip, x_center=video_clip.w/2, y_center=video_clip.h/2, width=1080, height=1920)

    video_clip = video_clip.set_audio(final_audio)
    
    # Get sentence timestamps
    chunks = transcribe_audio(audio_path)
    
    # Darken video slightly for text readability
    dark_overlay = ColorClip(size=(1080, 1920), color=(0,0,0)).set_opacity(0.4).set_duration(video_clip.duration)
    
    # Create sentence-level text clips
    text_clips = []
    for c in chunks:
        duration = c['end'] - c['start']
        if duration <= 0:
            duration = 0.5
            
        try:
            txt_clip = TextClip(
                c['text'], 
                fontsize=75, 
                color='white', 
                font='Arial-Bold', 
                stroke_color='black', 
                stroke_width=2,
                method='caption',
                align='center',
                size=(1080 * 0.85, None)
            )
            
            # Position slightly higher to avoid Instagram's bottom UI elements
            txt_clip = txt_clip.set_position(('center', 0.4), relative=True)\
                               .set_start(c['start'])\
                               .set_end(c['start'] + duration)\
                               .crossfadein(0.3)\
                               .crossfadeout(0.3)
                               
            text_clips.append(txt_clip)
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
        threads=1,
        logger=None # Suppress moviepy logging if it's too noisy
    )
    print(f"Final video saved to {output_path}")
    return output_path
