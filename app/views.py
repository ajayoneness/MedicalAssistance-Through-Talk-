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



weight_patterns = [r"I am (\d+) kilograms heavy.", r"My weight\? (\d+) kg\.", r"My scale shows (\d+) kg\.", r"Approximately (\d+) kilograms is my weight\.", r"My current weight reads (\d+) kg\.",r"I weigh in at (\d+) kg\.", r"My weight hovers around (\d+) kg\.", r"I'm (\d+) kilos on the scale\.", r"My weight\? (\d+) kilos\.", r"The scale indicates (\d+) kg\.", r"I weigh around (\d+) kilograms", r"I measure (\d+) kilograms\."]
name_patterns = [r"I am ([A-Z][a-z]+)",r"I am ([A-Z][a-z]+ [A-Z][a-z]+)", r"I'm ([A-Z][a-z]+ [A-Z][a-z]+)", r"I'm ([A-Z][a-z]+)", r"I go by the name ([A-Z][a-z]+).", r"I go by the name ([A-Z][a-z]+ [A-Z][a-z]+).", r"My name is ([A-Z][a-z]+).",r"My name is ([A-Z][a-z]+[A-Z][a-z]+).", r"Call me ([A-Z][a-z]+).", r"Call me ([A-Z][a-z]+[A-Z][a-z]+).", r"You can address me as ([A-Z][a-z]+).",r"You can address me as ([A-Z][a-z]+,[A-Z][a-z]+).", r"People know me as ([A-Z][a-z]+).", r"I respond to ([A-Z][a-z]+).", r"The name I carry is ([A-Z][a-z]+).", r"I identify myself as ([A-Z][a-z]+).", r"My name, ([A-Z][a-z]+), is what I go by.", r"Known by the name ([A-Z][a-z]+).", r"([A-Z][a-z]+) is my given name.", r"My name? It's ([A-Z][a-z]+).", r"You may know me as ([A-Z][a-z]+).", r"Refer to me as ([A-Z][a-z]+).", r"The name I respond to is ([A-Z][a-z]+)."]
age_patterns = [r"I'm (\d+) years old", r"I am (\d+) years old", r"My age is (\d+).", r"I'm (\d+) years of age.", r"I am (\d+) years old.", r"Age: (\d+).", r"(\d+) years is my age.", r"I've lived for (\d+) years.", r"My current age is (\d+).", r"I'm in my (\d+)th year.", r"I'm turning (\d+) this year.", r"I've been alive for (\d+) years.", r"I've reached (\d+) years.", r"My age? (\d+).", r"(\d+) is my age.", r"I've seen (\d+) birthdays."]
symptoms_keywords = ['sharp pains', 'headache', 'neck']
medicine_keywords = ['paracetamol', 'dolo', 'citrazine', 'painkiller', 'Aspirin']
allergy_patterns = [r"Allergies? I have a reaction to ([A-Za-z]+).", r"([A-Za-z]+) triggers my allergies.", r"My body reacts badly to ([A-Za-z]+).", r"I suffer from an allergy to ([A-Za-z]+).", r"([A-Za-z]+) causes an allergic response in me.", r"I'm sensitive to ([A-Za-z]+).", r"I am sensitive to ([A-Za-z]+).", r"Allergic reaction? It happens with ([A-Za-z]+).", r"I have an allergy to ([A-Za-z]+).", r"My system can't handle ([A-Za-z]+).", r"([A-Za-z]+) sets off my allergies.", r"I'm intolerant to ([A-Za-z]+).", r"I amm intolerant to ([A-Za-z]+).", r"My allergies act up with ([A-Za-z]+).", r"I'm prone to allergic reactions from ([A-Za-z]+).", r"I react badly to ([A-Za-z]+).", r"I have a sensitivity to ([A-Za-z]+)."]
previous_medication_pattern = [r"In the past, I've taken medication for (\w+).", r"My medical history includes treatment with (\w+)." , r"I've been prescribed (\w+) before." , r"Previous medications I've used include (\w+)." , r"I have a history of taking (\w+) as medication." , r"(\w+) was part of my previous treatment plan." , r"I've been on medication for (\w+) in the past." , r"My past prescriptions have included (\w+)." , r"I've taken (\w+) medication before." , r"I've been treated with (\w+) before." , r"In previous treatments, I've used (\w+) as medication." , r"My medical records show a history of (\w+) medication." , r"I've had experience with (\w+) as part of my treatment." , r"(\w+) has been part of my medication regimen in the past." , r"My previous medical history includes using (\w+) as medication."]
previous_medication = ["Paracetamol", "Ibuprofen", "Aspirin", "Lisinopril", "Simvastatin", "Metformin", "Amoxicillin","Omeprazole","Atorvastatin","Levothyroxine","Losartan","Metoprolol","Gabapentin","Prednisone","Citalopram","Albuterol","Sertraline","Hydrochlorothiazide","Fluoxetine","Amlodipine"]





def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')






def extract_entities(text):
    entities = {
        'name': None,
        'age': None,
        'weight': None,
        'symptoms': None,
        'medicine': None,
        'allergy': None,
        'previous_medication': None,

    }
    # name pattern
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            entities['name'] = match.group(1)

    for we_pattern in weight_patterns:
        weight_match = re.search(we_pattern, text)
        # print("Weight_match:- ", weight_match)
        if weight_match:
            entities['weight'] = weight_match.group(1)

    for age in age_patterns:
        age_match = re.search(age, text)
        if age_match:
            entities['age'] = age_match.group(1)

    for allergy in allergy_patterns:
        allergy_match = re.search(allergy, text)
        if allergy_match:
            entities['allergy'] = allergy_match.group(1)
    for symptoms in symptoms_keywords:
        if symptoms in text:
            entities['symptoms'] = symptoms

    # for prev_med in previous_medication_pattern:
    #     medicine_match = re.search(prev_med, text)
    #     # print(medicine_match)
    #     if medicine_match:
    #         entities['previous_medication'] = medicine_match.group(1)

    for prev_med in previous_medication:
        # medicine_match = re.search(prev_med, text)
        # print(medicine_match)
        if prev_med in text:
            entities['previous_medication'] = prev_med

    for medicine in medicine_keywords:
        if medicine in text:
            entities['medicine'] = medicine

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


        if username == 'admin' and password == 'codeaj':
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


            pdata = PatentData(name=entity['name'], age=entity['age'],medicine=entity['medicine'], allergy=entity['allergy'], previous_medication=entity['previous_medication'], weight=entity['weight'], symptoms=entity['symptoms'], recdata=rectext)
            pdata.save()

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







