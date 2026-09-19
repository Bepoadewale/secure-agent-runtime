# Scaling

At one sandbox the API can synchronously run work. At 100 use Redis/PostgreSQL queue, workers, per-tenant concurrency, image cache, object artifacts, and reaper. At 10,000+ use regional cells/control-plane sharding, queue partitions, worker pools by isolation class, capacity reservations/warm pools, distributed artifact/database systems, and strict per-tenant fairness. Warm pools reduce latency but complicate cleanliness; never reuse state without verified reset.
