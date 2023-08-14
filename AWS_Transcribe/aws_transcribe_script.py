import boto3

# Define the S3 bucket and audio file path
bucket_name = 'your-bucket-name' # --> change
audio_file_path = 'path/to/your/audiofile.mp3' # --> change

# Create a client for Amazon Transcribe
transcribe = boto3.client('transcribe')

# Create a job name and start transcription
job_name = "speechtotext"
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': f's3://{bucket_name}/{audio_file_path}'},
    MediaFormat='mp3',
    LanguageCode='en-US'
)

# Wait for the job to complete
while True:
    result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("Waiting for transcription job to complete...")
    time.sleep(15)  # You can adjust the sleep time

# Get the transcript file URL
transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']

# Download and process the transcript as needed, or just print the URI for manual retrieval
print(f"The transcript is available at: {transcript_uri}")
