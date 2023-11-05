from pydub import AudioSegment
import openai
import os
from dotenv import load_dotenv, find_dotenv
import tempfile

# Setup environment variables
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ["OPENAI_API_KEY"]

# ================================================================

# Util function to convert from milliseconds to srt timestamp 
def milliseconds_to_srt_timestamp(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int(milliseconds % 1000)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# ================================================================

def audio_to_srt(input_file_name, extension, getPlainText=False, segment_size=10):
    # Load the audio file
    try:
        audio =  AudioSegment.from_mp3(f"./audio/{input_file_name}.{extension}")
    except:
        print(f"Could not find file \"./audio/{input_file_name}.{extension}\"")
        return

    # Initialise Variables
    prev_end_segment_time = 0
    curr_time = 0 
    segment_length = segment_size * 60 * 1000 # segment_size minutes
    curr_id = 1
    srt_output = []
    seg_count = 1

    while (curr_time < len(audio)):
        print(f"========= Splitting Chunk {seg_count} =========")

        # Splits current chunk of segment
        end_segment_time = min(curr_time + segment_length, len(audio))
        segment = audio[curr_time:end_segment_time]

        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
            segment.export(temp_file.name, format="mp3")
            
            print(f"========= Transcribing Chunk {seg_count} =========")
            response = openai.Audio.transcribe(
                "whisper-1", 
                file=temp_file, 
                response_format="verbose_json",
                language="en"
            )
        
        # Additionally writes plain text to text file if specified
        if (getPlainText):
            with open(f"./text_output/{input_file_name}.txt", "a") as text_file:
                text_file.write(response["text"] + " ")
        
        # [(start, end, text)]
        post_response = [(seg["start"], seg["end"], seg["text"]) for seg in response["segments"]]

        for start, end, text in post_response:
            # Calculate times and append to srt_output
            start_srt = milliseconds_to_srt_timestamp(int(start)*1000 + int(prev_end_segment_time))
            end_srt = milliseconds_to_srt_timestamp(int(end)*1000 + int(prev_end_segment_time))
            srt_output.append(
                f"{curr_id}\n{start_srt} --> {end_srt}\n{text.lstrip()}\n"
            )

            # Increment variables
            curr_id += 1
        
        # Increment variables
        prev_end_segment_time = end_segment_time
        curr_time = end_segment_time
        seg_count += 1

    # Handle output
    print(f"========= Writing to output \"./srt_output/{input_file_name}.srt\" =========")
    with open(f"./srt_output/{input_file_name}.srt", 'w') as file:
        for sub_srt in srt_output:
            file.write(sub_srt)
            file.write("\n")
    print(f"========= Success =========")

if __name__ == "__main__":
    audio_to_srt("50011", "mp3", getPlainText=True)