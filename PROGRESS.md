# Discord System Design Project Progress

This document tracks the daily progress of the scalable chat system simulation, detailing what was accomplished on each day according to the assignment's timeline.

## Assignment Plan & Progress Tracking

| Date | Focus Area | Real Situation | Student Task | Mandatory Submission | Hidden Complexity Introduced | What You Check | Progress Status / Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2 April** | System Thinking | App becomes popular during a live event, 50,000 users join, one channel dominates | Write where system will fail and why | 1-page explanation | Thinking before coding | Do they identify bottlenecks (memory, load, hotspots)? | ✅ **Completed:** CPU, memory, and hotspot bottlenecks clearly identified in `system_failure_analysis.md`. |
| **3 April** | Basic System | Small system works fine with few users | Build chat system (users, channels, messages) | Working code + message count output | Illusion that system is "complete" | Does the system actually store and show data? | ✅ **Completed:** `april3_basic_system.py` stores message objects in a list and `stats()` displays the counts. |
| **4 April** | Scaling Awareness | Users increase 100x, system still single server | Simulate large message load and observe behavior | Code + short observation note | System slowdown and inefficiency | Did they actually simulate load or just write theory? | ✅ **Completed:** Simulated 100,000 messages — measured **1,628x slowdown**. Documented in `april4_observation.md`. |
| **5 April** | Shards Introduction | Multiple servers available but no distribution logic | Create shards and store data separately | Code showing messages per shard | Confusion about routing logic | Are shards independent (no global storage)? | ✅ **Completed:** 3 independent shards verified. Messages per shard output in `april5_shards_introduction.py`. |
| **6 April** | User-Based Sharding | One highly active user sends massive traffic | Route using user_id | Code + shard distribution output | Load imbalance (one shard overloaded) | Do they show uneven distribution clearly? | ✅ **Completed:** Influencer (user_id=7) caused Shard 1 to hit **66.2% load**. Hotspot warning triggered. See `april6_user_based_sharding.py`. |
| **7 April** | Channel-Based Sharding | One channel becomes viral (event spike) | Route using channel_id | Code + comparison note | Hotspot problem (single shard overload) | Do they compare with previous strategy properly? | ✅ **Completed:** Viral channel hit **85.7% load** on one shard. Direct comparison with April 6 included. See `april7_channel_based_sharding.py`. |
| **8 April** | Hash-Based Sharding | Need better distribution under uneven load | Implement hashing and choose key | Code + explanation of key choice | Decision complexity (what to hash?) | Do they justify their choice logically? | ✅ **Completed:** Chose `message_id` hashing — justified logically. Compared all 3 key options. Shard evolution 3→6 analyzed. See `april8_hash_based_sharding.py`. |
| **9 April** | Stress + Failure Simulation | Normal load, spike load, and one server failure | Run simulations, disable one shard, test system | Logs + final code + analysis | Failure handling, data loss, inconsistency | Do they observe and explain failure impact? | ✅ **Completed:** 3 scenarios run, Shard 1 disabled mid-test (1,675 msgs dropped), cross-shard query with missing data shown. Full analysis in `april9_stress_failure_simulation.py`. |

---

## Detailed Daily Log

### ✅ April 2: System Thinking
**Focus:** App becomes popular during a live event, 50,000 users join, one channel dominates
**What was done:**
- Created a failure analysis document (`system_failure_analysis.md`) explaining where the single-server system will fail under massive load.
- Outlined primary bottlenecks: CPU exhaustion, Network Bandwidth Saturation, Memory Exhaustion (OOM), and DB write bottlenecks.
- Highlighted the "Hotspot and Fan-out" problem where 80% of traffic concentrating in one channel causes massive broadcast delays.
- Included the user-provided Napkin AI breakdown link describing the progressive cascading failures.
- **Hidden Complexity Introduced:** Thinking before coding to realize that a single-server system inevitably collapses and lacks isolation.

### ✅ April 3: Basic System
**Focus:** Small system works fine with few users 
**What was done:**
- Created the foundational architecture (`april3_basic_system.py`) with a `Message` class and a `ChatServer` class.
- The `ChatServer` currently stores all messages in a single list on a single machine, representing a non-sharded basic server.
- Wrote a simulation process (`simulate_basic_usage`) to emulate 10 users submitting a total of 50 messages across 5 channels.
- Verified via `stats()` that the system successfully records the data and outputs the aggregate message count.
- **Hidden Complexity Introduced:** The illusion that the system is "complete". All data is stored globally, which provides no separation and will cause memory to grow endlessly under scale.

### ✅ April 4: Scaling Awareness
**Focus:** Users increase 100x, system still single server.
**What was done:**
- Scaled up the test to 10,000 users submitting 100,000 heavy payload messages (`april4_scaling_simulation.py`).
- Measured a **1,628x slowdown** compared to the Day 3 small load baseline.
- Wrote observations in `april4_observation.md`, documenting memory growth and CPU bottlenecks.
- **Hidden Complexity Introduced:** System slowdown and inefficiency — proved the single-server model is fundamentally broken at scale.

### ✅ April 5: Shards Introduction
**Focus:** Multiple servers available but no distribution logic.
**What was done:**
- Created `april5_shards_introduction.py` with independent `Shard` and `ShardManager` classes.
- Each shard has its **own isolated storage** — no global `messages` list exists on the manager.
- Used random routing (intentionally naive) to distribute 10,000 messages across 3 shards.
- Output showed roughly even distribution: Shard 0: 33.5%, Shard 1: 32.3%, Shard 2: 34.2%.
- Built an **independence verification** that proves all shards use separate memory addresses.
- **Hidden Complexity Introduced:** Confusion about routing logic — random assignment works here but won't scale with real requirements (user affinity, channel locality).

### ✅ April 6: User-Based Sharding
**Focus:** One highly active user sends massive traffic — route by `user_id`.
**What was done:**
- Created `april6_user_based_sharding.py` with `UserShardManager` routing via `user_id % num_shards`.
- **Scenario 1 (Normal load):** 1000 users, 10,000 messages → balanced: ~33% per shard. No hotspot.
- **Scenario 2 (Influencer):** user_id=7 sent 5,000 messages → always mapped to Shard 1.
  - Shard 1: **66.2%** of total load  | Shard 0: 16.9% | Shard 2: 17.0%
  -  **HOTSPOT WARNING triggered** automatically by built-in detection.
- **Hidden Complexity Introduced:** Load imbalance. One popular user hijacks an entire shard.
- **Conclusion documented:** User-based sharding is the "First Wrong Decision" — it breaks under any skewed user activity.

### ✅ April 7: Channel-Based Sharding
**Focus:** One channel becomes viral (event spike) — route by `channel_id`.
**What was done:**
- Created `april7_channel_based_sharding.py` with `ChannelShardManager` routing via `channel_id % num_shards`.
- **Scenario 1 (Normal load):** 50 channels, 10,000 messages → balanced: ~33% per shard. No hotspot.
- **Scenario 2 (Viral channel):** channel_id=3 received 8,000 messages → always routed to Shard 0.
  - Shard 0: **85.7%** of total load  | Shard 1: 7.2%  | Shard 2: 7.0% 
  -  **HOTSPOT WARNING triggered** with others completely idle.
- **Comparison with April 6:**
  - User-Based (April 6) under same viral scenario: ~33% balanced — it handles channel spikes fine.
  - Channel-Based (April 7) under viral scenario: **86.2% on one shard** — catastrophic.
  - Conclusion: Each strategy fails for different reasons.
- **Hidden Complexity Introduced:** Hotspot problem — a single viral event funnels ALL traffic into one shard.

### ✅ April 8: Hash-Based Sharding
**Focus:** Better distribution under uneven load — implement hashing and choose the key.
**What was done:**
- Created `april8_hash_based_sharding.py` with 3 hash managers: `HashByUserID`, `HashByChannelID`, `HashByMessageID`.
- Compared all 3 key choices on the same viral channel scenario:
  - Hash `user_id`:  No hotspot — but fails for influencer spikes (April 6 problem persists)
  - Hash `channel_id`:  Shard 1 hit **85.1% load** — same April 7 problem persists
  - Hash `message_id`:  ~33% per shard in BOTH viral AND influencer scenarios
- **Key Choice Justified:** `message_id` chosen because it is globally unique per message — distribution is independent of user/channel activity.
- **Trade-off documented:** Cross-shard queries become expensive — no data locality.
- **System Evolution (3→6 shards):** 32% of message IDs remap to different shards after scaling — proving simple hashing fails when shard count changes.
- **Hidden Complexity Introduced:** Decision complexity — and the limitation that consistent hashing is needed for dynamic scaling.

### ✅ April 9: Stress + Failure Simulation (FINAL DAY)
**Focus:** Normal load, spike load, one server failure — run simulations, disable a shard, test system.
**What was done:**
- Created `april9_stress_failure_simulation.py` covering all 4 mandatory parts:
- **Part 1 — 3 Simulation Scenarios:**
  - Normal day: 1,000 users, 5,000 msgs → ~33% per shard 
  - Viral event: 80% traffic on channel 5 → still balanced with message_id hash 
  - Extreme spike: 50,000 users + influencer → still balanced 
- **Part 2 — Cross-Shard Query:**
  - Fetched last 10 msgs of channel 5 across all 3 shards
  - Performance cost: O(4020 × 3) — ALL shards must be scanned every time
- **Part 3 — Failure Simulation:**
  - Shard 1 disabled mid-test after 5,000 messages
  - Phase 2: **1,675 messages DROPPED** (routed to offline shard)
  - Cross-shard query returned incomplete results (Shard 1 data inaccessible)
  - Hotspot detected on Shard 2 (50.7%) after Shard 1 went offline
- **Part 4 — Final Analysis (all 4 questions answered):**
  - Q1: User-based → Shard 1 fails first (66.2%). Channel-based → Shard 0 fails first (85.7%)
  - Q2: Channel-Based Sharding appeared balanced then catastrophically failed at 85.7% on spike
  - Q3: Scaling 3→10 remaps ~70%+ of keys — needs Consistent Hashing
  - Q4: Shard failure → dropped msgs, lost data, incomplete queries, no auto-redistribution
- **Hidden Complexity Introduced:** Failure handling, data loss, inconsistency, and the limits of all 3 strategies.
