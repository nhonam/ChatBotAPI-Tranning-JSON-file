import random
import json
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
from flask import Flask, jsonify, request

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r'  ,encoding='utf-8') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Ecommerce chatbot AI"
print("Let's chat! (type 'quit' to exit)")

app = Flask(__name__)
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message='Hello, World!')

@app.route('/api/add', methods=['POST'])
def add_numbers():
        data = request.get_json()
        question = data['question']
    # while True:
    # sentence = "do you use credit cards?"
        sentence = question
        # if sentence == "quit":
        #     break

        sentence = tokenize(sentence)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)

        tag = tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]
        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    # result = num1 + "123"
                    return jsonify(result=f"{random.choice(intent['responses'])}")
                    # print(f"{bot_name}: {random.choice(intent['responses'])}")
        else:
            # result = num1 + "123"
            return jsonify(result="I do not understand..")
            # print(f"{bot_name}: I do not understand...")
      
if __name__ == '__main__':
    app.run()
