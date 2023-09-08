

#Test for add drone function
curl -X POST localhost:5000/addDrone -H "Content-Type: application/json" -d '{"droneID":"5471-2153-8745-0784","name":"demo drone","description":"demo drone showcase","address":"Espoo","tpm2":{"device":"lab@192.168.0.250","tag":"test"}}'
#curl -X POST localhost:5000/addDrone -H "Content-Type: application/json" -d '{"droneID":"7867-2642-9565","name":"predator drone","description":"death from above","address":"Afghanistan","tpm2":{"device":"lab@192.168.0.250","tag":"test"}}'

#Test for drone Telemetry

#sleep 10

for ((i = 0 ; i < 10 ; i++)); do
    longitude=$(echo "104.56 + $i * 20" | bc)
    latitude=$(echo "98.63 + $i * 15" | bc)
    altitude=$(echo "900 - $i * 12" | bc)

    sleep 2 
    curl -X POST localhost:5000/receiveTelemetry -H "Content-Type: application/json" -d '{"droneID":"5471-2153-8745-0784","longitude":"'"$longitude"'","latitude":"'"$latitude"'","altitude":"'"$altitude"'"}'
done