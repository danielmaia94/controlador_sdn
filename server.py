#!/usr/bin/python

# coding=utf-8

import socket
import thread
import sys
import time
import select
import uuid

HOST = '10.0.0.1'
SOCKET_LIST = []
RECV_BUFFER = 1024
PORT = 9000


class Client:
    pass


def handler(client):
    """El handler maneja la conexiosn con cada socket individualmente"""

    print "Accepted connection from: ", client.addr

    # Este bucle se repite cada vez que se encuentran datos en el bufer
    while 1:

        # Leemos tamano del bufer del socket cliente hasta recibir algo
        data = client.socket.recv(RECV_BUFFER)

        # Enviamos la informacion al cliente otra vez, si este no nos la
        # devuelve es que se ha desconectado, entonces cerramos el socket
        if not client.socket.send(data):
            client.socket.close()
            SOCKET_LIST.remove(client.socket)
            print "Client " + client.code + " not found - Socket closed - Total clients: " + str(len(SOCKET_LIST))
            break
        else:
            print "Client " + client.code + ": " + data + " - Total clients: " + str(len(SOCKET_LIST))
    return


def server():

    # Declaracion del socket
    server_addr = (HOST, PORT)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_addr)
    server_socket.listen(10)

    print "Server is listening for connections\n"
    while 1:

        # Esto ocurre antes de que se conecte un nuevo cliente
        c = Client()
        c.code = str(uuid.uuid4().fields[-1])[:5]

        # El server se queda en el bucle server_socket.accept()
        # hasta que se conecte un cliente y entonces se devuelven
        # el socket y la direccion desde donde se ha conectado
        c.socket, c.addr = server_socket.accept()

        # Lo anadimos a una lista
        SOCKET_LIST.append(c.socket)

        # Y lo lanzamos en un hilo para gestionar su conexion
        thread.start_new_thread(handler, (c,))

    server_socket.close()

if __name__ == "__main__":
    sys.exit(server())
