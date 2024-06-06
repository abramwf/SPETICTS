from django.shortcuts import render, redirect
# from .forms import TranscribeForm
# from .models import Transcribe, Sentences, User
from django.http import JsonResponse
import nltk


# Create your views here.
def main(request):
  return render(request, 'profile-page.html')

def inputTest(request):
  return render(request, 'test-input.html')


# nltk.download('punkt')

# def transcribe_view(request):
#     if request.method == 'POST':
#         form = TranscribeForm(request.POST)
#         if form.is_valid():
#             transcribe_instance=form.save()
#             #Menyimpan id transcribe
#             request.session['transcribe_id'] = transcribe_instance.id
#             return redirect('transcribe_result')
#     else:
#         form = TranscribeForm()
#     return render(request, 'input.html', {'form': form})

# def transcribe_view_save(request):
#     if request.method == 'POST':
        

# def transcribe_result(request):
#     transcribe_id = request.session.get('transcribe_id')
#     if transcribe_id:
#         transcriptions = Transcribe.objects.filter(id=transcribe_id)
#         if transcriptions.exists():
#             transcribe_instance = transcriptions.first()
#             sentences = Sentences.objects.filter(id_trans=transcribe_instance)
#             return render(request, 'input.html', {'sentences': sentences})
#     return redirect('transcribe_view')


# views.py

import os
from django.shortcuts import render
from django.http import HttpResponse
import requests
import google.generativeai as genai
from django.core.cache import cache
from google.cloud import aiplatform
from google.protobuf.struct_pb2 import Value
from typing import List
from .models import Transcription, Sentence
import random

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
headers = {"Authorization": "Bearer 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"}

def query(file):
    response = requests.post(API_URL, headers=headers, files={"file": file}, params={"task": "transcribe"})
    return response.json()

# def generate_dummy_sentiment():
#     return [round(random.uniform(0, 1), 3) for _ in range(3)]

def transcribe_audio(request):
    transcription = None
    error = None
    # sentences_with_sentiment = []

    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        output = query(audio_file)
        
        
        if "text" in output:
            genai.configure(api_key="AIzaSyAFXT-_UIkJl0e5EKnXIw-o7yhfzIyPCQ8")

            generation_config = {
              "temperature": 1,
              "top_p": 0.95,
              "top_k": 64,
              "max_output_tokens": 8192,
              "response_mime_type": "text/plain",
            }
            safety_settings = [
              {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
              },
              {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
              },
              {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
              },
              {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
              },
            ]

            model = genai.GenerativeModel(
              model_name="gemini-1.5-pro-latest",
              safety_settings=safety_settings,
              generation_config=generation_config,
            )

            prompt= (
              "Tolong sempurnakan potongan paragraf berikut ini, paragraf ini merupakan hasil dari otomasi text to speech: "
                "(tolong jangan merubah kata ya). tolong pada setiap kalimatnya anda pisahkan dengan tanda titik, lalu jangan sampai "
                "ada tanda baca (.) lain kecuali pada akhir kalimat. Tolong jika ada tanda baca (.) pada angka atau ejaan uang atau "
                "list angka, tolong diganti dengan (,) saja. jika ada list semisal 1. 2. tolong ganti dengan 1, 2, \n"
            )
            response = model.generate_content(prompt + output["text"])
            transcription = response.text
            # sentences = [sentence.strip() for sentence in transcription.split('.') if sentence]
            
            # sentiment_results = [generate_dummy_sentiment() for _ in sentences]
            
            # Save transcription and sentences with sentiment to database

            # sentences_with_sentiment = list(zip(sentences, sentiment_results))

            # sentences = [sentence.strip() for sentence in transcription.split('.') if sentence]
            # sentiment_results = predict_custom_trained_model_sample(
            #     project="371850269577",
            #     endpoint_id="2125109685886386176",
            #     instances=sentences
            # )
        else:
            error = "Failed to transcribe audio"

    return render(request, 'input.html', {'transcription': transcription, 'error': error}) # 'sentiment_results': sentiment_results, 'sentences_with_sentiment': sentences_with_sentiment

def save_results(request):
    if request.method == 'POST':
        text = request.POST['text']
        sentences = request.POST.getlist('sentences')
        sentiments = request.POST.getlist('sentiments')

        transcription = Transcription.objects.create(text=text)
        for sentence, sentiment in zip(sentences, sentiments):
            sentiment_list = list(map(float, sentiment.strip('[]').split(',')))
            Sentence.objects.create(text=sentence, transcription=transcription, sentiment=sentiment_list)
        
        return redirect('input')
    return redirect('input')


# def predict_custom_trained_model_sample(
#     project: str,
#     endpoint_id: str,
#     instances: List[str],
#     location: str = "asia-southeast2",
#     api_endpoint: str = "asia-southeast2-aiplatform.googleapis.com",
# ):
#     client_options = {"api_endpoint": api_endpoint}
#     client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    
#     instances_formatted = [Value(string_value=instance) for instance in instances]
#     endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
#     response = client.predict(endpoint=endpoint, instances=instances_formatted)
    
#     predictions = []
#     for index, (prediction, sentence) in enumerate(zip(response.predictions, instances)):
#         predictions.append(f"Prediction {index+1}: {prediction}, Kalimat: {sentence}")
#     return predictions
