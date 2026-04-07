import random

# ─────────────────────────────────────────────────────────
#  April 7: Channel-Based Sharding (Second Wrong Decision)
# ─────────────────────────────────────────────────────────
# Situation: "Messages go where the channel lives"
# Real Problem: One channel becomes viral →
#               ALL traffic goes to one shard.
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

    def store(self, message):
        self.messages.append(message)

    def message_count(self):
        return len(self.messages)


class ShardManager:
    def __init__(self, num_shards, overload_threshold=0.5):
        self.shards = [Shard(i) for i in range(num_shards)]
        self.overload_threshold = overload_threshold

    def get_total_messages(self):
        return sum(s.message_count() for s in self.shards)

    def check_hotspot(self):
        """Mandatory: Warn if one shard has >50% of total load."""
        total = self.get_total_messages()
        if total == 0:
            return
        print("\n--- Hotspot Detection ---")
        hotspot_found = False
        for shard in self.shards:
            pct = shard.message_count() / total
            if pct > self.overload_threshold:
                print(f"🔥 HOTSPOT WARNING: Shard {shard.id} has {pct*100:.1f}% of load! (threshold: {self.overload_threshold*100:.0f}%)")
                hotspot_found = True
        if not hotspot_found:
            print("✅ No hotspot detected. Load is balanced.")

    def print_distribution(self, label=""):
        total = self.get_total_messages()
        if label:
            print(f"\n[{label}]")
        print(f"{'Shard ID':>10} | {'Messages':>10} | {'% of Total':>10} | {'Status':>14}")
        print("-" * 58)
        for shard in self.shards:
            count = shard.message_count()
            pct = (count / total * 100) if total > 0 else 0
            status = "🔥 OVERLOADED" if pct > self.overload_threshold * 100 else "💤 IDLE" if pct < 10 else "✅ OK"
            print(f"{'Shard ' + str(shard.id):>10} | {count:>10} | {pct:>9.1f}% | {status:>14}")
        print("-" * 58)
        print(f"{'TOTAL':>10} | {total:>10} |")


class ChannelShardManager(ShardManager):
    """Routes messages based on channel_id.
    Every message to the same channel always goes to the same shard.
    This is the 'second wrong decision'."""

    def get_shard(self, channel_id):
        return self.shards[channel_id % len(self.shards)]

    def send_message(self, message):
        shard = self.get_shard(message.channel_id)
        shard.store(message)


# ─────────────────────────────────────────────────────────
#  Scenario 1: Normal Load (evenly spread channels)
# ─────────────────────────────────────────────────────────
def simulate_normal_load(manager, num_users=1000, num_messages=10000, num_channels=50):
    for _ in range(num_messages):
        user_id = random.randint(1, num_users)
        channel_id = random.randint(1, num_channels)
        manager.send_message(Message(user_id, channel_id, "normal message"))


# ─────────────────────────────────────────────────────────
#  Scenario 2: Viral Channel (one channel dominates)
# ─────────────────────────────────────────────────────────
def simulate_viral_channel(manager, viral_channel_id=3, viral_msgs=8000,
                            normal_msgs=2000, num_users=1000, num_channels=50):
    # Viral channel receives 8000 messages — all go to the same shard
    for _ in range(viral_msgs):
        user_id = random.randint(1, num_users)
        manager.send_message(Message(user_id, viral_channel_id, "cricket final update!!"))

    # Other channels share the remaining 2000 messages
    for _ in range(normal_msgs):
        user_id = random.randint(1, num_users)
        # Pick any channel EXCEPT the viral one
        channel_id = random.choice([c for c in range(1, num_channels + 1) if c != viral_channel_id])
        manager.send_message(Message(user_id, channel_id, "normal message"))


# ─────────────────────────────────────────────────────────
#  Comparison with April 6 (User-Based Sharding)
# ─────────────────────────────────────────────────────────
class UserShardManager(ShardManager):
    """April 6 strategy — kept here for direct comparison."""

    def get_shard(self, user_id):
        return self.shards[user_id % len(self.shards)]

    def send_message(self, message):
        shard = self.get_shard(message.user_id)
        shard.store(message)


# ─────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    NUM_SHARDS = 3
    VIRAL_CHANNEL = 3  # channel_id=3 → maps to Shard 3%3=0

    print("=" * 58)
    print("  April 7: Channel-Based Sharding (Second Wrong Decision)")
    print("=" * 58)

    # ── Scenario 1: Normal Load ──────────────────────────
    print("\n>>> Scenario 1: Normal Load (50 channels, 10000 messages)")
    manager_normal = ChannelShardManager(NUM_SHARDS)
    simulate_normal_load(manager_normal)
    manager_normal.print_distribution("Normal Load — Channel-Based Sharding")
    manager_normal.check_hotspot()

    # ── Scenario 2: Viral Channel ────────────────────────
    print("\n" + "=" * 58)
    viral_shard = VIRAL_CHANNEL % NUM_SHARDS
    print(f"\n>>> Scenario 2: Viral Channel (channel_id={VIRAL_CHANNEL} sends 8000 messages)")
    print(f"    channel_id={VIRAL_CHANNEL} → always routes to Shard {viral_shard}")

    manager_viral = ChannelShardManager(NUM_SHARDS)
    simulate_viral_channel(manager_viral, viral_channel_id=VIRAL_CHANNEL)
    manager_viral.print_distribution("Viral Channel — Channel-Based Sharding")
    manager_viral.check_hotspot()

    # ── Comparison: April 6 vs April 7 ──────────────────
    print("\n" + "=" * 58)
    print("  COMPARISON: April 6 (User-Based) vs April 7 (Channel-Based)")
    print("=" * 58)

    # Rerun same viral scenario with User-Based sharding
    manager_user = UserShardManager(NUM_SHARDS)
    simulate_viral_channel(manager_user, viral_channel_id=VIRAL_CHANNEL)

    print("\n[April 6 — User-Based Sharding under Viral Channel scenario]")
    manager_user.print_distribution()
    manager_user.check_hotspot()

    print("\n[April 7 — Channel-Based Sharding under Viral Channel scenario]")
    manager_viral_2 = ChannelShardManager(NUM_SHARDS)
    simulate_viral_channel(manager_viral_2, viral_channel_id=VIRAL_CHANNEL)
    manager_viral_2.print_distribution()
    manager_viral_2.check_hotspot()

    # ── Observation Summary ──────────────────────────────
    print("\n" + "=" * 58)
    print("  OBSERVATION SUMMARY")
    print("=" * 58)
    total = manager_viral.get_total_messages()
    viral_shard_obj = manager_viral.shards[viral_shard]
    viral_pct = viral_shard_obj.message_count() / total * 100

    print(f"\n  • Viral channel_id={VIRAL_CHANNEL} → always maps to Shard {viral_shard}")
    print(f"  • Shard {viral_shard} received {viral_shard_obj.message_count()} / {total} messages ({viral_pct:.1f}%)")
    print(f"  • Other shards are nearly idle — this is the HOTSPOT problem.")
    print(f"\n  April 6 (User-Based): Imbalance caused by one ACTIVE USER")
    print(f"  April 7 (Channel-Based): Imbalance caused by one VIRAL CHANNEL")
    print(f"  Both strategies fail — just for different reasons.")
    print(f"\n  ❌ Conclusion: Channel-based sharding is the 'Second Wrong Decision'.")
    print(f"     A viral event (cricket final, live stream) funnels ALL traffic")
    print(f"     into one shard, leaving others completely idle.")
