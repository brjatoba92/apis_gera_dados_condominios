import requests
import pandas as pd
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
LATITUDE = -9.6498   # Exemplo: Maceió
LONGITUDE = -35.7089
RADIUS = 55000  # em metros
KEYWORDS = [
    "edifício residencial",
    "condomínio",
    "residencial",
    "condomínio fechado",
    "torre residencial",
    "residencial clube",
    "apartamento prédio",
    "complexo de condomínio",
    "complexo de apartamentos",
    "Edifício de apartamentos mobiliados",
    "Complexo residencial",
    "Apartamentos",
    "Imobiliaria de aluguel de condomínios",
]

def buscar_places(keyword, lat, lng, radius):
    url_base = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": keyword,
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": API_KEY
    }

    resultados = []
    while True:
        response = requests.get(url_base, params=params)
        data = response.json()

        if response.status_code != 200:
            print("Erro na requisição:", response.status_code, data.get("error_message"))
            break

        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            print("Status da API:", data.get("status"), data.get("error_message", ""))
            break

        resultados.extend(data.get("results", []))

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        # Aguardar o token ficar válido (exigência da API)
        time.sleep(2)
        params = {
            "pagetoken": next_page_token,
            "key": API_KEY
        }

    return resultados

def detalhes_place(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    return response.json().get("result", {})

def main():
    todos_resultados = []

    for keyword in KEYWORDS:
        print(f"\n🔍 Buscando por: {keyword}")
        resultados = buscar_places(keyword, LATITUDE, LONGITUDE, RADIUS)
        print(f"✅ Encontrados {len(resultados)} resultados para '{keyword}'")

        for lugar in resultados:
            nome = lugar.get("name")
            endereco = lugar.get("formatted_address")
            place_id = lugar.get("place_id")
            
            telefone = ""
            if place_id:
                detalhes = detalhes_place(place_id)
                telefone = detalhes.get("formatted_phone_number", "")

            todos_resultados.append({
                "nome": nome,
                "endereco": endereco,
                "telefone": telefone
            })

            time.sleep(1)  # respeita limites da API

    # Remover duplicatas (nome + endereço)
    df = pd.DataFrame(todos_resultados).drop_duplicates(subset=["nome", "endereco"])
    df.to_csv("edificios_residenciais.csv", index=False)
    df.to_json("edificios_residenciais.json", orient="records", indent=4, force_ascii=False)

    print(f"\n💾 {len(df)} edifícios únicos salvos em CSV e JSON.")

if __name__ == "__main__":
    main()
