from pytube import YouTube

import pysrt

from youtube_transcript_api import YouTubeTranscriptApi 
  
# assigning srt variable with the list 
# of dictionaries obtained by the get_transcript() function
yt_vid_id = "Ko5Lnkt2sTg"
transcript_list = YouTubeTranscriptApi.list_transcripts(yt_vid_id)
print(transcript_list)
# srt = YouTubeTranscriptApi.get_transcript("Ko5Lnkt2sTg", languages=['ar'])

# prints the result
# print(srt)
    
def list_available_subtitles(video_url):
    # Create a YouTube object
    yt = YouTube(video_url)

    # Get the available captions
    captions = yt.captions

    # Print the available languages
    if not captions:
        print("No subtitles available for this video.")
        return

    print("Available subtitle languages:")
    for caption in captions:
        print(f"{caption.code}: {caption.name}")

def download_subtitles(video_url, language_code='en'):
    # Create a YouTube object
    yt = YouTube(video_url)

    # Get the captions in the specified language
    caption = yt.captions.get_by_language_code(language_code)
    if not caption:
        print(f"No subtitles found for language code: {language_code}")
        return

    # Download the subtitles
    srt_captions = caption.generate_srt_captions()
    with open(f'subtitles_{language_code}.srt', 'w', encoding='utf-8') as f:
        f.write(srt_captions)

    # Load the subtitles using pysrt
    # subs = pysrt.open('subtitles.srt', encoding='utf-8')

    # # Print the subtitles with timestamps
    # for sub in subs:
    #     print(f"{sub.start} --> {sub.end}")
    #     print(sub.text)
    #     print()

# Example usage
video_url = 'https://www.youtube.com/watch?v=Ko5Lnkt2sTg'
# list_available_subtitles(video_url)
# download_subtitles(video_url, 'auto')