# Twelve-Factor App

The Twelve-Factor App is a set of deployment and operational principles for services. The factors support one another, but they are not implementation stages.

This topic keeps factor-specific demos here and reuses relevant database, Redis, queue, logging, and migration demos from the main curriculum.

| # | Factor | Main question | Demo |
| --- | --- | --- | --- |
| I | Codebase | Which code and revision are deployed? | [Codebase](codebase.ipynb) |
| II | Dependencies | Can a clean environment reproduce the packages? | [Dependencies](dependencies.ipynb) |
| III | Config | Which values change between deployments? | [Config](config.ipynb) |
| IV | Backing services | Can databases, caches, and queues be replaced through configuration? | [Redis](../05-cache-jobs/redis.ipynb) · [Queue](../05-cache-jobs/queue.ipynb) |
| V | Build, release, run | Are build, release, and runtime kept separate? | [Build, release, run](release.ipynb) |
| VI | Processes | Can processes be replaced without losing shared state? | [Processes](processes.ipynb) |
| VII | Port binding | Does the service expose itself through a configured port? | [Port binding](port.ipynb) |
| VIII | Concurrency | Can web and worker process types scale independently? | [Concurrency](concurrency.ipynb) |
| IX | Disposability | Can processes start quickly and stop gracefully? | [Disposability](disposability.ipynb) |
| X | Dev/prod parity | Do environments use the same code, dependencies, and service types? | [Dev/prod parity](parity.ipynb) |
| XI | Logs | Does the process emit events to standard output? | [Logging](../06-reliability-test/logging.ipynb) |
| XII | Admin processes | Do migrations run from the same release and configuration? | [Migrations](../03-database/migrations.ipynb) |
