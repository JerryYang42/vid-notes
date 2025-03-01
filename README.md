# vid-notes

## Components:

Video Download: you-get or youtube-dl (with Bilibili support)
Subtitle Extraction: pysrt or webvtt-py
Text Processing: OpenAI API (GPT-4) or Anthropic API (Claude)

## Analysis:

Pros: Full control over the pipeline, highly customizable, can be automated
Cons: Requires programming knowledge, may need maintenance as Bilibili changes
Complexity: Moderate
Cost: API costs for AI processing (typically $0.01-0.10 per note depending on length)


## Prerequisites:

Install Python packages: pip install you-get pysrt webvtt-py anthropic
Set up an Anthropic API key


Usage:
```bash
python bilibili_notes.py https://www.bilibili.com/video/your-video-id --api-key YOUR_API_KEY
```

## How it works:

Downloads the video and subtitles using you-get
Extracts text from subtitles based on format
Uses Claude AI to generate structured notes
Saves notes as markdown files


## Potential enhancements:

Add batch processing for multiple videos
Implement a simple GUI using Streamlit
Add translation capabilities for non-native language content
