import time
import random

class Message:
    def __init__(self, user_id, channel_id, content):
        self.user_id = user_id
        self.channel_id = channel_id
        self.content = content
        self.metadata = "*" * 1024  # ~1KB payload per message

class ChatServer:
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)

    def stats(self):
        print(f"Total messages stored: {len(self.messages)}")

def simulate_small_load():
    """April 3 baseline: 10 users, 50 messages — instant."""
    server = ChatServer()
    start = time.time()
    for _ in range(50):
        user_id = random.randint(1, 10)
        channel_id = random.randint(1, 5)
        server.send_message(Message(user_id, channel_id, "hello"))
    elapsed = time.time() - start
    print(f"[Small Load]  10 users, 50 messages  → {elapsed:.6f}s")
    server.stats()
    return elapsed

def simulate_large_load():
    """April 4 stress: 10,000 users, 100,000 messages — observe slowdown."""
    server = ChatServer()
    num_users = 10000
    num_messages = 100000
    batch_size = 20000

    print(f"\n[Large Load]  {num_users} users, {num_messages} messages")
    print(f"{'Batch':>10} | {'Messages':>10} | {'Batch Time':>12} | {'Total Time':>12}")
    print("-" * 55)

    total_start = time.time()
    for i in range(num_messages):
        user_id = random.randint(1, num_users)
        channel_id = random.randint(1, 50)
        server.send_message(Message(user_id, channel_id, "heavy payload"))

        if (i + 1) % batch_size == 0:
            batch_num = (i + 1) // batch_size
            elapsed = time.time() - total_start
            # Calculate time for just this batch
            print(f"{'#' + str(batch_num):>10} | {i + 1:>10} | {'...':>12} | {elapsed:>11.4f}s")

    total_elapsed = time.time() - total_start
    print("-" * 55)
    server.stats()
    print(f"Total time: {total_elapsed:.4f}s")
    return total_elapsed

if __name__ == "__main__":
    print("=" * 55)
    print("  April 4: Scaling Awareness — Single Server Stress")
    print("=" * 55)

    small_time = simulate_small_load()
    large_time = simulate_large_load()

    print(f"\n--- Comparison ---")
    print(f"Small load (50 msgs):     {small_time:.6f}s")
    print(f"Large load (100,000 msgs): {large_time:.4f}s")
    print(f"Slowdown factor:          {large_time / small_time:.1f}x")
    print(f"\nObservation: The single server approach breaks down at scale.")
    print(f"Memory grows endlessly, and there is no way to distribute load.")
