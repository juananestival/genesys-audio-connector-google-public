import json
from flask import Flask, request
from simple_websocket import Server, ConnectionClosed
import wave
import audioop
import time

app = Flask(__name__)

# --- Configuration ---
WAV_FILE_PATH = "sample_8k_16bit_mono.wav"  # IMPORTANT: Place your WAV file path here.
                                           # The file should be 8000 Hz, 16-bit, mono for best results.
AUDIO_CHUNK_SIZE = 1600  # Send audio in 1600-byte chunks (100ms of 8kHz 16-bit audio)

def stream_wav_file(ws, file_path):
    """
    Reads a WAV file, converts its audio to PCMU (μ-law), and streams it
    over the WebSocket connection.
    """
    print(f"Attempting to stream audio from: {file_path}")
    try:
        with wave.open(file_path, 'rb') as wf:
            # --- Verify WAV file format ---
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            channels = wf.getnchannels()

            print(f"WAV file details - Sample Width: {sample_width}, Frame Rate: {framerate}, Channels: {channels}")

            # Genesys expects 8000 Hz. If it's different, conversion is needed.
            # For this example, we'll proceed but log a warning.
            if framerate != 8000:
                print(f"Warning: WAV file frame rate is {framerate} Hz, but 8000 Hz is expected by Genesys.")

            # --- Read, Convert, and Send Audio Data ---
            pcm_data = wf.readframes(AUDIO_CHUNK_SIZE)
            while pcm_data:
                # Convert the linear PCM data to PCMU (μ-law) format.
                # This is a critical step for Genesys compatibility.
                # The 'sample_width' (in bytes) is required for the conversion.
                ulaw_data = audioop.lin2ulaw(pcm_data, sample_width)
                
                # Send the converted audio data as a binary message
                ws.send(ulaw_data)
                
                # Read the next chunk of PCM data
                pcm_data = wf.readframes(AUDIO_CHUNK_SIZE)
                
                # Small delay to simulate real-time streaming
                time.sleep(0.02) # 20ms delay between chunks

            print("Finished streaming audio file.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred during audio streaming: {e}")


@app.route('/ws/<path:path_param>', websocket=True)
def echo(path_param):
    print(f"New WebSocket connection on path: /ws/{path_param}")
    ws = Server.accept(request.environ)
    try:
        while True:
            data = ws.receive()
            if isinstance(data, str):
                try:
                    # Parse the JSON string into a Python dictionary
                    message = json.loads(data)
                    # Extract the value of the 'type' key
                    message_type = message.get('type')
                    print(f"Successfully extracted message type: '{message_type}'")

                    if message_type == 'open':
                        idtest = message.get('id')
                        myseq = message.get('serverseq', 0) + 1
                        
                        data_to_send = {
                            "type": "opened",
                            "id": idtest,
                            "version": "2",
                            "seq": myseq,
                            "clientseq": message.get('seq'), 
                            "parameters": {
                                "startPaused": False,
                                "media": [
                                    {
                                        "type": "audio",
                                        "format": "PCMU",
                                        "channels": ["external"],
                                        "rate": 8000
                                    }
                                ],
                                "language": "es-us",
                            }
                        }
                        ws.send(json.dumps(data_to_send))
                        print("Sent 'opened' message. Starting audio stream...")
                        


                    elif message_type == 'ping':
                        idtest = message.get('id')
                        myseq = message.get('serverseq', 0) + 1
                        
                        data_to_send = {
                            "type": "pong",
                            "id": idtest,
                            "version": "2",
                            "seq": myseq,
                            "clientseq": message.get('seq'), 
                            "parameters": {}
                        }
                        ws.send(json.dumps(data_to_send))
                        print("Sent 'pong' message.")
                                                # --- TRIGGER AUDIO STREAM ---
                        # After confirming the connection, start sending the WAV file.
                        stream_wav_file(ws, WAV_FILE_PATH)

                except json.JSONDecodeError:
                    print(f"Received a non-JSON text message.")
            else:
                # This is where your server would RECEIVE binary audio from Genesys
                print(f"Received a binary message (likely audio from client). Size: {len(data)} bytes")
            
    except ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return ''

if __name__ == '__main__':
    # You need a sample WAV file for this to work.
    # A proper file would be 16-bit PCM, single-channel (mono), with an 8000 Hz sample rate.
    # You can create one with a tool like Audacity.
    # Make sure the WAV_FILE_PATH variable points to your file.
    app.run(host='0.0.0.0', port=8080, debug=True)