from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from seleniumbase import Driver

import time
import uvicorn
import threading
import socket

app = FastAPI()


class UserLogin(BaseModel):
    username: str
    password: str


# WebSocket route to receive messages from the socket server
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        print(f"Received message from socket server: {message}")


def get_message_from_socket(host: str, port: int):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        while True:
            message = client_socket.recv(1024).decode()
            print(f"Received message from socket server: {message}")
            return message
    finally:
        client_socket.close()


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
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = "0.0.0.0"  # Listen on all available network interfaces
            port = 12345  # Adjust the port as needed

            server_socket.bind((host, port))
            server_socket.listen(5)

            print(f"Socket server is listening on {host}:{port}")

            while True:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")

                message = client_socket.recv(1024).decode()
                print(f"Received message from client: {message}")

                driver.type("#approvals_code", message)
                time.sleep(2)
                driver.click('#checkpointSubmitButton')
                time.sleep(5)
                driver.click('#checkpointSubmitButton')
                client_socket.close()
                break

        time.sleep(10)
        cookies = driver.get_cookies()
        cookie_string = ';'.join([f"{cookie['name']}:{cookie['value']}" for cookie in cookies])

        return {"cookie": cookie_string}
    return {"cookie": ''}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        print(f"Received message from socket server: {message}")


# Function to handle incoming socket connections and messages

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
