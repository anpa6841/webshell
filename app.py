import subprocess
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Serve static files for the front-end (HTML/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get():
    # Serving the HTML page for frontend interaction
    return HTMLResponse(content=open("static/terminal.html").read(), status_code=200)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive command from the frontend
            command = await websocket.receive_text()
            
            # Execute the command in a subprocess
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Capture the output and send it to the frontend in real-time
            stdout, stderr = process.communicate()
            
            if stdout:
                await websocket.send_text(stdout.decode())
            if stderr:
                await websocket.send_text(stderr.decode())
    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
