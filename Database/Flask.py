#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://estanis:estanis@cluster0.nsd3vad.mongodb.net/?retryWrites=true&w=majority")
db = client["IOT"]
collection = db["INFO_ATUADOR"]

@app.route("/atuador", methods=["GET"])
def get_atuador():
    atuador = collection.find()
    output = []
    for a in atuador:
        output.append({"_id": str(a["_id"]), "nome": a["nome"], "status": a["status"]})
    return jsonify(output)

@app.route("/atuador/<id>", methods=["GET"])
def get_atuador_by_id(id):
    atuador = collection.find_one({"_id": ObjectId(id)})
    return jsonify({"_id": str(atuador["_id"]), "nome": atuador["nome"], "status": atuador["status"]})

@app.route("/atuador", methods=["POST"])
def add_atuador():
    atuador = collection.insert_one(request.json)
    return jsonify({"_id": str(atuador.inserted_id)})

@app.route("/atuador/<id>", methods=["PUT"])
def update_atuador(id):
    collection.update_one({"_id": ObjectId(id)}, {"$set": request.json})
    return jsonify({"message": "Atuador atualizado com sucesso!"})

@app.route("/atuador/<id>", methods=["DELETE"])
def delete_atuador(id):
    collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Atuador deletado com sucesso!"})

app.run(debug=True)
