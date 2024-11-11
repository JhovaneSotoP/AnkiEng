import requests
import json
import requests
import urllib.parse
from gtts import gTTS
import os
import time


# URL de AnkiConnect
anki_url = "http://localhost:8765"

# Función para enviar solicitudes a AnkiConnect
def invoke(action, params=None):
    return requests.post(anki_url, json={
        "action": action,
        "version": 6,
        "params": params
    }).json()

# 1. Crear un mazo
def create_deck(deck_name):
    result = invoke("createDeck", {"deck": deck_name})
    if result.get("error") is None:
        print(f"Mazo '{deck_name}' creado.")
    else:
        print(f"Error al crear el mazo: {result['error']}")

# 2. Agregar una tarjeta al mazo
def add_card(deck_name, word, ipa,audio_path,definitions,tipo):
    note = {
        "deckName": deck_name,
        "modelName": "VocabularioEN",  # Modelo de la tarjeta (e.g., "Basic", "Basic (and reversed card)", etc.)
        "fields": {
            "Palabra": word,
            "Pronuciacion": ipa,
            "Audio":audio_path,
            "Definiciones":definitions,
            "tipo":tipo
        },
        "tags": [],  # Puedes añadir etiquetas opcionales
        "options": {
            "allowDuplicate": True
        }
    }

    result = invoke("addNote", {"note": note})
    if result.get("error") is None:
        print(f"Tarjeta {word} creada correctamente")
    else:
        print(f"Error al añadir la tarjeta: {result['error']}")

def crearTarjeta(data):
  for n in data["category"].keys():
    mazo=f"Vocabulary::{n.capitalize()}"
    create_deck(mazo)

    definicion=""

    for j in data["category"][n]:
        if j["example"]=="":
            definicion+=f"<li>{j["definition"]}</li><br>"
        else:
            definicion+=f"<li>{j["definition"]}<br><b>Example:</b> {j["example"]}</li><br>"
    
    definicion=f"<ol>{definicion}</ol>"

    add_card(mazo,data["word"],str(data["phonetic"]),data["audio"],definicion,n.capitalize())


url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def extraerData(frase):
  
  print(f"Buscando {frase} en el diccionario...")
  url_final=url+urllib.parse.quote(frase)
  solicitud=requests.get(url_final)
  
  if solicitud.status_code==200:
    print(f"{frase} localizada")
    json=solicitud.json()[0]
    tarjeta={}

    tarjeta.update({"word":json["word"].capitalize()})

    if "phonetic" in json.keys():
      tarjeta.update({"phonetic":json["phonetic"]})
    else:
      tarjeta.update({"phonetic":""})
    
    tarjeta.update({"category":{}})
    for n in json["meanings"]:
      
      try:
        category=n['partOfSpeech']
        
        tarjeta["category"].update({category:[]})
        for k in n['definitions']:
          definition=k['definition']

          if "example" in k.keys():
            example=k["example"]
          else:
            example=""
          tarjeta["category"][category].append({"definition":definition,"example":example})

      except:
        tarjeta.update({"category":{"":{"definition":"","example":""}}})
    print("Datos extraidos...")
    tts = gTTS(text=frase, lang='en')
    path="C:/Users/adria/AppData/Roaming/Anki2/Usuario 1/collection.media/"
    audio_file = path+frase.replace(" ", "_") + ".mp3"
    tts.save(audio_file)
    print(f"Audio guardado en {audio_file}")
    # Reproducir el audio (opcional)
    #os.system(f"start {audio_file}")
    tarjeta.update({"audio":frase.replace(" ", "_") + ".mp3"})

    crearTarjeta(tarjeta)

    
    
  else:
    print("Request failed")


while(1):
    os.system("CLS")
    dato= input("Ingresa una palabra: ")
    if dato.upper()=="P":
        break
    try:
        busca=dato.split(",")
        for n in busca:
          extraerData(n)
        time.sleep(1)
    except:
        print("Error intenta de nuevo")