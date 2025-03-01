import subprocess
import os
# import json
import sys
from pathlib import Path
import argparse
# import anthropic

# Configuration
OUTPUT_DIR = Path("./downloads")
NOTES_DIR = Path("./notes")

def setup_directories():
    """Create necessary directories if they don't exist."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    NOTES_DIR.mkdir(exist_ok=True)

def download_video(url):
    """Download video from Bilibili using you-get."""
    print(f"Downloading video from {url}...")
    try:
        # Use you-get to download the video with subtitles
        result = subprocess.run(
            ["you-get", "--output-dir", str(OUTPUT_DIR), "--debug", url],
            capture_output=True,
            text=True,
            check=True
        )
        print("Download completed successfully")
        return parse_download_output(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")
        print(e.stdout)
        print(e.stderr)
        return None

def parse_download_output(output):
    """Parse the output from you-get to find the downloaded files."""
    lines = output.split('\n')
    video_file = None
    subtitle_file = None
    
    for line in lines:
        if "Saving to:" in line:
            file_path = line.split("Saving to:")[-1].strip()
            if file_path.endswith(('.mp4', '.flv', '.avi')):
                video_file = file_path
            elif file_path.endswith(('.srt', '.ass', '.vtt')):
                subtitle_file = file_path
    
    return {"video": video_file, "subtitle": subtitle_file}

def extract_subtitle_text(subtitle_file):
    """Extract text from subtitle file."""
    if not subtitle_file:
        return None
        
    if subtitle_file.endswith('.srt'):
        return extract_from_srt(subtitle_file)
    elif subtitle_file.endswith('.ass'):
        return extract_from_ass(subtitle_file)
    elif subtitle_file.endswith('.vtt'):
        return extract_from_vtt(subtitle_file)
    else:
        print(f"Unsupported subtitle format: {subtitle_file}")
        return None

def extract_from_srt(srt_file):
    """Extract text from SRT subtitle file."""
    import pysrt
    subs = pysrt.open(srt_file)
    return " ".join(sub.text for sub in subs)

def extract_from_ass(ass_file):
    """Extract text from ASS subtitle file."""
    text_lines = []
    with open(ass_file, 'r', encoding='utf-8') as f:
        events_section = False
        for line in f:
            if line.startswith('[Events]'):
                events_section = True
                continue
            if events_section and line.startswith('Dialogue:'):
                parts = line.split(',')
                if len(parts) >= 10:
                    text = ','.join(parts[9:]).strip()
                    # Remove formatting codes like {\\an8}
                    import re
                    text = re.sub(r'{\\[^}]*}', '', text)
                    text_lines.append(text)
    return " ".join(text_lines)

def extract_from_vtt(vtt_file):
    """Extract text from VTT subtitle file."""
    import webvtt
    vtt = webvtt.read(vtt_file)
    return " ".join(caption.text for caption in vtt)

def generate_notes(subtitle_text, video_url, client):
    """Generate notes from subtitle text using Claude AI."""
    if not subtitle_text:
        return "No subtitle text available to generate notes."
    
    print("Generating notes from subtitles...")
    
    prompt = f"""
    I have subtitles from a Bilibili video: {video_url}
    
    Please create comprehensive notes based on the content. Organize the notes in a clear structure with:
    1. Main topics and themes
    2. Key points and insights
    3. Important details or examples
    
    Subtitle text:
    {subtitle_text[:15000]}  # Limiting to avoid token limits
    
    Generate detailed, well-structured notes that would be useful for someone who wants to review the video content later.
    """
    
    try:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.3,
            system="You are an assistant that creates well-structured, comprehensive notes from video subtitles.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error generating notes: {e}")
        return f"Error generating notes: {str(e)}"

def save_notes(notes, video_url):
    """Save the generated notes to a file."""
    import hashlib
    url_hash = hashlib.md5(video_url.encode()).hexdigest()[:10]
    filename = NOTES_DIR / f"notes_{url_hash}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Notes for Bilibili Video\n\n")
        f.write(f"Source: {video_url}\n\n")
        f.write(notes)
    
    print(f"Notes saved to {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="Download Bilibili videos and generate notes from subtitles")
    parser.add_argument("url", help="URL of the Bilibili video")
    # parser.add_argument("--api-key", help="Anthropic API key")
    args = parser.parse_args()
    
    # api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    # if not api_key:
    #     print("Error: Anthropic API key is required. Set it with --api-key or ANTHROPIC_API_KEY environment variable.")
    #     sys.exit(1)
    
    # client = anthropic.Anthropic(api_key=api_key)
    
    setup_directories()
    
    download_result = download_video(args.url)
    if not download_result:
        print("Failed to download the video.")
        return
    
    subtitle_file = download_result.get("subtitle")
    if not subtitle_file:
        print("No subtitle file found.")
        return
    
    subtitle_text = extract_subtitle_text(subtitle_file)
    if not subtitle_text:
        print("Failed to extract text from subtitles.")
        return
    
    print(subtitle_text)
    
    # notes = generate_notes(subtitle_text, args.url, client)
    # notes_file = save_notes(notes, args.url)
    
    # print(f"\nProcess completed successfully!")
    # print(f"Video downloaded to: {download_result.get('video')}")
    # print(f"Notes saved to: {notes_file}")

if __name__ == "__main__":
    main()
