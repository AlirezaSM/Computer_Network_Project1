import socket
import threading
import time

PORT = 7447
MESSAGE_LENGTH_SIZE = 64
ENCODING = 'utf-8'

def main():

    address = socket.gethostbyname(socket.gethostname())
    SERVER_INFORMATION = (address, PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(SERVER_INFORMATION)

    username = set_username(s)
    print("""- '/users' showing accessible users
- '/choose_user' choose a user for messaging
- '/change_username' change your username
- '/disconnect' disconnect from server""")

    receive_thread = threading.Thread(target=receive, args=(s, username))
    receive_thread.start()

    while True:

        order = input('Enter your order: ')
        send_msg(s, order)

        if order == '/disconnect':
            send_msg(s, "/disconnect")
            exit()
        elif order == '/users':
            show_accessible_users(s)
        elif order == '/choose_user':
            choose_target_user(s, username)
        elif order == '/change_username':
            change_username(s, username)


def receive(client, username):
    while True:
        try:
            message_length = int(client.recv(MESSAGE_LENGTH_SIZE).decode(ENCODING))
            msg = client.recv(message_length).decode(ENCODING)

            msg_list = msg .split(' ')
            if msg_list[0] == '/message':
                print(msg.replace('/message ', '\n'))
            else:
                f = open("response.txt", "w")
                f.write(msg)
                f.close()

        except OSError:
            break

def change_username(client, username):
    new_username = input('Enter new Username: ')
    send_msg(client, new_username)
    response = get_server_response()

    if response == 'free':
        print("New Username set")
        return new_username
    elif response == 'reserved':
        print("Username reserved")
        return username


def choose_target_user(client, username):
    target_user = 'not set'
    response = 'not set'
    while response != 'connected':
        target_user = input('Enter target username: ')
        send_msg(client, target_user)
        response = get_server_response()

        if response == 'connected':
            print("Connected to {}".format(target_user))
        elif response == 'user not found':
            print("User not found")

    if response == 'connected':
        message_to_user(client, username)


def message_to_user(client, username):
    message = "/message "
    message += input("Enter your message: ")
    send_msg(client, message)


def show_accessible_users(client):
    users = get_server_response()
    print("Accessible users: ", users)


def set_username(client):
    username = 'not set'
    response = 'not set'
    while response != 'free':
        username = input('Enter your Username: ')
        send_msg(client, username)
        response = get_msg(client)

        if response == 'free':
            print("Username set")
        elif response == 'reserved':
            print("Username reserved")

    return username


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


def get_server_response():
    time.sleep(0.1)
    f = open("response.txt", "r")
    server_response = f.read()
    f.close()
    return server_response


if __name__ == '__main__':
    main()