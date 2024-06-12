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
from .wordCloudGenerator import generate_wordcloud, load_wordcloud

# Import paginator
from django.core.paginator import Paginator

# Create your views here.
def load_stop_words():
    try:
        stop_words = ['ada', 'adalah', 'adanya', 'adapun', 'agak', 'agaknya', 'agar', 'akan', 'akankah', 'akhir', 'akhiri', 'akhirnya', 'aku', 'akulah', 'amat', 'amatlah', 'anda', 'andalah', 'antar', 'antara', 'antaranya', 'apa', 'apaan', 'apabila', 'apakah', 'apalagi', 'apatah', 'artinya', 'asal', 'asalkan', 'atas', 'atau', 'ataukah', 'ataupun', 'awal', 'awalnya', 'bagai', 'bagaikan', 'bagaimana', 'bagaimanakah', 'bagaimanapun', 'bagi', 'bagian', 'bahkan', 'bahwa', 'bahwasanya', 'baik', 'bakal', 'bakalan', 'balik', 'banyak', 'bapak', 'baru', 'bawah', 'beberapa', 'begini', 'beginian', 'beginikah', 'beginilah', 'begitu', 'begitukah', 'begitulah', 'begitupun', 'bekerja', 'belakang', 'belakangan', 'belum', 'belumlah', 'benar', 'benarkah', 'benarlah', 'berada', 'berakhir', 'berakhirlah', 'berakhirnya', 'berapa', 'berapakah', 'berapalah', 'berapapun', 'berarti', 'berawal', 'berbagai', 'berdatangan', 'beri', 'berikan', 'berikut', 'berikutnya', 'berjumlah', 'berkali-kali', 'berkata', 'berkehendak', 'berkeinginan', 'berkenaan', 'berlainan', 'berlalu', 'berlangsung', 'berlebihan', 'bermacam', 'bermacam-macam', 'bermaksud', 'bermula', 'bersama', 'bersama-sama', 'bersiap', 'bersiap-siap', 'bertanya', 'bertanya-tanya', 'berturut', 'berturut-turut', 'bertutur', 'berujar', 'berupa', 'besar', 'betul', 'betulkah', 'biasa', 'biasanya', 'bila', 'bilakah', 'bisa', 'bisakah', 'boleh', 'bolehkah', 'bolehlah', 'buat', 'bukan', 'bukankah', 'bukanlah', 'bukannya', 'bulan', 'bung', 'cara', 'caranya', 'cukup', 'cukupkah', 'cukuplah', 'cuma', 'dahulu', 'dalam', 'dan', 'dapat', 'dari', 'daripada', 'datang', 'dekat', 'demi', 'demikian', 'demikianlah', 'dengan', 'depan', 'di', 'dia', 'diakhiri', 'diakhirinya', 'dialah', 'diantara', 'diantaranya', 'diberi', 'diberikan', 'diberikannya', 'dibuat', 'dibuatnya', 'didapat', 'didatangkan', 'digunakan', 'diibaratkan', 'diibaratkannya', 'diingat', 'diingatkan', 'diinginkan', 'dijawab', 'dijelaskan', 'dijelaskannya', 'dikarenakan', 'dikatakan', 'dikatakannya', 'dikerjakan', 'diketahui', 'diketahuinya', 'dikira', 'dilakukan', 'dilalui', 'dilihat', 'dimaksud', 'dimaksudkan', 'dimaksudkannya', 'dimaksudnya', 'diminta', 'dimintai', 'dimisalkan', 'dimulai', 'dimulailah', 'dimulainya', 'dimungkinkan', 'dini', 'dipastikan', 'diperbuat', 'diperbuatnya', 'dipergunakan', 'diperkirakan', 'diperlihatkan', 'diperlukan', 'diperlukannya', 'dipersoalkan', 'dipertanyakan', 'dipunyai', 'diri', 'dirinya', 'disampaikan', 'disebut', 'disebutkan', 'disebutkannya', 'disini', 'disinilah', 'ditambahkan', 'ditandaskan', 'ditanya', 'ditanyai', 'ditanyakan', 'ditegaskan', 'ditujukan', 'ditunjuk', 'ditunjuki', 'ditunjukkan', 'ditunjukkannya', 'ditunjuknya', 'dituturkan', 'dituturkannya', 'diucapkan', 'diucapkannya', 'diungkapkan', 'dong', 'dua', 'dulu', 'empat', 'enggak', 'enggaknya', 'entah', 'entahlah', 'guna', 'gunakan', 'hal', 'hampir', 'hanya', 'hanyalah', 'hari', 'harus', 'haruslah', 'harusnya', 'hendak', 'hendaklah', 'hendaknya', 'hingga', 'ia', 'ialah', 'ibarat', 'ibaratkan', 'ibaratnya', 'ibu', 'ikut', 'ingat', 'ingat-ingat', 'ingin', 'inginkah', 'inginkan', 'ini', 'inikah', 'inilah', 'itu', 'itukah', 'itulah', 'jadi', 'jadilah', 'jadinya', 'jangan', 'jangankan', 'janganlah', 'jauh', 'jawab', 'jawaban', 'jawabnya', 'jelas', 'jelaskan', 'jelaslah', 'jelasnya', 'jika', 'jikalau', 'juga', 'jumlah', 'jumlahnya', 'justru', 'kala', 'kalau', 'kalaulah', 'kalaupun', 'kalian', 'kami', 'kamilah', 'kamu', 'kamulah', 'kan', 'kapan', 'kapankah', 'kapanpun', 'karena', 'karenanya', 'kasus', 'kata', 'katakan', 'katakanlah', 'katanya', 'ke', 'keadaan', 'kebetulan', 'kecil', 'kedua', 'keduanya', 'keinginan', 'kelamaan', 'kelihatan', 'kelihatannya', 'kelima', 'keluar', 'kembali', 'kemudian', 'kemungkinan', 'kemungkinannya', 'kenapa', 'kepada', 'kepadanya', 'kesampaian', 'keseluruhan', 'keseluruhannya', 'keterlaluan', 'ketika', 'khususnya', 'kini', 'kinilah', 'kira', 'kira-kira', 'kiranya', 'kita', 'kitalah', 'kok', 'kurang', 'lagi', 'lagian', 'lah', 'lain', 'lainnya', 'lalu', 'lama', 'lamanya', 'lanjut', 'lanjutnya', 'lebih', 'lewat', 'lima', 'luar', 'macam', 'maka', 'makanya', 'makin', 'malah', 'malahan', 'mampu', 'mampukah', 'mana', 'manakala', 'manalagi', 'masa', 'masalah', 'masalahnya', 'masih', 'masihkah', 'masing', 'masing-masing', 'mau', 'maupun', 'melainkan', 'melakukan', 'melalui', 'melihat', 'melihatnya', 'memang', 'memastikan', 'memberi', 'memberikan', 'membuat', 'memerlukan', 'memihak', 'meminta', 'memintakan', 'memisalkan', 'memperbuat', 'mempergunakan', 'memperkirakan', 'memperlihatkan', 'mempersiapkan', 'mempersoalkan', 'mempertanyakan', 'mempunyai', 'memulai', 'memungkinkan', 'menaiki', 'menambahkan', 'menandaskan', 'menanti', 'menanti-nanti', 'menantikan', 'menanya', 'menanyai', 'menanyakan', 'mendapat', 'mendapatkan', 'mendatang', 'mendatangi', 'mendatangkan', 'menegaskan', 'mengakhiri', 'mengapa', 'mengatakan', 'mengatakannya', 'mengenai', 'mengerjakan', 'mengetahui', 'menggunakan', 'menghendaki', 'mengibaratkan', 'mengibaratkannya', 'mengingat', 'mengingatkan', 'menginginkan', 'mengira', 'mengucapkan', 'mengucapkannya', 'mengungkapkan', 'menjadi', 'menjawab', 'menjelaskan', 'menuju', 'menunjuk', 'menunjuki', 'menunjukkan', 'menunjuknya', 'menurut', 'menuturkan', 'menyampaikan', 'menyangkut', 'menyatakan', 'menyebutkan', 'menyeluruh', 'menyiapkan', 'merasa', 'mereka', 'merekalah', 'merupakan', 'meski', 'meskipun', 'meyakini', 'meyakinkan', 'minta', 'mirip', 'misal', 'misalkan', 'misalnya', 'mula', 'mulai', 'mulailah', 'mulanya', 'mungkin', 'mungkinkah', 'nah', 'naik', 'namun', 'nanti', 'nantinya', 'nyaris', 'nyatanya', 'oleh', 'olehnya', 'pada', 'padahal', 'padanya', 'pak', 'paling', 'panjang', 'pantas', 'para', 'pasti', 'pastilah', 'penting', 'pentingnya', 'per', 'percuma', 'perlu', 'perlukah', 'perlunya', 'pernah', 'persoalan', 'pertama', 'pertama-tama', 'pertanyaan', 'pertanyakan', 'pihak', 'pihaknya', 'pukul', 'pula', 'pun', 'punya', 'rasa', 'rasanya', 'rata', 'rupanya', 'saat', 'saatnya', 'saja', 'sajalah', 'saling', 'sama', 'sama-sama', 'sambil', 'sampai', 'sampai-sampai', 'sampaikan', 'sana', 'sangat', 'sangatlah', 'satu', 'saya', 'sayalah', 'se', 'sebab', 'sebabnya', 'sebagai', 'sebagaimana', 'sebagainya', 'sebagian', 'sebaik', 'sebaik-baiknya', 'sebaiknya', 'sebaliknya', 'sebanyak', 'sebegini', 'sebegitu', 'sebelum', 'sebelumnya', 'sebenarnya', 'seberapa', 'sebesar', 'sebetulnya', 'sebisanya', 'sebuah', 'sebut', 'sebutlah', 'sebutnya', 'secara', 'secukupnya', 'sedang', 'sedangkan', 'sedemikian', 'sedikit', 'sedikitnya', 'seenaknya', 'segala', 'segalanya', 'segera', 'seharusnya', 'sehingga', 'seingat', 'sejak', 'sejauh', 'sejenak', 'sejumlah', 'sekadar', 'sekadarnya', 'sekali', 'sekali-kali', 'sekalian', 'sekaligus', 'sekalipun', 'sekarang', 'sekarang', 'sekecil', 'seketika', 'sekiranya', 'sekitar', 'sekitarnya', 'sekurang-kurangnya', 'sekurangnya', 'sela', 'selain', 'selaku', 'selalu', 'selama', 'selama-lamanya', 'selamanya', 'selanjutnya', 'seluruh', 'seluruhnya', 'semacam', 'semakin', 'semampu', 'semampunya', 'semasa', 'semasih', 'semata', 'semata-mata', 'semaunya', 'sementara', 'semisal', 'semisalnya', 'sempat', 'semua', 'semuanya', 'semula', 'sendiri', 'sendirian', 'sendirinya', 'seolah', 'seolah-olah', 'seorang', 'sepanjang', 'sepantasnya', 'sepantasnyalah', 'seperlunya', 'seperti', 'sepertinya', 'sepihak', 'sering', 'seringnya', 'serta', 'serupa', 'sesaat', 'sesama', 'sesampai', 'sesegera', 'sesekali', 'seseorang', 'sesuatu', 'sesuatunya', 'sesudah', 'sesudahnya', 'setelah', 'setempat', 'setengah', 'seterusnya', 'setiap', 'setiba', 'setibanya', 'setidak-tidaknya', 'setidaknya', 'setinggi', 'seusai', 'sewaktu', 'siap', 'siapa', 'siapakah', 'siapapun', 'sini', 'sinilah', 'soal', 'soalnya', 'suatu', 'sudah', 'sudahkah', 'sudahlah', 'supaya', 'tadi', 'tadinya', 'tahu', 'tahun', 'tak', 'tambah', 'tambahnya', 'tampak', 'tampaknya', 'tandas', 'tandasnya', 'tanpa', 'tanya', 'tanyakan', 'tanyanya', 'tapi', 'tegas', 'tegasnya', 'telah', 'tempat', 'tengah', 'tentang', 'tentu', 'tentulah', 'tentunya', 'tepat', 'terakhir', 'terasa', 'terbanyak', 'terdahulu', 'terdapat', 'terdiri', 'terhadap', 'terhadapnya', 'teringat', 'teringat-ingat', 'terjadi', 'terjadilah', 'terjadinya', 'terkira', 'terlalu', 'terlebih', 'terlihat', 'termasuk', 'ternyata', 'tersampaikan', 'tersebut', 'tersebutlah', 'tertentu', 'tertuju', 'terus', 'terutama', 'tetap', 'tetapi', 'tiap', 'tiba', 'tiba-tiba', 'tidak', 'tidakkah', 'tidaklah', 'tiga', 'tinggi', 'toh', 'tunjuk', 'turut', 'tutur', 'tuturnya', 'ucap', 'ucapnya', 'ujar', 'ujarnya', 'umum', 'umumnya', 'ungkap', 'ungkapnya', 'untuk', 'usah', 'usai', 'waduh', 'wah', 'wahai', 'waktu', 'waktunya', 'walau', 'walaupun', 'wong', 'yaitu', 'yakin', 'yakni', 'yang']
        teks_tambahan = ['assalamualaikum', 'warahmatullahi', 'wabarakatuh', 'wassalamualikum']
        stop_words.extend(teks_tambahan)
        return stop_words
    except FileNotFoundError:
        print("File stopwords tidak ditemukan.")
        return []

stop_words = load_stop_words()

def main(request):
    transcriptions = Transcribe.objects.all().order_by('-id')

    # Set up pagination
    p = Paginator(transcriptions, 3)
    page = request.GET.get('page')
    transcriptions = p.get_page(page)
    nums = "a" * transcriptions.paginator.num_pages

    transcription_sentences = {}
    wordclouds = {}

    for transcribe in transcriptions:
        doc = [transcribe.trans_result]  # Assuming the transcribe model has a trans_result field

        # Debugging output
        # print(f"Generating word cloud for transcription ID {transcribe.id} with content: {doc}")

        wordcloud_image = load_wordcloud(doc, stop_words)
        # print(wordcloud_image)

        # if wordcloud_image:
        #     wordclouds[transcribe.id] = wordcloud_image  # Save the wordcloud per transcription id
        # else:
        #     wordclouds[transcribe.id] = None  # Handle the case where wordcloud generation failed

    context = {
        'transcriptions': transcriptions,
        'nums': nums,
        'wordclouds': wordclouds  # Pass wordclouds to the context
    }
    return render(request, 'dashboard.html', context)

def other_view(request):
    transcriptions = Transcribe.objects.all().order_by('-id')
    context = {
        'transcriptions': transcriptions
    }
    return render(request, 'other.html', context)

def detil_view(request, pk):
    transcribe = get_object_or_404(Transcribe, pk=pk)
    transcriptions = Transcribe.objects.all().order_by('-id')
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

    # print(f"Named Entities: {named_entities}")

    # Generate wordcloud
    docs = [sentence.sentence for sentence in sentences]
    image_base64 = load_wordcloud(docs, stop_words)

    context = {
        'transcribe': transcribe,
        'sentences': sentences,
        'named_entities': entity_list,
        'wordcloud': image_base64,
        'transcriptions': transcriptions
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
    trans = Transcribe.objects.all().order_by('-id')[:4]

    user = request.user 
    transcription = None
    error = None
    sentences_with_sentiment = []
    named_entities = []
    file_name = None
    image_base64 = None

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
            image_base64 = load_wordcloud(transcription, stop_words)
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
                    'im'
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
                    'user':user,
                    'trans': trans
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
                        'user':user,
                        'wordcloud': image_base64,
                        'trans': trans
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
        'user':user,
        'wordcloud': image_base64,
        'trans':trans
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
