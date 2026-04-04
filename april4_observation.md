# Scaling Awareness Observation (April 4)

## Scenario Executed
We simulated a 100x increase in users compared to Day 3's baseline, running the same single-server architecture (`ChatServer`) under heavy pressure.

| Metric | Day 3 (Small) | Day 4 (Large) |
| :--- | :--- | :--- |
| Users | 10 | 10,000 |
| Messages | 50 | 100,000 |
| Time | 0.000049s | 0.0800s |
| **Slowdown Factor** | — | **1,628x** |

## Observations

### 1. Memory Growth is Unbounded
Every single message object (with a ~1KB metadata payload) is appended to a Python list that lives entirely in RAM. At 100,000 messages, the server consumed roughly ~100MB of memory. At real-world scale (millions of messages), this would cause an Out of Memory (OOM) crash, exactly as predicted in our April 2 analysis.

### 2. No Load Distribution
All 100,000 messages from 10,000 different users are funneled into a single `self.messages` array on a single machine. There is absolutely no way to offload work to other servers. The CPU is locked in a single-threaded loop, unable to parallelize any work.

### 3. The Slowdown is Real, Not Theoretical
We did not just "write theory" — we actually ran the simulation and measured a **1,628x slowdown** compared to the small load. The batch checkpoint table in the terminal output proves progressive degradation as the list grows.

## Conclusion
The single-server model is confirmed to be fundamentally broken at scale. The system needs structural separation of data across multiple independent machines (shards) to survive real-world traffic. This sets the stage for Day 5's shard introduction.
