import socket
import select

clients = {}
nicknames = {}

def broadcast(message, sender_socket=None):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                client_socket.close()
                remove_client(client_socket)

def handle_command(client_socket, message):
    command_parts = message.split(maxsplit=1)
    command = command_parts[0].upper()
    arg = command_parts[1] if len(command_parts) > 1 else ""

    if command == "MSG":
        if client_socket in nicknames:
            broadcast(f"[{nicknames[client_socket]}] {arg}", client_socket)
    elif command == "NICK":
        nicknames[client_socket] = arg
        client_socket.send(f"Pseudo défini comme: {arg}\n".encode())
    elif command == "NAMES":
        names = " ".join(nicknames.values())
        client_socket.send(f"[server] {names}\n".encode())
    elif command == "BYEBYE":
        client_socket.send("Déconnexion du serveur.\n".encode())
        remove_client(client_socket)
    elif command == "REMOVE":
        remove_nick, msg = arg.split(maxsplit=1)
        remove_client_by_nick(remove_nick, msg)
    else:
        client_socket.send("Commande invalide\n".encode())

def remove_client(client_socket):
    address = clients[client_socket]
    nickname = nicknames.pop(client_socket, address)
    broadcast(f"[server] {nickname} s'est déconnecté")
    client_socket.close()
    del clients[client_socket]

def remove_client_by_nick(nickname, msg):
    for client_socket, nick in nicknames.items():
        if nick == nickname:
            client_socket.send(f"[server] {msg}\n".encode())
            remove_client(client_socket)
            return

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 7777))
    server_socket.listen(5)
    print("Serveur de chat démarré")

    while True:
        sockets = list(clients.keys()) + [server_socket]
        readable, _, _ = select.select(sockets, [], [])

        for sock in readable:
            if sock == server_socket:
                client_socket, client_address = server_socket.accept()
                clients[client_socket] = f"{client_address[0]}:{client_address[1]}"
                nicknames[client_socket] = clients[client_socket]
                broadcast(f"[server] {clients[client_socket]} s'est connecté")
            else:
                try:
                    message = sock.recv(1024).decode().strip()
                    if message:
                        handle_command(sock, message)
                    else:
                        remove_client(sock)
                except:
                    remove_client(sock)

if __name__ == "__main__":
    main()
