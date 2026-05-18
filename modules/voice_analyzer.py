try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

import re
import tempfile
import os


def transcribe_audio(audio_bytes: bytes) -> dict:
    """
    Transcribes audio bytes to text using SpeechRecognition.
    Prefers offline Sphinx for privacy, falls back to Google if configured or if Sphinx fails wildly.
    """
    if not _SR_AVAILABLE:
        return {"success": False, "error": "Speech recognition libraries are not installed on this server."}

    try:

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            # Clean up noise a bit for better offline recognition
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            try:
                # Task 4.2: Local Offline STT
                text = recognizer.recognize_sphinx(audio_data)
            except Exception as e:
                # Fallback to Google if offline fails (e.g. library missing models)
                try:
                    text = recognizer.recognize_google(audio_data)
                except Exception as inner_e:
                    raise Exception(f"Offline STT failed: {e}. Online STT failed: {inner_e}")
        
        os.remove(tmp_path)
        return {"success": True, "text": text}
    except sr.UnknownValueError:
        return {"success": False, "error": "Speech was unintelligible. Please speak clearly or check your microphone."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_filler_words(text: str) -> dict:
    """
    Analyzes text for common filler words.
    Returns dict with counts and feedback string.
    """
    filler_words = ["um", "uh", "like", "you know", "literally", "basically", "actually"]
    text_lower = text.lower()
    
    counts = {}
    total_fillers = 0
    for word in filler_words:
        # Simple word boundary regex
        matches = len(re.findall(r'\b' + word + r'\b', text_lower))
        if matches > 0:
            counts[word] = matches
            total_fillers += matches
            
    feedback = ""
    if total_fillers > 0:
        details = ", ".join([f"'{k}' ({v} times)" for k, v in counts.items()])
        if total_fillers > 3:
            feedback = f"Communication Tip: You used quite a few filler words ({details}). Try taking a brief pause instead of filling the silence."
        else:
            feedback = f"Communication Tip: You used a few filler words ({details}). It's natural, but try to minimize them for a more confident delivery."
            
    return {
        "total": total_fillers,
        "counts": counts,
        "feedback": feedback
    }
