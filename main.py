import json
from flask import Flask, request
from simple_websocket import Server, ConnectionClosed

app = Flask(__name__)

def sequence_updater(myseq, audioconnectorseq):
    """
        When Genesys send a request from audioconnector then Genesys is the client and the target
        is the server. 
        Example:
        When audioconnecto send an open request the server will recive something like this
        {"seq":1,"serverseq":0}

        Now the server must to answer with some mandatory fields
        - type
        - version
        - id
        - "seq":1,
        - "clientseq":1, 

        In this case we are the clientseq. 
        We must to answer like to the genesys request "seq1" we respond with "clientseq:1"

    """
    clientseq = myseq + 1
    seq = audioconnectorseq

    return clientseq, seq


@app.route('/ws/<path:path_param>', websocket=True)
def echo(path_param):
    print(f"New WebSocket connection on path: /ws/{path_param}")
    ws = Server.accept(request.environ)
    try:
        while True:
            data = ws.receive()
            print(data)
            if isinstance(data, str):
                try:
                    # Parse the JSON string into a Python dictionary
                    message = json.loads(data)
                    # Extract the value of the 'type' key
                    message_type = message.get('type')
                    print(f"Successfully extracted message type: '{message_type}'")
                    clientseq, audioconnectorseq = sequence_updater(message.get('serverseq'), message.get('seq'))
                    print(f"the pair of sequende is {clientseq} and {audioconnectorseq}")

                    if message_type == 'open':
                        idtest = message.get('id')
                        #current_client_seq = message.get('seq')
                        #current_server_seq = message.get('serverseq')
                        data_to_send = {
                            "type": "opened",
                            "id": idtest,
                            "version": "2",
                            "seq":audioconnectorseq,
                            "clientseq":clientseq, 
                            "parameters": {
                            "startPaused": True,
                            "media": [
                            {
                                "type": "audio",
                                "format": "PCMU",
                                "channels": [
                                "external"
                                ],
                                "rate": 8000
                            }
                            ],
                            "language": "es-us",
                        }
                        }
                        ws.send(json.dumps(data_to_send))

                except json.JSONDecodeError:
                    print(f"Received a non-JSON text message: {data}")
            
    except ConnectionClosed:
        pass
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)