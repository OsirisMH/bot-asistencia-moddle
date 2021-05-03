import json
import os

data_file = open("../data.json", "r")
data = json.load(data_file)
data_file.close()

data = data['materias']['1']['nombre']

print(data.decode('utf-8'))