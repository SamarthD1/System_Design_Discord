# Discord System Design Project Progress

This document tracks the daily progress of the scalable chat system simulation, detailing what was accomplished on each day according to the assignment's timeline.

## Assignment Plan & Progress Tracking

| Date | Focus Area | Real Situation | Student Task | Mandatory Submission | Hidden Complexity Introduced | What You Check | Progress Status / Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2 April** | System Thinking | App becomes popular during a live event, 50,000 users join, one channel dominates | Write where system will fail and why | 1-page explanation | Thinking before coding | Do they identify bottlenecks (memory, load, hotspots)? | ✅ **Completed:** CPU, memory, and hotspot bottlenecks clearly identified in `system_failure_analysis.md`. |
| **3 April** | Basic System | Small system works fine with few users | Build chat system (users, channels, messages) | Working code + message count output | Illusion that system is "complete" | Does the system actually store and show data? | ✅ **Completed:** `april3_basic_system.py` stores message objects in a list and `stats()` displays the counts. |
| **4 April** | Scaling Awareness | Users increase 100x, system still single server | Simulate large message load and observe behavior | Code + short observation note | System slowdown and inefficiency | Did they actually simulate load or just write theory? | ✅ **Completed:** Simulated 100,000 messages — measured **1,628x slowdown**. Documented in `april4_observation.md`. |
| **5 April** | Shards Introduction | Multiple servers available but no distribution logic | Create shards and store data separately | Code showing messages per shard | Confusion about routing logic | Are shards independent (no global storage)? | ✅ **Completed:** 3 independent shards verified. Messages per shard output in `april5_shards_introduction.py`. |
| **6 April** | User-Based Sharding | One highly active user sends massive traffic | Route using user_id | Code + shard distribution output | Load imbalance (one shard overloaded) | Do they show uneven distribution clearly? | ⏳ Pending |
| **7 April** | Channel-Based Sharding | One channel becomes viral (event spike) | Route using channel_id | Code + comparison note | Hotspot problem (single shard overload) | Do they compare with previous strategy properly? | ⏳ Pending |
| **8 April** | Hash-Based Sharding | Need better distribution under uneven load | Implement hashing and choose key | Code + explanation of key choice | Decision complexity (what to hash?) | Do they justify their choice logically? | ⏳ Pending |
| **9 April** | Stress + Failure Simulation | Normal load, spike load, and one server failure | Run simulations, disable one shard, test system | Logs + final code + analysis | Failure handling, data loss, inconsistency | Do they observe and explain failure impact? | ⏳ Pending |

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
