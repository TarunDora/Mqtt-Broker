import socket
import ssl
import threading

def signup_or_login():
    choice = input("Do you want to (S)ignup or (L)ogin? ").upper()
    if choice == "S":
        return "SIGNUP"
    elif choice == "L":
        return "LOGIN"
    else:
        print("Invalid choice. Please try again.")
        return signup_or_login()

def receive_messages(ssl_client_socket):
    try:
        while True:
            # Receive new messages for the subscribed topic
            message = ssl_client_socket.recv(1024).decode()
            if message:
                print("New message:", message)
            else:
                print("No more messages for this topic.")
                break
    except Exception as e:
        print(f"Error occurred while receiving messages: {e}")

def subscribe_topic(ssl_client_socket, topic):
    try:
        # Subscribe to the specified topic
        ssl_client_socket.sendall(f"SUBSCRIBE:{topic}".encode())

        # Receive messages for the topic
        response = ssl_client_socket.recv(1024).decode()
        print(f"Messages for topic '{topic}':")
        print(response)

        # Receive SUBACK message to acknowledge receipt of messages (QoS 0)
        suback = ssl_client_socket.recv(1024).decode()
        print(f"Received SUBACK message: {suback}")

        # Start a thread to continuously receive new messages for the subscribed topic
        threading.Thread(target=receive_messages, args=(ssl_client_socket,)).start()
    except Exception as e:
        print(f"Error occurred while subscribing to topic: {e}")

def main():
    try:
        # Connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Wrap the client socket with SSL
        ssl_client_socket = ssl.wrap_socket(client_socket, ssl_version=ssl.PROTOCOL_TLS)
        
        ssl_client_socket.connect(("127.0.0.1", 12559))
        print("Connected to server.")

        # Specify client action as signup or login
        ssl_client_socket.sendall(signup_or_login().encode())

        # Send username and password
        username = input("Enter username: ")
        password = input("Enter password: ")

        ssl_client_socket.sendall(username.encode())
        ssl_client_socket.sendall(password.encode())

        # Authenticate as subscriber
        client_type = "SUBSCRIBER"
        ssl_client_socket.sendall(client_type.encode())

        response = ssl_client_socket.recv(1024).decode()
        print(response)

        if response == "Signup successful." or response == "Login successful.":
            subscribed = False
            while True:
                try:
                    if not subscribed:
                        choice = input("Do you want to (S)ubscribe to a topic or (L)ist available topics? ").upper()
                        if choice == "S":
                            topic = input("Enter topic to subscribe to: ")
                            subscribe_topic(ssl_client_socket, topic)
                            subscribed = True
                        elif choice == "L":
                            ssl_client_socket.sendall("SUBSCRIBE:LIST_TOPICS".encode())

                            # Receive list of topics from server
                            response = ssl_client_socket.recv(1024).decode()
                            print("Available topics:")
                            print(response)

                            # Receive SUBACK message to acknowledge receipt of messages (QoS 0)
                            '''suback = ssl_client_socket.recv(1024).decode()
                            print(f"Received SUBACK message: {suback}")
                            subscribed = True'''
                        else:
                            print("Invalid choice. Please try again.")
                    else:
                        # Continue to receive new messages for the subscribed topic
                        pass

                except Exception as e:
                    print(f"Error occurred: {e}")
                    ssl_client_socket.close()
                    break
        else:
            print("Authentication failed.")

        # Close client socket when done
        ssl_client_socket.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()