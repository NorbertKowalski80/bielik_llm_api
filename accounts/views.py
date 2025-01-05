import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from datetime import datetime  # Dodajemy import do obsługi dat

API_KEY = "LXguOlBBBzgnrFLvx6_1QYGm-Q2mhRGFd313S7k-B-Q"
BASE_URL = "https://bielik.cui.wroclaw.pl:8444/v1"


def home_view(request):
    # Pobierz historię z sesji lub ustaw jako pustą listę
    history = request.session.get("chat_history", [])
    return render(request, 'home.html', {"history": history})


@csrf_exempt
def ask_bielik(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            user_message = body.get("message", "")

            url = f"{BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "speakleash/Bielik-11B-v2.3-Instruct",
                "messages": [{"role": "user", "content": user_message}],
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                response_data = response.json()
                reply = response_data["choices"][0]["message"]["content"]

                # Formatowanie odpowiedzi w HTML (np. akapity, pogrubienie)
                formatted_reply = reply.replace("\n", "<br>")  # Zamiana nowych linii na HTML-owe łamania
                formatted_reply = formatted_reply.replace("###", "<h3>")  # Nagłówki
                formatted_reply = formatted_reply.replace("**", "<b>").replace("</b>", "</b>")  # Pogrubienie

                # Pobierz aktualną datę
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Zapisz zapytanie, odpowiedź i datę w historii
                history = request.session.get("chat_history", [])
                history.append({"question": user_message, "answer": formatted_reply, "date": current_date})
                request.session["chat_history"] = history  # Zaktualizuj sesję

                return JsonResponse({"reply": formatted_reply}, status=200)
            else:
                return JsonResponse(
                    {"error": f"Błąd API: {response.status_code}. Treść: {response.text}"},
                    status=response.status_code,
                )
        except requests.exceptions.ConnectionError:
            return JsonResponse({"error": "Nie udało się połączyć z serwerem."}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Metoda nieobsługiwana. Użyj POST."}, status=405)
