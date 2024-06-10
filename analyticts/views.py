from django.shortcuts import render, redirect, get_object_or_404
from .models import Transcribe, Sentences, Named
from .forms import TranscribeForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import time, requests
from django.shortcuts import render, redirect
from .models import User
import google.generativeai as genai
import spacy
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Import paginator
from django.core.paginator import Paginator

# Create your views here.
def main(request):
    try:    
        transcriptions = Transcribe.objects.all().order_by('-id')

        if not transcriptions.exists():
            raise Transcribe.DoesNotExist
        # Set up pagination
        p = Paginator(Transcribe.objects.all(), 3)
        page = request.GET.get('page')
        transcriptions = p.get_page(page)
        nums = "a"*transcriptions.paginator.num_pages

        return render(request, 'dashboard.html', {'transcriptions':transcriptions, 'nums':nums})
    except Transcribe.DoesNotExist:
        messages.error(request, "No projects found, click add project to make a new project")
        return render(request, 'dashboard.html', {'transcriptions': [], 'nums': ''})

def detil_view(request, pk):
    transcribe = get_object_or_404(Transcribe, pk=pk)
    sentences = Sentences.objects.filter(id_trans=transcribe)
    named_entities = Named.objects.filter(transcription=transcribe)
    
    entity_list = []
    for entity in named_entities:
        entity_info = {
            'id': entity.id,
            'label': entity.label,  
            'text': entity.text,
        }
        entity_list.append(entity_info)

    print(f"Named Entities: {named_entities}")

    context = {
        'transcribe': transcribe,
        'sentences': sentences,
        'named_entities': entity_list
    }
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            transcribe_id = request.POST.get('delete')
            try:
                transcribe_to_delete = Transcribe.objects.get(pk=transcribe_id)
                transcribe_to_delete.delete()
                messages.success(request, "File deleted successfully.")
                return redirect('home')
            except Transcribe.DoesNotExist:
                messages.error(request, "File not found.")
                return redirect('home')
    
    return render(request, 'detil-page.html', context)



# Load the spaCy model once at the top of your file
nlp_ner_last = spacy.load("./analyticts/last-model/model-last")

WHISPER_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
WHISPER_HEADERS = {"Authorization": "Bearer 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"}

SENTIMENT_API_URL = "https://api-inference.huggingface.co/models/stevanussmbrng/speeches_sentiment"
SENTIMENT_HEADERS = {"Authorization": "Bearer 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"}

MAX_RETRIES = 5  # Set the maximum number of retries
RETRY_INTERVAL = 10  # Set the time interval between retries (in seconds)

# def main(request):
#   return render(request, 'profile-page.html')

def query_whisper(file):
    response = requests.post(WHISPER_API_URL, headers=WHISPER_HEADERS, files={"file": file}, params={"task": "transcribe"})
    response.raise_for_status()  
    return response.json()

def query_sentiment(payload):
    for _ in range(MAX_RETRIES):
        try:
            response = requests.post(SENTIMENT_API_URL, headers=SENTIMENT_HEADERS, json=payload)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying the API: {e}")
            time.sleep(RETRY_INTERVAL)
    
    print("Error: Unable to retrieve sentiment after maximum retries.")
    return None  # Indicate failure to retrieve sentiment

def transcribe_audio(request):
    user = request.user 
    transcription = None
    error = None
    sentences_with_sentiment = []
    named_entities = []
    file_name = None

    if request.method == 'POST' and request.FILES.get('audio'):
        print("POST request received")
        audio_file = request.FILES['audio']
        file_name = audio_file.name
        print(f"User username: {user.username}")
        print(f"File name: {file_name}")
        try:
            output = query_whisper(audio_file)
            print(f"Whisper output: {output}")
        except requests.exceptions.RequestException as e:
            error = f"Failed to transcribe audio: {str(e)}"
            return render(request, 'input.html', {
                'transcription': transcription,
                'error': error,
                'sentences_with_sentiment': sentences_with_sentiment,
                'named_entities': named_entities,
                'file_name': file_name,
                'user': user
            })

        if "text" in output:
            print(f"Transcription text: {output['text']}")
            genai.configure(api_key="AIzaSyC8C8EBUXv4UQvAe5TE9EklBTJgn-OzVXk")

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

            prompt = (
              "Tolong sempurnakan potongan paragraf berikut ini, paragraf ini merupakan hasil dari otomasi text to speech: "
              "(tolong jangan merubah kata ya). tolong pada setiap kalimatnya anda pisahkan dengan tanda titik, lalu jangan sampai "
              "ada tanda baca (.) lain kecuali pada akhir kalimat. Tolong jika ada tanda baca (.) pada angka atau ejaan uang atau "
              "list angka, tolong diganti dengan (,) saja. jika ada list semisal 1. 2. tolong ganti dengan 1, 2, \n"
            )
            response = model.generate_content(prompt + output["text"])
            transcription = response.text
            sentences = [sentence.strip() for sentence in transcription.split('.') if sentence]

            try:
                sentiment_results = query_sentiment({"inputs": sentences})
            except requests.exceptions.RequestException as e:
                error = f"Failed to analyze sentiment: {str(e)}"
                return render(request, 'input.html', {
                    'transcription': transcription,
                    'error': error,
                    'sentences_with_sentiment': sentences_with_sentiment,
                    'named_entities': named_entities,
                    'file_name': file_name,
                    'user':user
                })

            if sentiment_results is None:
                error = "Failed to analyze sentiment after maximum retries."
                return render(request, 'input.html', {
                    'transcription': transcription,
                    'error': error,
                    'sentences_with_sentiment': sentences_with_sentiment,
                    'named_entities': named_entities,
                    'file_name': file_name,
                    'user':user
                })

            for sentence, sentiment in zip(sentences, sentiment_results):
                if isinstance(sentiment, list):
                    sentiments = {entry['label']: entry['score'] for entry in sentiment}
                    sentences_with_sentiment.append((
                        sentence,
                        round(sentiments.get('positive', 0.0), 5),
                        round(sentiments.get('negative', 0.0), 5),
                        round(sentiments.get('neutral', 0.0), 5)
                    ))
                else:
                    error = "Unexpected sentiment analysis format"
                    return render(request, 'input.html', {
                        'transcription': transcription,
                        'error': error,
                        'sentences_with_sentiment': sentences_with_sentiment,
                        'named_entities': named_entities,
                        'file_name': file_name,
                        'user':user
                    })

            doc_last = nlp_ner_last(transcription)

            entities = []
            current_entity = {'teks': '', 'label': ''}

            for token in doc_last:
                label = ""
                for ent in doc_last.ents:
                    if token.text in ent.text:
                        label = ent.label_
                        break

                if token.is_punct:
                    current_entity['teks'] += token.text
                else:
                    if current_entity['label'] == label:
                        current_entity['teks'] += ' ' + token.text
                    else:
                        if current_entity['teks']:
                            entities.append(current_entity)
                        current_entity = {'teks': token.text, 'label': label}

            # Append the last entity
            if current_entity['teks']:
                entities.append(current_entity)

            named_entities = entities

        else:
            error = "Failed to transcribe audio"

    return render(request, 'input.html', {
        'transcription': transcription,
        'error': error,
        'sentences_with_sentiment': sentences_with_sentiment,
        'named_entities': named_entities,
        'file_name': file_name,
        'user':user
    })

# @login_required
def save_results(request):
    if request.method == 'POST':
        try:
            text = request.POST['text']
            file_name = request.POST['file_name']
            sentences = request.POST.getlist('sentences')
            positive_scores = request.POST.getlist('positive')
            negative_scores = request.POST.getlist('negative')
            neutral_scores = request.POST.getlist('neutral')
            named_entities_texts = request.POST.getlist('named_entities_texts')
            named_entities_labels = request.POST.getlist('named_entities_labels')

            transcription = Transcribe.objects.create(trans_result=text, title=file_name)
            for sentence, pos, neg, neu in zip(sentences, positive_scores, negative_scores, neutral_scores):
                maxScore = max(pos, neg, neu)
                if pos == maxScore:
                    sa_tag = Sentences.SATag.POSITIVE
                elif neg == maxScore:
                    sa_tag = Sentences.SATag.NEGATIVE
                else:
                    sa_tag = Sentences.SATag.NEUTRAL
                Sentences.objects.create(
                    sentence=sentence,
                    id_trans=transcription,
                    positive=pos,
                    negative=neg,
                    neutral=neu,
                    sa_tag=sa_tag
                )
            
            for text, label in zip(named_entities_texts, named_entities_labels):
                Named.objects.create(
                    text=text,
                    transcription=transcription,
                    label=label
                )
            messages.success(request, "Transcription saved succesfully.")
        # error handling for save transcribe
        except Exception as e:
            messages.error(request, f"An error was found: {e}")
        return redirect('home')
    return redirect('home')
