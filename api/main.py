import pymongo #Librería para comunicarse con la bd mongodb
from flask import Flask, jsonify, request #Flask es para levantar un servidor web. jsonify para poder retornar un json como respuesta al cliente. request permite capturar peticiones rest

#Función para crear conexión a la bd
def get_db_connection(uri):
	client = pymongo.MongoClient(uri) #Crear una conexión a la bd
	return client.cryptongo #Devolver bd cryptongo

app = Flask(__name__) #Crear un servidor web a partir del nombre del archivo ejecutado
db_connection = get_db_connection('mongodb://localhost:27017/') #Conexión a la bd

#Función para obtener lista de documentos a devolver
def get_documents():
	params = {} #Defino un diccionario de datos
	name = request.args.get('name', '') #Obtengo el campo "name", recibido por get. Si no existe, devuelve vacío
	limit = int(request.args.get('limit', 0)) #Obtengo el campo "limit", recibido por get. Si no existe, devuelve 0, omitiendo limit. Fuerzo conversión a entero

	if name: #Si existe "name"
		params.update({'name': name}) #Lo agrego al diccionario de datos

	cursor = db_connection.tickers.find( #Busco tickers
		params, #, según lo que recibí por get
		{'_id': 0, 'ticker_hash': 0} #Campos omitidos
	).limit(limit)

	return list(cursor) #convertir resultados de bd en una lista y devolverlo como respuesta a la petición

#Función para obtener el top20 de documentos
def get_top20():
	params = {} #Defino un diccionario de datos
	name = request.args.get('name', '') #Obtengo el campo "name", recibido por get. Si no existe, devuelve vacío
	limit = int(request.args.get('limit', 0)) #Obtengo el campo "limit", recibido por get. Si no existe, devuelve 0, omitiendo limit. Fuerzo conversión a entero

	if name: #Si existe "name"
		params.update({'name', name}) #Lo agrego al diccionario de datos

	params.update({'rank': {'$lte': 20}}) #Agrego condición para el find, inicando que el campo "rank" debe ser menor o igual a 20

	cursor = db_connection.tickers.find( #Busco tickers
		params, #, según lo que recibí por get
		{'_id': 0, 'ticker_hash': 0} #Campos omitidos
	).limit(limit)

	return list(cursor) #convertir resultados de bd en una lista y devolverlo como respuesta a la petición

#Función para eliminar un documento
def remove_currency():
	params = {} #Defino un diccionario de datos
	name = request.args.get('name', '') #Obtengo el campo "name", recibido por get. Si no existe, devuelve vacío

	if name: #Si existe "name"
		params.update({'name': name}) #Lo agrego al diccionario de datos
	else:
		return False

	return db_connection.tickers.delete_many( #Borro todos los documentos que coincidan con el dato recibido por get
		params
	).deleted_count #Retorna la cantidad de documentos borrados

@app.route("/") #Defino la ruta raíz para recibir peticiones
def index(): #Cuando alguien pida esta ruta, se ejecutará esta función
	return jsonify( #Retornará una respuesta en formato json
		{
			'name': 'Cryptongo API'
		}
	)

@app.route("/top20", methods=['GET']) #Defino ruta GET para top20
def top20(): #Se ejecutará esta función cuando alguien entre a esa ruta
	return jsonify(get_top20()) #Devuelvo un json con la lista de top20

@app.route("/tickers", methods=['GET', 'DELETE']) #Defino ruta para obtener o eliminar tickers, recibiendo petición por GET o DELETE
def tickers(): #Con la ruta, se ejecuta esta función
	if request.method == "GET": #Si el método consultado por la ruta, es GET
		return jsonify(get_documents()) #Devuelve un json con el resultado de tickers, según parámetros por get (Puede ser sin parámetros)
	elif request.method == "DELETE": #En cambio, si el método consultado es por DELETE
		result = remove_currency() #Se borran los tickers que coincidan con los parámetros recibidos por get (Los parámetros son obligatorios)
		if result > 0:
			return jsonify({ #Retornar un json con la respuesta
				'text': 'Documentos eliminados'
			}), 204 #Flask permite agregar otro parámetro al return, indicando el código de respuesta, en este caso, un "No hay contenido" (común en los borrados de datos)
		else:
			return jsonify({ #Retornar un json con la respuesta
				'error': 'No se encontraron documentos'
			}), 404 #Flask permite agregar otro parámetro al return, indicando el código de respuesta, en este caso, un "No encontrado"``