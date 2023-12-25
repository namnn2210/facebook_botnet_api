from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from seleniumbase import Driver
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import time
import uvicorn
import asyncio
import socket

app = FastAPI()
origins = [
    "http://localhost:3000",  # React app
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class UserLogin(BaseModel):
    username: str
    password: str


two_factor_code_storage = {}


# WebSocket route to receive messages from the socket server

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    print(f"WebSocket connection accepted for {username}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data from {username}: {data}")
            two_factor_code_storage[username] = data
            print(f"Stored 2FA code for {username}: {data}")
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for {username}")
    finally:
        await websocket.close()


@app.post("/login")
async def login(user_login: UserLogin):
    username = user_login.username
    password = user_login.password

    proxy = 'division1tckl_gmail_com:xPTMylKzxi@63.161.13.114:3128'
    driver = Driver(uc=True, headless=False, proxy=proxy)

    driver.open("https://www.facebook.com")

    # Enter your Facebook username and password
    if driver.is_element_visible('#email'):
        driver.type("#email", username)
        driver.type("#pass", password)

    # Click the "Log In" button
    driver.click('button[name="login"]')
    time.sleep(10)
    button = "a[role='button']"
    if driver.is_element_visible(button):
        a_button_element = driver.get_text(button)
        # Get the text of the <a> element with role="button"
        if a_button_element == "Need another way to confirm it's you?":
            start_time = time.time()
            username = user_login.username  # Assuming this is the unique identifier

            # Wait for the 2FA code to be received via WebSocket
            while username not in two_factor_code_storage:
                await asyncio.sleep(1)  # Non-blocking sleep
                # Implement a timeout mechanism
                if time.time() - start_time > 30:  # 30 seconds timeout
                    return {"error": "Timeout waiting for 2FA code"}
            two_factor_code = two_factor_code_storage.pop(username)

            driver.type("#approvals_code", two_factor_code)
            time.sleep(2)
            while driver.is_element_visible('#checkpointSubmitButton'):
                driver.click('#checkpointSubmitButton')
                time.sleep(2)
        time.sleep(10)
        cookies = driver.get_cookies()
        cookie_string = ';'.join([f"{cookie['name']}:{cookie['value']}" for cookie in cookies])
        data = {
            'cookie': cookie_string
        }
        print(data)
        driver.quit()
        return JSONResponse(content=data)
    return JSONResponse(content={})


# Function to handle incoming socket connections and messages

def main():
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
