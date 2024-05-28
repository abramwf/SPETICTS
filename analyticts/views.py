from django.shortcuts import render, redirect
from .forms import TranscribeForm
from .models import Transcribe, Sentences, User
from .forms import TranscribeForm
from django.http import JsonResponse
import nltk


# Create your views here.
def main(request):
  return render(request, 'profile-page.html')

def inputTest(request):
  return render(request, 'test-input.html')


nltk.download('punkt')

def transcribe_view(request):
    if request.method == 'POST':
        form = TranscribeForm(request.POST)
        if form.is_valid():
            transcribe_instance=form.save()
            #Menyimpan id transcribe
            request.session['transcribe_id'] = transcribe_instance.id
            return redirect('transcribe_result')
    else:
        form = TranscribeForm()
    return render(request, 'test-input.html', {'form': form})

def transcribe_view_save(request):
    if request.method == 'POST':
        

def transcribe_result(request):
    transcribe_id = request.session.get('transcribe_id')
    if transcribe_id:
        transcriptions = Transcribe.objects.filter(id=transcribe_id)
        if transcriptions.exists():
            transcribe_instance = transcriptions.first()
            sentences = Sentences.objects.filter(id_trans=transcribe_instance)
            return render(request, 'test-input.html', {'sentences': sentences})
    return redirect('transcribe_view')