"""Stable application errors translated by inbound adapters."""


class CacheUnavailable(Exception):
    pass


class ProviderUnavailable(Exception):
    pass


class QueueUnavailable(Exception):
    pass


class JobNotFound(Exception):
    pass
