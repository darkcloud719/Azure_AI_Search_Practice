from flask import Flask, Response, request
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time, json

app = Flask(__name__)

influx_url = "http://localhost:8086"
token = "hE7ic4TSR3KaRh0jt5zu0jq_44wM29x-OTXYnFWJnBZ9msnzT4c6YRWMS_wJdC0BvWKZg7Gobu-LzGRJWfSObg=="
org = "hello"
bucket = "testbucket"

client = InfluxDBClient(url=influx_url, toke=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)


@app.route('/home', methods=['GET'])
def get_home():
    start_time = time.time()
    status_code = 200


    try:
        response = {"message":"Success"}

        if request.args.get('error'):
            raise ValueError("Simulated error")
        
    except Exception as e:
        status_code = 500
        response = {"error":str(e)}

    finally:
        duration = time.time() - start_time
        request_count = 1

        point = Point("api_performance").tag("endpoint","/home").tag("method",request.method).field("response_time",duration).field("status_code", status_code).field("request_count", request_count)

        if status_code >= 400:
            point = point.field("error_rate",1)
        else:
            point = point.field("error_rate",0)

        write_api.write(bucket=bucket, org=org, record=point)

        return Response(json.dumps(response), status=status_code, mimetype="application/json")
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)