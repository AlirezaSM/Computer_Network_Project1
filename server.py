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

    start(s)


def start(server):

    server.listen()

    while True:
        conn, address = server.accept()
        t = threading.Thread(target = handle_client, args = (conn, address))
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
            user_list.remove([username, address[0], address[1]])
            connected = False
        elif order == '/users':
            send_users_list(conn, username)
        elif order == '/choose_user':
            set_target_user(conn)

    conn.close()


def set_target_user(client):
    is_target_user_set = False
    target_user = 'not set'
    while not is_target_user_set:
        target_user = get_msg(client)
        if not is_username_free(target_user):
            send_msg(client, "connected")
            is_username_set = True
            message_to_user(client, target_user)
        else:
            send_msg(client, "user not found")


def message_to_user(client, target_user):
    send_msg(client, "you can send message now")


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
            user_list.append([username, address[0], address[1]])
            is_username_set = True
        else:
            send_msg(client, "reserved")

    return username

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