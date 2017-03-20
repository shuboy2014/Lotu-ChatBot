from pprint import pprint as pp
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
import requests
import apiai

ACCESS_TOKEN = 'EAAGOpHydMTkBAHGkuUZAzzsPUEqj7jxzeRFRL6oeZAE0LoqZBtR0LAMZBC1Au0FiPCgVvR8dIvM01tlpg5g0ZBZCxLzEo0WmkOwUwNhrKgPE3ZCs0NlHmBEYT3VjEtK0ij47QkQNCXh10JN3tbfubgMY8V9TpIcaEeKP1ZAeWbmwaAZDZD'
URL = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ACCESS_TOKEN
VERIFY_TOKEN = '958209560'
CLIENT_ACCESS_TOKEN = '57a3d57bb3e24e5aa4df1c353aedceea'


def get_reply(msg):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.session_id = "session"
    request.query = msg
    response = request.getresponse()
    response = json.loads(response.read().decode('utf-8'))
    return response["result"]["fulfillment"]["speech"]


def send_msg(fbid, msg):
    text = get_reply(msg)

    if text is None:
        text = "Sorry, I don’t Understand!"

    response = requests.post(
        URL,
        json.dumps({"recipient": {"id": fbid}, "message": {"text": str(text)}}),
        headers={"Content-Type": "application/json"}
    )

    return response.json()


class BotView(View):
    def get(self, *args, **kwargs):
        if self.request.GET.get('hub.verify_token', '') == VERIFY_TOKEN:
            print("Facebook Ping!")
            return HttpResponse(self.request.GET.get('hub.challenge', 'Not available'))
        else:
            print("Anonymous Ping!")
            return JsonResponse({"hub.verify_token": "Invalid Token"})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return View.dispatch(self, *args, **kwargs)

    def post(self, *args, **kwargs):
        msg = json.loads(self.request.body.decode('utf-8'))
        for entry in msg['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    send_msg(message['sender']['id'], message['message']['text'])
        return HttpResponse()
