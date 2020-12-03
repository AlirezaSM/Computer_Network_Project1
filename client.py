import socket

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

    while True:

        order = input('Enter your order: ')
        send_msg(s, order)

        if order == '/disconnect':
            break
        elif order == '/users':
            show_accessible_users(s)
        elif order == '/choose_user':
            choose_target_user(s)
        elif order == '/change_username':
            change_username(s, username)
        # elif order == 'inbox':
        #     print(get_msg(s))

    # send_msg(s, "HELLO WORLD!!")
    # send_msg(s, "DISCONNECT")


def change_username(client, username):
    new_username = input('Enter new Username: ')
    send_msg(client, new_username)
    response = get_msg(client)

    if response == 'free':
        print("New Username set")
        return new_username
    elif response == 'reserved':
        print("Username reserved")
        return username


def choose_target_user(client):
    target_user = 'not set'
    response = 'not set'
    while response != 'connected':
        target_user = input('Enter target username: ')
        send_msg(client, target_user)
        response = get_msg(client)

        if response == 'connected':
            print("Connected to {}".format(target_user))
        elif response == 'user not found':
            print("User not found")

    if response == 'connected':
        message_to_user(client, target_user)


def message_to_user(client, target_user):
    message = "/message "
    message += input("Enter your message to {}: ".format(target_user))
    send_msg(client, message)


def show_accessible_users(client):
    users = get_msg(client)
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
    # msg_list = msg .split(' ')
    # if msg_list[0] == '/message':
    #     print(msg)
    # else:
    #     return msg
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