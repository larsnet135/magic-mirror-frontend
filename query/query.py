import requests
HOST_IP = "127.0.0.1"
PORT = 8000

USER_INPUT = "Whatever thingy"
payload = {'user_input': f'{USER_INPUT}'}

r = requests.get(f'http://{HOST_IP}:{PORT}/chatbot', params=payload)

data = r.json()
response_string = data['chatbot_response']['text']

print(response_string)


def write_response_file(response: str) -> None:
    with open("chatbot_response.txt", "w") as outputfile:
        outputfile.write(response)

write_response_file(response_string)
