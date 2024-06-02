from django.shortcuts import render, redirect, get_object_or_404
from .models import Transcribe, Sentences, User
from .forms import TranscribeForm
from django.http import JsonResponse
import nltk

# Import paginator
from django.core.paginator import Paginator

# Create your views here.
def main(request):
    transcriptions = Transcribe.objects.all()

    # Set up pagination
    p = Paginator(Transcribe.objects.all(), 3)
    page = request.GET.get('page')
    transcriptions = p.get_page(page)
    nums = "a"*transcriptions.paginator.num_pages

    return render(request, 'dashboard.html', {'transcriptions':transcriptions, 'nums':nums})

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

# def transcribe_view_save(request):
#     if request.method == 'POST':

def transcribe_result(request):
    transcribe_id = request.session.get('transcribe_id')
    if transcribe_id:
        transcriptions = Transcribe.objects.filter(id=transcribe_id)
        if transcriptions.exists():
            transcribe_instance = transcriptions.first()
            sentences = Sentences.objects.filter(id_trans=transcribe_instance)
            return render(request, 'test-input.html', {'sentences': sentences})
    return redirect('transcribe_view')

def detil_view(request,pk):
    transcribe = get_object_or_404(Transcribe, pk)
    sentences = Sentences.objects.get(id_trans=transcribe)
    context= {
        'transcribe':transcribe,
        'sentences':sentences
    }
    return render(request, 'detil-page.html', context)