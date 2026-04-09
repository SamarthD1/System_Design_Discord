import hashlib
import random
import time
import sys

# 
#  April 9: Stress Simulation + Failure Simulation (Final Day)
# 
#  Covers ALL mandatory features:
#   3 simulation scenarios (normal, viral, extreme spike)
#   Failure simulation (disable one shard mid-test)
#   Cross-shard query (fetch last N messages of a channel)
#   Hotspot detection (>50% warning)
#   Performance awareness (count shards checked per query)
#   Final analysis (answers all 4 evaluation questions)
# 


# 
#  Core Classes
# 

class Message:
    _id_counter = 0

    def __init__(self, user_id, channel_id, content):
        Message._id_counter += 1
        self.message_id = Message._id_counter
        self.user_id = user_id
        self.channel_id = channel_id
        self.content = content
        self.timestamp = time.time()

    @classmethod
    def reset_counter(cls):
        cls._id_counter = 0


class Shard:
    def __init__(self, shard_id):
        self.id = shard_id
        self.messages = []
        self.is_online = True   # Can be set to False to simulate failure

    def store(self, message):
        if not self.is_online:
            return False          # Message is LOST — shard is down
        self.messages.append(message)
        return True

    def message_count(self):
        return len(self.messages)

    def get_messages_for_channel(self, channel_id, limit=None):
        """Fetch messages belonging to a specific channel from this shard."""
        result = [m for m in self.messages if m.channel_id == channel_id]
        if limit:
            return result[-limit:]
        return result


class HashShardManager:
    """Hash by message_id — our best strategy from April 8."""

    def __init__(self, num_shards, overload_threshold=0.5):
        self.shards = [Shard(i) for i in range(num_shards)]
        self.overload_threshold = overload_threshold
        self.dropped_messages = 0   # Count messages lost due to shard failures

    def get_shard(self, key):
        h = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        return self.shards[h % len(self.shards)]

    def send_message(self, message):
        shard = self.get_shard(message.message_id)
        stored = shard.store(message)
        if not stored:
            self.dropped_messages += 1

    def get_total_messages(self):
        return sum(s.message_count() for s in self.shards if s.is_online)

    def disable_shard(self, shard_id):
        """Simulate a shard going offline."""
        self.shards[shard_id].is_online = False
        print(f"\n    SHARD {shard_id} IS NOW OFFLINE (simulating server failure)")

    def check_hotspot(self):
        total = self.get_total_messages()
        if total == 0:
            return
        hotspot_found = False
        for shard in self.shards:
            if not shard.is_online:
                continue
            pct = shard.message_count() / total
            if pct > self.overload_threshold:
                print(f"   HOTSPOT: Shard {shard.id} has {pct*100:.1f}% load!")
                hotspot_found = True
        if not hotspot_found:
            print("   No hotspot detected.")

    def print_distribution(self):
        total = sum(s.message_count() for s in self.shards)
        online_total = self.get_total_messages()
        print(f"  {'Shard':>7} | {'Messages':>10} | {'% of All':>9} | {'Status':>14}")
        print("  " + "-" * 52)
        for shard in self.shards:
            count = shard.message_count()
            pct = (count / total * 100) if total > 0 else 0
            if not shard.is_online:
                status = " OFFLINE"
            elif online_total > 0 and count / online_total > self.overload_threshold:
                status = " OVERLOADED"
            elif pct < 5:
                status = " IDLE"
            else:
                status = " ONLINE"
            print(f"  {'Shard ' + str(shard.id):>7} | {count:>10} | {pct:>8.1f}% | {status:>14}")
        print("  " + "-" * 52)
        print(f"  {'TOTAL':>7} | {total:>10} |")
        if self.dropped_messages > 0:
            print(f"\n   DROPPED MESSAGES (lost due to shard failure): {self.dropped_messages}")

    def cross_shard_query(self, channel_id, limit=10):
        """
        Mandatory Feature: Cross-Shard Query
        Fetch last N messages of a channel — data may be on any shard.
        Must scan ALL online shards and combine results.
        """
        shards_checked = 0
        all_results = []

        for shard in self.shards:
            shards_checked += 1
            if not shard.is_online:
                print(f"   Shard {shard.id} is OFFLINE — skipping (data may be MISSING!)")
                continue
            msgs = shard.get_messages_for_channel(channel_id)
            all_results.extend(msgs)

        # Sort all results by timestamp and take the last N
        all_results.sort(key=lambda m: m.timestamp)
        final_results = all_results[-limit:] if len(all_results) >= limit else all_results

        print(f"\n  Cross-Shard Query: Last {limit} messages in channel {channel_id}")
        print(f"     Shards checked: {shards_checked} / {len(self.shards)}")
        print(f"     Total found across all shards: {len(all_results)}")
        print(f"     Returned (last {limit}): {len(final_results)} messages")
        print(f"     Performance cost: O(n × shards) = O({len(all_results)} × {shards_checked})")
        if len(final_results) > 0:
            print(f"     Sample: msg_id={final_results[-1].message_id}, "
                  f"user={final_results[-1].user_id}, "
                  f"channel={final_results[-1].channel_id}")
        return final_results, shards_checked


# 
#  Simulation Functions
# 

def run_normal_day(manager, num_users=1000, num_messages=5000, num_channels=50):
    """Scenario 1: Normal day — uniform traffic."""
    Message.reset_counter()
    start = time.time()
    for _ in range(num_messages):
        uid = random.randint(1, num_users)
        cid = random.randint(1, num_channels)
        manager.send_message(Message(uid, cid, "normal chat"))
    return time.time() - start


def run_viral_event(manager, num_users=1000, num_messages=5000,
                    viral_channel=5, viral_pct=0.8):
    """Scenario 2: Viral event — 80% traffic on one channel."""
    Message.reset_counter()
    viral_count = int(num_messages * viral_pct)
    normal_count = num_messages - viral_count
    start = time.time()
    for _ in range(viral_count):
        uid = random.randint(1, num_users)
        manager.send_message(Message(uid, viral_channel, "CRICKET FINAL!!!"))
    for _ in range(normal_count):
        uid = random.randint(1, num_users)
        cid = random.randint(1, 50)
        manager.send_message(Message(uid, cid, "other chat"))
    return time.time() - start


def run_extreme_spike(manager, num_users=50000, num_messages=10000,
                      influencer_id=7, spike_pct=0.5):
    """Scenario 3: Extreme spike — 50K users + influencer dominating."""
    Message.reset_counter()
    spike_count = int(num_messages * spike_pct)
    normal_count = num_messages - spike_count
    start = time.time()
    for _ in range(spike_count):
        uid = influencer_id
        cid = random.randint(1, 5)
        manager.send_message(Message(uid, cid, "influencer post"))
    for _ in range(normal_count):
        uid = random.randint(1, num_users)
        cid = random.randint(1, 50)
        manager.send_message(Message(uid, cid, "normal"))
    return time.time() - start


# 
#  MAIN
# 

def separator(title=""):
    print("\n" + "" * 65)
    if title:
        print(f"  {title}")
        print("" * 65)


if __name__ == "__main__":
    NUM_SHARDS = 3

    separator("April 9: Stress Simulation + Failure Simulation (Final Day)")

    # 
    #  PART 1: THREE SIMULATION SCENARIOS
    # 

    separator("PART 1: SCENARIO — Normal Day")
    print("  Config: 1,000 users, 5,000 messages, 50 channels")
    m_normal = HashShardManager(NUM_SHARDS)
    t = run_normal_day(m_normal)
    m_normal.print_distribution()
    m_normal.check_hotspot()
    print(f" Time: {t:.4f}s")

    separator("PART 1: SCENARIO — Viral Event (80% traffic on channel 5)")
    print("  Config: 1,000 users, 5,000 messages, channel_5 gets 80% load")
    m_viral = HashShardManager(NUM_SHARDS)
    t = run_viral_event(m_viral)
    m_viral.print_distribution()
    m_viral.check_hotspot()
    print(f" Time: {t:.4f}s")
    print(f"\n  Note: Hash by message_id keeps distribution balanced even during viral event.")

    separator("PART 1: SCENARIO — Extreme Spike (50K users + influencer)")
    print("  Config: 50,000 users, 10,000 messages, influencer sends 50%")
    m_spike = HashShardManager(NUM_SHARDS)
    t = run_extreme_spike(m_spike)
    m_spike.print_distribution()
    m_spike.check_hotspot()
    print(f" Time: {t:.4f}s")
    print(f"\n  Note: message_id hashing absorbs extreme spikes automatically.")

    # 
    #  PART 2: CROSS-SHARD QUERY
    # 

    separator("PART 2: CROSS-SHARD QUERY — Fetch Last 10 Messages of Channel 5")
    print("  (Running on viral event data — channel 5 had 80% traffic)")
    results, shards_checked = m_viral.cross_shard_query(channel_id=5, limit=10)
    print(f"\n   All {shards_checked} shards must be scanned for EVERY read query.")
    print(f"     This is the cost of distributing data by message_id — no locality.")

    # 
    #  PART 3: FAILURE SIMULATION — Disable Shard 1 Mid-Test
    # 

    separator("PART 3: FAILURE SIMULATION — Shard 1 Goes Down")
    print("  Simulating a real server crash during the extreme spike scenario...")
    m_failure = HashShardManager(NUM_SHARDS)

    # Send half the messages first
    Message.reset_counter()
    print("\n  [Phase 1] Sending 5,000 messages — all shards online...")
    for _ in range(5000):
        uid = random.randint(1, 1000)
        cid = random.randint(1, 50)
        m_failure.send_message(Message(uid, cid, "pre-failure message"))

    print("\n  Distribution BEFORE failure:")
    m_failure.print_distribution()

    # Disable Shard 1
    m_failure.disable_shard(1)

    # Send more messages after failure
    print("\n  [Phase 2] Sending 5,000 more messages — Shard 1 now OFFLINE...")
    for _ in range(5000):
        uid = random.randint(1, 1000)
        cid = random.randint(1, 50)
        m_failure.send_message(Message(uid, cid, "post-failure message"))

    print("\n  Distribution AFTER failure:")
    m_failure.print_distribution()
    m_failure.check_hotspot()

    # Cross-shard query with shard down
    separator("PART 3b: CROSS-SHARD QUERY WITH SHARD DOWN")
    print("  Querying channel 10 — some data may be on offline Shard 1...")
    results_partial, _ = m_failure.cross_shard_query(channel_id=10, limit=10)
    print(f"\n  DATA LOSS: Messages stored on Shard 1 are PERMANENTLY inaccessible!")
    print(f"     In a real system this causes: incomplete results, inconsistency, user-visible errors.")

    # 
    #  PART 4: FINAL ANALYSIS
    # 

    separator("PART 4: FINAL ANALYSIS")

    print("""
  Q1. Which shard failed first and why?
  
  In user-based and channel-based sharding, the shard that received
  the most popular user_id or channel_id fails first. In our April 6
  test, Shard 1 (user_id=7 → 7%3=1) hit 66.2% load and would crash
  first. In April 7, Shard 0 (channel_id=3 → 3%3=0) hit 85.7% load.
  
  With message_id hashing (our April 8+ choice), no single shard
  accumulates disproportionate load — all fail roughly at the same
  time under extreme global load.

  Q2. Which strategy looked good but failed under spike?
  
  Channel-Based Sharding (April 7) looks good on paper — channels
  stay together, queries are easy. But during a viral event (cricket
  final), ALL traffic funnels into one shard. It appeared balanced
  with normal data but catastrophically failed at 85.7% under spike.
  
  User-Based Sharding (April 6) also appeared balanced with 1000
  random users but immediately broke when one influencer dominated.

  Q3. What happens if shards increase from 3 → 10?
  
  Simple hash-based sharding (key % num_shards) remaps ALL routing
  when num_shards changes. In our April 8 analysis, 32% of message
  IDs mapped to different shards after scaling from 3 → 6.
  Going to 10 shards would remap ~70%+ of keys, making all
  previously stored data effectively UNREACHABLE without migration.
  Production solution: Consistent Hashing (virtual nodes).

  Q4. What breaks when one shard goes down?
  
  As demonstrated in Part 3:
  → Messages HASHED to that shard during downtime are DROPPED.
  → Messages already STORED on that shard are INACCESSIBLE.
  → Cross-shard queries return INCOMPLETE results (missing data).
  → No automatic redistribution — other shards do NOT take over.
  → System continues running but with silent DATA LOSS.
  Production solution: Replication (each shard has a replica).
    """)

    separator("SUMMARY: All 3 Strategies Compared")
    print(f"""
  {'Strategy':>20} | {'Normal Load':>12} | {'Viral Channel':>14} | {'Influencer':>11} | {'Scaling':>10}
  {'-'*77}
  {'User-Based (Apr 6)':>20} | {'OK':>12} | {'OK':>14} | {'FAILS':>11} | {'FAILS':>10}
  {'Channel-Based (Apr 7)':>20} | {'OK':>12} | {'FAILS':>14} | {'OK':>11} | {'FAILS':>10}
  {'Hash-MessageID (Apr 8)':>20} | {'OK':>12} | {'OK':>14} | {'OK':>11} | {'FAILS':>10}
  {'-'*77}
  None of these strategies is perfect. Real systems use:
  • Consistent Hashing   → Minimize remapping when shards scale
  • Replication          → Survive shard failures without data loss
  • Hybrid Sharding      → Combine message_id distribution + channel affinity
    """)
