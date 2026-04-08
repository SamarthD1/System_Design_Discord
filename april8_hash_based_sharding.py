import hashlib
import random

# ─────────────────────────────────────────────────────────
#  April 8: Hash-Based Sharding (Better but Not Perfect)
# ─────────────────────────────────────────────────────────
# Situation: We try to distribute messages evenly using hashing.
# Real Problem: Even hashing fails when number of shards changes.
#
# Key Decision: What should we hash?
#   → user_id   : same as April 6, still causes influencer imbalance
#   → channel_id: same as April 7, still causes viral channel hotspot
#   → message_id: truly unique per message → best even distribution
#
# We choose MESSAGE_ID because:
#  1. Every message has a unique ID — inherently uniform distribution
#  2. It is NOT tied to user activity or channel popularity
#  3. No single user or channel can overload one shard
#  4. Trade-off: Cross-shard queries become harder (no affinity)
# ─────────────────────────────────────────────────────────

class Message:
    _id_counter = 0

    def __init__(self, user_id, channel_id, content):
        Message._id_counter += 1
        self.message_id = Message._id_counter  # Unique auto-incrementing ID
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
        total = self.get_total_messages()
        if total == 0:
            return
        hotspot_found = False
        for shard in self.shards:
            pct = shard.message_count() / total
            if pct > self.overload_threshold:
                print(f"  🔥 HOTSPOT: Shard {shard.id} has {pct*100:.1f}% load!")
                hotspot_found = True
        if not hotspot_found:
            print("  ✅ No hotspot detected.")

    def print_distribution(self, label=""):
        total = self.get_total_messages()
        if label:
            print(f"\n[{label}]")
        print(f"  {'Shard':>7} | {'Messages':>10} | {'% of Total':>10} | {'Status':>14}")
        print("  " + "-" * 52)
        for shard in self.shards:
            count = shard.message_count()
            pct = (count / total * 100) if total > 0 else 0
            status = "🔥 OVERLOADED" if pct > self.overload_threshold * 100 else "💤 IDLE" if pct < 5 else "✅ OK"
            print(f"  {'Shard ' + str(shard.id):>7} | {count:>10} | {pct:>9.1f}% | {status:>14}")
        print("  " + "-" * 52)
        print(f"  {'TOTAL':>7} | {total:>10} |")


# ─────────────────────────────────────────────────────────
#  Hash-Based Shard Managers (3 key variations)
# ─────────────────────────────────────────────────────────

class HashShardManager(ShardManager):
    """Base hash manager — subclasses decide what key to hash."""

    def get_shard(self, key):
        h = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        return self.shards[h % len(self.shards)]

    def send_message(self, message):
        raise NotImplementedError("Subclass must implement send_message")


class HashByUserID(HashShardManager):
    """Hash on user_id — same as April 6, still fails for influencers."""
    def send_message(self, message):
        shard = self.get_shard(message.user_id)
        shard.store(message)


class HashByChannelID(HashShardManager):
    """Hash on channel_id — same as April 7, still fails for viral channels."""
    def send_message(self, message):
        shard = self.get_shard(message.channel_id)
        shard.store(message)


class HashByMessageID(HashShardManager):
    """
    Hash on message_id — OUR CHOICE.
    Best distribution: each message has a unique ID,
    so no single user or channel can overload one shard.
    """
    def send_message(self, message):
        shard = self.get_shard(message.message_id)
        shard.store(message)


# ─────────────────────────────────────────────────────────
#  Simulation Helpers
# ─────────────────────────────────────────────────────────

def simulate_viral(manager, viral_channel_id=3, viral_msgs=8000,
                   normal_msgs=2000, num_users=1000, num_channels=50):
    """Same viral scenario used in April 7 for fair comparison."""
    Message._id_counter = 0  # Reset counter for each run
    for _ in range(viral_msgs):
        user_id = random.randint(1, num_users)
        manager.send_message(Message(user_id, viral_channel_id, "cricket final!"))
    for _ in range(normal_msgs):
        user_id = random.randint(1, num_users)
        channel_id = random.choice([c for c in range(1, num_channels + 1) if c != viral_channel_id])
        manager.send_message(Message(user_id, channel_id, "normal message"))


def simulate_influencer(manager, influencer_id=7, influencer_msgs=5000,
                        normal_msgs=5000, num_users=1000):
    """Same influencer scenario from April 6 for fair comparison."""
    Message._id_counter = 0
    for _ in range(influencer_msgs):
        manager.send_message(Message(influencer_id, random.randint(1, 50), "influencer post"))
    for _ in range(normal_msgs):
        manager.send_message(Message(random.randint(1, num_users), random.randint(1, 50), "normal"))


# ─────────────────────────────────────────────────────────
#  System Evolution: What happens when shards change 3 → 6?
# ─────────────────────────────────────────────────────────

def simulate_shard_scaling():
    """
    Demonstrate the key failure of hash-based sharding:
    When shard count changes, ALL routing keys remap.
    Messages stored on 3 shards would go to different shards on 6 shards.
    This causes data loss / inconsistency in a real system.
    """
    print("\n" + "=" * 60)
    print("  SYSTEM EVOLUTION: Shard Count 3 → 6")
    print("=" * 60)

    test_keys = [101, 202, 303, 404, 505]
    print(f"\n  {'Message ID':>12} | {'Shard (n=3)':>12} | {'Shard (n=6)':>12} | {'Remapped?':>10}")
    print("  " + "-" * 55)

    remapped = 0
    for key in test_keys + list(range(1, 21)):  # test 25 keys
        h = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        shard_3 = h % 3
        shard_6 = h % 6
        changed = "⚠️  YES" if shard_3 != shard_6 else "✅ NO"
        if shard_3 != shard_6:
            remapped += 1
        if key in test_keys:  # Only print sample keys for readability
            print(f"  {key:>12} | {'Shard ' + str(shard_3):>12} | {'Shard ' + str(shard_6):>12} | {changed:>10}")

    total_tested = len(test_keys) + 20
    print(f"\n  Tested {total_tested} message IDs:")
    print(f"  → {remapped} / {total_tested} would remap to a DIFFERENT shard after scaling!")
    pct_remapped = remapped / total_tested * 100
    print(f"  → {pct_remapped:.1f}% of data becomes unreachable / misrouted after adding shards.")
    print(f"\n  ❌ This is the core failure of simple hash-based sharding.")
    print(f"     Solution in production systems: Consistent Hashing (not covered here).")


# ─────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  April 8: Hash-Based Sharding (Better but Not Perfect)")
    print("=" * 60)

    NUM_SHARDS = 3

    # ── Part 1: Compare all 3 hash key choices ────────────
    print("\n>>> Part 1: What happens when we hash different keys?")
    print("    (Same viral channel scenario as April 7 for fair comparison)")

    # Hash by user_id
    m1 = HashByUserID(NUM_SHARDS)
    simulate_viral(m1)
    m1.print_distribution("Hash by user_id (viral channel scenario)")
    m1.check_hotspot()

    # Hash by channel_id
    m2 = HashByChannelID(NUM_SHARDS)
    simulate_viral(m2)
    m2.print_distribution("Hash by channel_id (viral channel scenario)")
    m2.check_hotspot()

    # Hash by message_id — OUR CHOICE
    m3 = HashByMessageID(NUM_SHARDS)
    simulate_viral(m3)
    m3.print_distribution("Hash by message_id — OUR CHOICE (viral channel scenario)")
    m3.check_hotspot()

    # ── Part 2: Verify message_id also handles influencer case ──
    print("\n" + "=" * 60)
    print("\n>>> Part 2: Does message_id hash survive the influencer scenario?")
    print("    (Same influencer scenario as April 6)")

    m4 = HashByMessageID(NUM_SHARDS)
    simulate_influencer(m4)
    m4.print_distribution("Hash by message_id — Influencer scenario")
    m4.check_hotspot()

    # ── Part 3: Key Choice Justification ──────────────────
    print("\n" + "=" * 60)
    print("  KEY CHOICE JUSTIFICATION")
    print("=" * 60)
    print("""
  We chose to hash on MESSAGE_ID. Here's why:

  Option A — Hash user_id:
    ❌ Same as April 6. One influencer still overloads one shard.
    ❌ Popular users still concentrate load on the same shard.

  Option B — Hash channel_id:
    ❌ Same as April 7. One viral channel still overloads one shard.
    ❌ All messages in a trending event go to the same place.

  Option C — Hash message_id: ✅ OUR CHOICE
    ✅ Every message gets a globally unique ID.
    ✅ Distribution is independent of who sent it or which channel.
    ✅ Even if one user sends 10,000 messages, they spread across all shards.
    ✅ Even if one channel goes viral, its messages spread across all shards.

  Trade-off of message_id hashing:
    ⚠️  Cross-shard queries become expensive.
        "Fetch last 10 messages of channel X" must scan ALL shards.
    ⚠️  No data locality — related data is spread everywhere.
    """)

    # ── Part 4: System Evolution (3 → 6 shards) ──────────
    simulate_shard_scaling()
