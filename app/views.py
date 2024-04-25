from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
import os
import nltk
import pandas as pd
from nltk import ne_chunk, word_tokenize, pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags
import re
import configparser
from .models import PatentData




def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')







def extract_entities(text):
    config = configparser.ConfigParser()
    config_file = os.path.abspath('static/config.ini')
    print(config_file)
    config.read(config_file)

    entities = {
        'name': None,
        'age': None,
        'weight': None,
        'symptoms': None
    }

    # Extract name using regex pattern
    name_pattern = config.get('entity_recognition', 'name_pattern')
    match = re.search(name_pattern, text)
    if match:
        entities['name'] = match.group(2)
    # Extract age and weight using regex patterns
    age_pattern = config.get('entity_recognition', 'age_pattern')
    weight_pattern = config.get('entity_recognition', 'weight_pattern')
    age_match = re.search(age_pattern, text)
    weight_match = re.search(weight_pattern, text)
    if age_match:
        entities['age'] = age_match.group(2)
    if weight_match:
        entities['weight'] = weight_match.group(1)
    # Extract symptoms using keyword matching
    values = config.get('entity_recognition', 'symptoms_keywords').split(',')
    symptoms_keywords = [value.strip("[ ] '") for value in values]
    for keyword in symptoms_keywords:
        if keyword in text:
            entities['symptoms'] = keyword
            # break
    return entities



def highlight_entities(text, entities):
    highlighted_text = text
    for key, value in entities.items():
        if value:
            highlighted_text = highlighted_text.replace(value, f'*{value}*')
    return highlighted_text













@csrf_exempt
def save_recording(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        with open(f'static/{audio_file.name}', 'wb') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        return JsonResponse({'message': 'Recording saved successfully.'})
    return JsonResponse({'message': 'Failed to save recording.'}, status=400)




def index(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']


        if username == 'admin' and password == 'admin':
            return redirect('dashboard')


        else:
            message =  "Incorrect username or password !! "
            return render(request, 'login.html', {"message":message})



    return render(request, 'login.html')













def dashboard(request):

    if request.method == "POST":
        rectext = request.POST['rectext']
        entity = extract_entities(rectext)
        print(entity)

        if entity['name'] != None:
            PatentData(name=entity['name'], age=entity['age'], weight=entity['weight'], symptoms=entity['symptoms'], recdata=rectext).save()

        return render(request, 'dashboard.html',{"entity":entity, "rectext":rectext})
    
    return render(request, 'dashboard.html')






def patientlist(request):

    data = PatentData.objects.all()

    return render(request, 'patientlist.html',{"data":data})



def patientprofile(request,idd):

    pdata = PatentData.objects.get(id=idd)

    return render(request, 'patientprofile.html',{"pdata":pdata})




















def convert(request):
    recognizer = sr.Recognizer()
    # audio_file_path = os.path.abspath('static/recording.wav')
    audio_file_path = 'C:\\Users\\ajayo\\OneDrive\\Desktop\\alya\\django Implementation\\MedicalAssistant\\static\\recording.wav'


    
    print(audio_file_path)
    with sr.AudioFile(audio_file_path) as source:
        # Listen for the data (load audio to memory)
        audio_data = recognizer.record(source)

        # Recognize the speech in the audio data
        try:
            text = recognizer.recognize_google(audio_data)
            ttxt =  text
        except sr.UnknownValueError:
            ttxt = "Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            ttxt = "Could not request results from Speech Recognition service; {0}".format(e)
    
    return render(request, 'dashboard.html',{"text":ttxt})







