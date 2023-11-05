# Long audio to srt converter

Converts longer audio from openai Whisper to an srt file. The program splits
the chunks of music up, transcribes each, and combines all chunks into a srt file
with continuous timestamps.

## Running the script

- Clone the repository, and install the dependencies.
- You will want to have your `.env` file with your openAI token saved under
`OPENAI_API_KEY`.
- Change the inputs and output paths of the audio in the `audio_to_srt` function.
