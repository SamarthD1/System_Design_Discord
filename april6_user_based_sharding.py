import random
import time

# ─────────────────────────────────────────────────────────
#  April 6: User-Based Sharding (First Wrong Decision)
# ─────────────────────────────────────────────────────────
# Situation: "Each user will stick to one shard"
# Real Problem: One influencer sends 5000 messages →
#               That user alone overloads one shard.
# ─────────────────────────────────────────────────────────

class Message:
    def __init__(self, user_id, channel_id, content):
        self.user_id = user_id
        self.channel_id = channel_id
        self.content = content


class Shard:
    """Independent shard — stores its own messages only."""

    def __init__(self, shard_id):
        self.id = shard_id
        self.messages = []
        self.is_overloaded = False

    def store(self, message):
        self.messages.append(message)

    def message_count(self):
        return len(self.messages)


class ShardManager:
    def __init__(self, num_shards, overload_threshold=0.5):
        self.shards = [Shard(i) for i in range(num_shards)]
        self.overload_threshold = overload_threshold  # 50% of total load

    def get_total_messages(self):
        return sum(s.message_count() for s in self.shards)

    def check_hotspot(self):
        """Hotspot Detection: Warn if one shard has >50% of total load."""
        total = self.get_total_messages()
        if total == 0:
            return
        print("\n--- Hotspot Detection ---")
        hotspot_found = False
        for shard in self.shards:
            pct = shard.message_count() / total
            if pct > self.overload_threshold:
                print(f"🔥 HOTSPOT WARNING: Shard {shard.id} has {pct*100:.1f}% of total load! (threshold: {self.overload_threshold*100:.0f}%)")
                shard.is_overloaded = True
                hotspot_found = True
        if not hotspot_found:
            print("✅ No hotspot detected. Load is balanced.")

    def print_distribution(self, label=""):
        total = self.get_total_messages()
        if label:
            print(f"\n[{label}]")
        print(f"{'Shard ID':>10} | {'Messages':>10} | {'% of Total':>10} | {'Status':>12}")
        print("-" * 55)
        for shard in self.shards:
            count = shard.message_count()
            pct = (count / total * 100) if total > 0 else 0
            status = "🔥 OVERLOADED" if pct > self.overload_threshold * 100 else "✅ OK"
            print(f"{'Shard ' + str(shard.id):>10} | {count:>10} | {pct:>9.1f}% | {status:>12}")
        print("-" * 55)
        print(f"{'TOTAL':>10} | {total:>10} |")


class UserShardManager(ShardManager):
    """Routes messages based on user_id.
    Every message from the same user always goes to the same shard.
    This is the 'first wrong decision'."""

    def get_shard(self, user_id):
        return self.shards[user_id % len(self.shards)]

    def send_message(self, message):
        shard = self.get_shard(message.user_id)
        shard.store(message)


# ─────────────────────────────────────────────────────────
#  Scenario 1: Normal Load (balanced users)
# ─────────────────────────────────────────────────────────
def simulate_normal_load(manager, num_users=1000, num_messages=10000):
    for _ in range(num_messages):
        user_id = random.randint(1, num_users)
        channel_id = random.randint(1, 50)
        manager.send_message(Message(user_id, channel_id, "normal message"))


# ─────────────────────────────────────────────────────────
#  Scenario 2: Influencer Load (one user dominates)
# ─────────────────────────────────────────────────────────
def simulate_influencer_load(manager, influencer_user_id=7, influencer_msgs=5000, normal_msgs=5000, num_users=1000):
    # Influencer sends 5000 messages — all go to the same shard
    for _ in range(influencer_msgs):
        channel_id = random.randint(1, 50)
        manager.send_message(Message(influencer_user_id, channel_id, "influencer post"))

    # Regular users send the rest
    for _ in range(normal_msgs):
        user_id = random.randint(1, num_users)
        # Make sure regular users don't accidentally map to same shard for clarity
        channel_id = random.randint(1, 50)
        manager.send_message(Message(user_id, channel_id, "normal message"))


# ─────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  April 6: User-Based Sharding (First Wrong Decision)")
    print("=" * 55)

    NUM_SHARDS = 3

    # --- Scenario 1: Normal balanced load ---
    print("\n>>> Scenario 1: Normal Load (1000 users, 10000 messages)")
    manager_normal = UserShardManager(NUM_SHARDS)
    simulate_normal_load(manager_normal)
    manager_normal.print_distribution("Normal Load — User-Based Sharding")
    manager_normal.check_hotspot()

    # --- Scenario 2: Influencer causes imbalance ---
    print("\n" + "=" * 55)
    print("\n>>> Scenario 2: Influencer Load (user_id=7 sends 5000 messages)")
    influencer_id = 7
    influencer_shard = influencer_id % NUM_SHARDS
    print(f"    Influencer user_id={influencer_id} → always routes to Shard {influencer_shard}")

    manager_influencer = UserShardManager(NUM_SHARDS)
    simulate_influencer_load(manager_influencer, influencer_user_id=influencer_id)
    manager_influencer.print_distribution("Influencer Load — User-Based Sharding")
    manager_influencer.check_hotspot()

    # --- Observation Summary ---
    print("\n" + "=" * 55)
    print("  OBSERVATION SUMMARY")
    print("=" * 55)
    total = manager_influencer.get_total_messages()
    influencer_shard_obj = manager_influencer.shards[influencer_shard]
    influencer_pct = influencer_shard_obj.message_count() / total * 100
    print(f"\n  • Influencer (user_id={influencer_id}) mapped to → Shard {influencer_shard}")
    print(f"  • That shard received {influencer_shard_obj.message_count()} / {total} messages ({influencer_pct:.1f}%)")
    print(f"  • Other shards are relatively idle while Shard {influencer_shard} is overloaded.")
    print(f"\n  ❌ Conclusion: User-based sharding causes load imbalance.")
    print(f"     One popular user can single-handedly overload an entire shard.")
    print(f"     This is the 'First Wrong Decision'.")
