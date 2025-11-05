# Basic Setup

1. Create a virtualenv and activate it.

```sh
python3 -m venv venv
source venv/bin/activate
```

2. Install the requirements

```sh
pip3 install -r requirements.txt
```

3. Use a tool like ngrok or pagekite to open a localhost tunnel to the port 8080.
In my case I use pagekite so I execute something like this

```sh
pagekite.py 8080 yourconfig.pagekite.me
```

4. Start the main.py
```sh
python3 main.py
```


5. Make a call in Genesys to the audio connector
You should see something lke this on the console

```
New WebSocket connection on path: /ws/1
{"type":"open","version":"2","id":"066764af-0848-400c-9454-951fd455d4cd","seq":1,"serverseq":0,"position":"PT0.0S","parameters":{"organizationId":"e1f572df-0fb6-4fc5-a8c9-9107b4c70fdd","conversationId":"654eff96-52f7-42fb-8fe7-a4f9f33c3291","participant":{"id":"1aec8efd-e26f-45f0-fdb1-bcfe549fb148","ani":"tel:+1xxxxxxxxxx","aniName":"","dnis":"tel:+xxxxxxx"},"media":[{"type":"audio","format":"PCMU","channels":["external"],"rate":8000}],"language":"es-es","inputVariables":{"myvalor":"miresultado"}}}
Successfully extracted message type: 'open'
{"type":"paused","version":"2","id":"066764af-0848-400c-9454-951fd455d4cd","seq":2,"serverseq":1,"position":"PT0.0S","parameters":{}}
Successfully extracted message type: 'paused'
{"type":"ping","version":"2","id":"066764af-0848-400c-9454-951fd455d4cd","seq":3,"serverseq":1,"position":"PT0.0S","parameters":{}}
Successfully extracted message type: 'ping'

```
# genesys-audio-connector-google-public
