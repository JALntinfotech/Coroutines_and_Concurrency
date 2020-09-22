from socket import socket, AF_INET, SOCK_STREAM
from Promise_Architecture import ReadWait, WriteWait, NewTask, accept, receive, send


def handle_client(client, addr):
    print("Connection from", addr)
    while True:
        data = client.recv(65536)
        if not data:
            break
        client.send(data)
    client.close()
    print("Client closed.")
    yield  # Adding yield makes the handle_client function a generator/coroutine.


def handle_client_improved(client, addr):
    print("Connection from", addr)
    while True:
        yield ReadWait(client)
        data = client.recv(65536)
        if not data:
            break
        yield WriteWait(client)
        client.send(data)
    client.close()
    print("Client closed")


def handle_client_final(client, addr):
    print("Connection from", addr)
    while True:
        data = yield receive(client, 65536)
        if not data:
            break
        yield send(client, data)
    print("Closing client")
    client.close()


def server(port):
    print("Server starting.")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", port))
    sock.listen(5)
    while True:
        print("... (freezes) ...")
        client, addr = sock.accept()
        yield NewTask(handle_client(client, addr))


def server_improved(port):
    print("Server starting")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", port))
    sock.listen(5)
    while True:
        yield ReadWait(sock)
        client, addr = sock.accept()
        yield NewTask(handle_client_improved(client, addr))


def server_final(port):
    print("Server starting")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", port))
    sock.listen(5)
    while True:
        client, address = yield accept(sock)
        yield NewTask(handle_client_final(client, address))
