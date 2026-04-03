import time
import random

class Message:
    def __init__(self, user_id, channel_id, content):
        self.user_id = user_id
        self.channel_id = channel_id
        self.content = content

class ChatServer:
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)

    def stats(self):
        print(f"Total messages stored: {len(self.messages)}")

def simulate_basic_usage():
    server = ChatServer()
    num_users = 10
    num_messages = 50
    
    print(f"--- April 3: Basic Chat System ---")
    print(f"Simulating {num_users} users sending {num_messages} total messages...")
    
    start_time = time.time()
    for _ in range(num_messages):
        user_id = random.randint(1, num_users)
        channel_id = random.randint(1, 5)
        msg = Message(user_id, channel_id, "hello from user")
        server.send_message(msg)
        
    end_time = time.time()
    
    print(f"Simulation completed in {end_time - start_time:.6f} seconds")
    server.stats()

if __name__ == "__main__":
    simulate_basic_usage()
