from click import Choice, option
import mysql.connector
from mysql.connector import Error
from sql import create_connection
from sql import execute_query
from sql import execute_read_query
import datetime
from datetime import date
import flask
from flask import jsonify
from datetime import date
from flask import request

conn = create_connection('cis3368spring22.conwletcnyv5.us-east-2.rds.amazonaws.com', 'RaulG0722', 'Chidori151', 'CIS3368Spring22db')

app = flask.Flask(__name__) #sets up the application
app.config["DEBUG"] = True #allow to show errors in browser

@app.route('/', methods=['GET']) # default url without any routing as GET request
def home():
    return "<h1> This API manages zoo animal data and logs </h1>"

@app.route('/api/zoo/all', methods = ['GET']) #get all rows from zoo table
def all_animals():
    animals_sql = "select * FROM zoo"
    animals = execute_read_query(conn, animals_sql)
    return jsonify(animals)

@app.route('/api/zoo', methods = ['GET'])
def single_animal():
    if 'id' in request.args: #only if an id is provided as an argument, proceed
        id = int(request.args['id'])
    else:
        return 'ERROR: No ID provided!'
    animals_sql = "select * FROM zoo"
    animals = execute_read_query(conn, animals_sql)
    results = []
    for animal in animals:
        if animal['id'] == id:
            results.append(animal)
    return jsonify(results)

@app.route('/api/zoo/add', methods = ['POST'])
def add_animal(): 
    animal = request.json['animal'] #requests data for new table entry
    name = request.json['name']
    gender = request.json['gender']
    subtype = request.json['subtype']
    age = request.json['age']
    color = request.json['color']
    new_animal = "INSERT INTO zoo (animal, name, gender, subtype, age, color) VALUES ('%s', '%s', '%s', '%s', %s, '%s')" % (animal, name, gender, subtype, age, color)
    execute_query(conn, new_animal)
    #sql to read table in order to get the last value of the index of the array
    read_sql = "SELECT * FROM zoo"
    animals = execute_read_query(conn, read_sql)
    comment = "A '%s' by the name of '%s' was added to the zoo table" % (animal, name)
    animalid = animals[-1].get("animalid")
    date_log = date.today()
    new_log = "INSERT INTO log (date, animalid, comment) VALUES ('%s', '%s' '%s')" % (date_log, animalid, comment)
    execute_query(conn, new_log)
    return 'Successfully added animal'

@app.route('/api/zoo/put', methods = ['PUT'])
def put_animal():
    #requests id for animal that needs to get updated
    id = request.json['animalid']
    animal = request.json['animal']
    name = request.json['name']
    gender = request.json['gender']
    subtype = request.json['subtype']
    age = request.json['age']
    color = request.json['color']
    update_sql = "UPDATE zoo SET animal = '%s', name = '%s', gender = '%s', subtype = '%s', age = %s, color = '%s' WHERE animalid = %s" % (animal, name, gender, subtype, age, color, id)
    execute_query(conn, update_sql)
    return 'Successfully updated animal'

@app.route('/api/zoo/delanimal', methods = ['DELETE'])
def del_animal():
    animalid = request.json['animalid2Bdel'] # requests id and animal type in order to delete the animal from zoo table
    animal = request.json['animal']
    name = request.json['name']
    del_sql = "DELETE FROM zoo where id = %s AND animal = '%s' " % (animalid, animal)
    execute_query(conn, del_sql)
    comment = "A '%s' by the name of '%s' was deleted from the zoo table" % (animal, name)
    date_log = date.today()
    #sql to create entry for the log table
    new_log = "INSERT INTO log (date, animalid, comment) VALUES ('%s', '%s' '%s')" % (date_log, animalid, comment)
    execute_query(conn, new_log)
    return 'Successfully deleted animal'

@app.route('/api/logs/all',  methods = ['GET'])
def read_logs():
    #gets all rows from the logs table
    logs_sql = "select * FROM logs"
    logs = execute_read_query(conn, logs_sql)
    return jsonify(logs)

@app.route('/api/logs/reset', methods = ['DELETE'])
def del_logs():
    #asks for confirmation in order to delete all records from the table
    confirmation = request.json['confirmation']
    if confirmation == "TRUE":
        dellogs_sql = "DELETE FROM logs"
        execute_query(conn, dellogs_sql)
    else:
        return 'Need confirmation TRUE to delete all records'
    return 'Successully deleted logs'
app.run()