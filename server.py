import socket
import threading

PORT = 7447
MESSAGE_LENGTH_SIZE = 64
ENCODING = 'utf-8'
user_list = []


def main():

    address = socket.gethostbyname(socket.gethostname())
    HOST_INFORMATION = (address, PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(HOST_INFORMATION)

    print("[SERVER STARTS] Server is starting ...")
    f = open("user_list.txt", "w")
    f.write("")
    f.close()

    start(s)


def start(server):

    server.listen()

    while True:
        conn, address = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, address))
        t.start()


def handle_client(conn, address):

    print("[NEW CONNECTION] connected from {}".format(address))

    username = set_username(conn, address)

    connected = True
    while connected:

        order = get_msg(conn)
        print("[MESSAGE RECEIVED from {}] {}".format(username, order))

        if order == '/disconnect':
            print("[CONNECTION CLOSED] connection closed from {}".format(username))
            broadcast_message("[USER LEFT] {} left the server".format(username))
            user_list.remove([username, address[0], address[1], conn])
            connected = False
        elif order == '/users':
            send_users_list(conn, username)
        elif order == '/choose_user':
            set_target_user(conn)
        elif order == '/change_username':
            username = change_username(conn, username)

    conn.close()


def change_username(client, username):
    new_username = get_msg(client)
    if is_username_free(new_username):
        send_msg(client, "free")
        for user in user_list:
            if user[0] == username:
                user[0] = new_username
        return new_username
    else:
        send_msg(client, "reserved")
        return username

def set_target_user(client):
    is_target_user_set = False
    target_user = 'not set'
    while not is_target_user_set:
        target_user = get_msg(client)
        if not is_username_free(target_user):
            send_msg(client, "connected")
            is_username_set = True
            message_to_user(client, target_user)
            break
        else:
            send_msg(client, "user not found")
            break


def message_to_user(client, target_user):
    msg = get_msg(client)

    target_socket = ""
    for user in user_list:
        if user[0] == target_user:
            target_socket = user[3]

    msg_list = msg.split(' ')
    if msg_list[0] == '/message':
        send_msg(target_socket, msg)


def send_users_list(client, username):
    username_list = list(map(lambda x: x[0], user_list))
    username_list.remove(username)
    send_msg(client, str(username_list))


def set_username(client, address):
    is_username_set = False
    username = 'not set'
    while not is_username_set:
        username = get_msg(client)
        if is_username_free(username):
            send_msg(client, "free")
            broadcast_message("[NEW USER] {} joined to the server".format(username))
            user_list.append([username, address[0], address[1], client])
            is_username_set = True
        else:
            send_msg(client, "reserved")

    return username


def broadcast_message(message):
    for user in user_list:
        send_msg(user[3], "/message " + message)


def is_username_free(username):
    is_free = True
    for user in user_list:
        if username == user[0]:
            is_free = False

    return is_free


def get_msg(client):
    message_length = int(client.recv(MESSAGE_LENGTH_SIZE).decode(ENCODING))
    msg = client.recv(message_length).decode(ENCODING)
    return msg


def send_msg(client, msg):

    message = msg.encode(ENCODING)

    msg_length = len(message)
    msg_length = str(msg_length).encode(ENCODING)
    msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

    client.send(msg_length)
    client.send(message)


if __name__ == '__main__':
    main()