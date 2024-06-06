# from .models import Transcribe, Sentences
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# import nltk

# nltk.download('punkt')

# @receiver(post_save, sender=Transcribe)
# def create_sentences(sender, instance, created, **kwargs):
#     if created:
#         # Tokenize the trans_result into sentences
#         sentences = nltk.tokenize.sent_tokenize(instance.trans_result)
#         for sentence in sentences:
#             Sentences.objects.create(id_trans=instance, sentence=sentence)