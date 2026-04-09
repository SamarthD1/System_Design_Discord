import random
import time

# ─────────────────────────────────────────────────────────
#  April 5: Introduce Shards (But No Strategy Yet)
# ─────────────────────────────────────────────────────────
# Situation: We now have 3 machines (shards).
# Problem: Where should data go?
# Key Rule: Each shard must be INDEPENDENT — no global storage.
# ─────────────────────────────────────────────────────────

class Message:
    def __init__(self, user_id, channel_id, content):
        self.user_id = user_id
        self.channel_id = channel_id
        self.content = content


class Shard:
    """Represents an independent server/machine.
    Each shard has its OWN message storage — no shared global list."""

    def __init__(self, shard_id):
        self.id = shard_id
        self.messages = []  # Independent storage per shard

    def store(self, message):
        self.messages.append(message)

    def message_count(self):
        return len(self.messages)


class ShardManager:
    """Manages multiple shards. Responsible for routing messages.
    The routing strategy is intentionally left as a simple decision
    point — no hardcoded user/channel logic yet."""

    def __init__(self, num_shards):
        self.shards = [Shard(i) for i in range(num_shards)]

    def send_message(self, message):
        # Naive routing: randomly assign to a shard
        # This is intentionally simple — no user_id or channel_id logic yet.
        # The point is to prove shards work independently.
        shard = random.choice(self.shards)
        shard.store(message)

    def print_distribution(self):
        total = sum(s.message_count() for s in self.shards)
        print(f"\n{'Shard ID':>10} | {'Messages':>10} | {'% of Total':>10}")
        print("-" * 40)
        for shard in self.shards:
            count = shard.message_count()
            pct = (count / total * 100) if total > 0 else 0
            print(f"{'Shard ' + str(shard.id):>10} | {count:>10} | {pct:>9.1f}%")
        print("-" * 40)
        print(f"{'TOTAL':>10} | {total:>10} |")

    def verify_independence(self):
        """Proves shards are independent — no shared global storage."""
        print("\n--- Independence Verification ---")
        # Each shard's messages list is a separate object in memory
        ids = [id(shard.messages) for shard in self.shards]
        all_unique = len(set(ids)) == len(ids)
        print(f"Number of shards: {len(self.shards)}")
        print(f"Each shard has its own storage: {all_unique}")
        print(f"Memory addresses: {['0x' + format(i, 'x') for i in ids]}")
        if all_unique:
            print("PASS: All shards are fully independent.")
        else:
            print("FAIL: Shards share storage — this is a design flaw!")


def simulate_sharded_system():
    num_shards = 3
    num_users = 1000
    num_messages = 10000

    print("=" * 50)
    print("  April 5: Shards Introduction (No Strategy Yet)")
    print("=" * 50)
    print(f"\nConfig: {num_shards} shards, {num_users} users, {num_messages} messages")
    print("Routing: Random assignment (no user/channel logic)")

    manager = ShardManager(num_shards)

    # Step 1: Send messages
    start = time.time()
    for _ in range(num_messages):
        user_id = random.randint(1, num_users)
        channel_id = random.randint(1, 50)
        msg = Message(user_id, channel_id, "hello")
        manager.send_message(msg)
    elapsed = time.time() - start

    print(f"\nSimulation completed in {elapsed:.4f}s")

    # Step 2: Show messages per shard
    manager.print_distribution()

    # Step 3: Prove independence (no global storage)
    manager.verify_independence()

    # Step 4: Show that data is NOT accessible globally
    print("\n--- Global Storage Check ---")
    print(f"Does ShardManager have a global messages list? {'messages' in dir(manager)}")
    print("Each shard only knows about its own data.")
    for shard in manager.shards:
        channels_in_shard = set(m.channel_id for m in shard.messages)
        users_in_shard = set(m.user_id for m in shard.messages)
        print(f"  Shard {shard.id}: {shard.message_count()} msgs, "
              f"{len(users_in_shard)} unique users, "
              f"{len(channels_in_shard)} unique channels")


if __name__ == "__main__":
    simulate_sharded_system()
