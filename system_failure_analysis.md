# System Failure Analysis (April 2)

[Napkin Document Link](https://app.napkin.ai/page/CgoiCHByb2Qtb25lEiwKBFBhZ2UaJDNkYjA5NzlkLWU0MjktNGFkNy05ODY2LTk1NDdlYjA0NmE2ZA?s=1)

## Scenario Summary
*   A Discord-like system experiences a sudden spike of **50,000 users joining within 5 minutes**.
*   **One hot channel** receives approximately **80% of total messages**, with spikes reaching thousands of messages per second.
*   The system initially runs on a **single server**.

## 1. Primary Bottlenecks (What Fails First)
*   **CPU Bottleneck:** The server hits 100% CPU due to message parsing, managing thousands of active socket connections, and the intense logic required for broadcasting messages (fan-out).
*   **Network Bandwidth Saturation:** Delivering a 1KB message to 50,000 users at 100 messages/sec results in a **5GB/s** requirement, exceeding typical 1Gbps or 10Gbps single-server network limits.
*   **Memory Exhaustion:** Each open socket and growing message buffers for slow clients consume memory, eventually leading to **Out of Memory (OOM) crashes**.
*   **Database Write Bottleneck:** A single database instance cannot handle the thousands of concurrent writes per second, causing significant latency.

## 2. The Biggest Problem: Hotspot and Fan-out
*   **Hotspot Imbalance:** 80% of activity is concentrated in one channel, making it impossible to distribute load effectively across the system.
*   **Fan-out Problem:** Sending one message to 50,000 people in a single channel is exponentially more expensive than sending 50,000 messages to individual recipients.

## 3. Progressive Degradation and Cascade Failure
*   **Latency Spikes:** Delivery times increase from milliseconds to seconds as resources reach their limits.
*   **Cascading Failure:** One failure triggers another in a loop: CPU overload → message queuing → memory pressure → system slowdown → write backlog → total responsiveness failure.

## Final Conclusion
The system collapse is inevitable because a **single server** lacks horizontal scaling and isolation between channels. The **"hotspot traffic"** in one channel creates resource contention that brings down the entire system through a cascading failure.
