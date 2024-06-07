from .models import Transcribe, Sentences
from django.db.models.signals import post_save
from django.dispatch import receiver
import nltk

nltk.download('punkt')

# @receiver(post_save, sender=Transcribe)
# def create_sentences(sender, instance, created, **kwargs):
#     if created:
#         # Tokenize the trans_result into sentences
#         sentences = nltk.tokenize.sent_tokenize(instance.trans_result)
#         for sentence in sentences:
#             Sentences.objects.create(id_trans=instance, sentence=sentence)

# @receiver(post_save, sender=Sentences)
# def update_sa_tag(sender, instance, created, **kwargs):
#     max_value = max(instance.positive, instance.negative, instance.neutral)

#     # Set sa_tag based on the maximum value
#     if instance.positive == max_value:
#         instance.sa_tag = Sentences.SATag.POSITIVE
#     elif instance.negative == max_value:
#         instance.sa_tag = Sentences.SATag.NEGATIVE
#     else:
#         instance.sa_tag = Sentences.SATag.NEUTRAL
    
#     instance.save(update_fields=['sa_tag'])