from flask import Flask
from flask import request
from flask_cors import CORS
from flask import render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os


#for gcp
from google.cloud import storage

#for gcp speech
import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types




UPLOAD_FOLDER = 'sample_data/uploads'

bucket_name="my-xtra-cool-bucket"
destination_blob_name="sample_data"
gcs_uri="gs://my-xtra-cool-bucket/sample_data"


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def hello():
    return render_template('index.html')



#this function does the call to google to remotely convert the audio file to text

def transcribe_gcs(gcs_uri):
    """Transcribes the audio file specified by the gcs_uri."""
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=44100,
        language_code='en-US')

    response = client.recognize(config, audio)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))





@app.route('/audio-file',methods=['POST'])
def get_audio():

    if request.method=="POST":

        print(request)
        
        file = request.files['myAudioFile']
        filename = secure_filename(file.filename)

        print(filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("filename is ",filename)
        dest=os.path.join(app.config['UPLOAD_FOLDER'], filename)

        print("dest file is ",dest)
        source_file_name=dest
        upload_blob(bucket_name, source_file_name, destination_blob_name)

        # return redirect(url_for('uploaded_file',filename=filename))
        text_transcribed=transcribe_gcs(gcs_uri)

        
        
        

    return text_transcribed





# def upload_to_gcloud(bucket_name, source_file, destination_blob_name):

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))






if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')