from flask import Flask, request, jsonify, redirect, Response, render_template
import droneDataController as droneCont
import database as data
app= Flask(__name__)

    


@app.route('/addDrone', methods = ['POST'])
def addDrone():

    d= request.get_json()
    errors,drone = droneCont.addDrone(d)
    data = {
        'errors':errors,
        'data':drone,
    }
    if (drone == 'error'):
        
        return Response(f"errors: {errors}", status=500, mimetype='application/json')
    else:
        return jsonify(data)



@app.route('/receiveTelemetry', methods = ['POST'])
def receiveTelemetry():

    d = request.get_json()
    errors, drone = droneCont.receiveTelemetry(d)

    data = {
        'errors':errors,
        'data':drone
    }

    if (drone == 'error'):

        return Response(f"errors: {errors}", status=500, mimetype='application/json')
    else:
        return jsonify(data)

@app.route('/drones', methods = ['GET'])
def allDrones():
    return render_template('drones.html', data = data.drone)

#@app.route('/drone/<id>')
#def drone():
#    for x in data.droneTelemetry:
        


@app.route('/test', methods = ['GET'])
def test():
    return jsonify(data.droneTelemetry)