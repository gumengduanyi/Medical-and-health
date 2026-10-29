import hashlib
import threading
import time
import uuid
from copy import deepcopy


class CandidateStore:
    def __init__(self, ttl=1800, capacity=100):
        self.ttl = ttl
        self.capacity = capacity
        self.lock = threading.Lock()
        self.entries = {}

    def remember(self, owner, identity, document):
        with self.lock:
            now = time.monotonic()
            self.entries = {key: value for key, value in self.entries.items() if value[0] > now}
            while len(self.entries) >= self.capacity:
                self.entries.pop(next(iter(self.entries)))
            key = uuid.uuid4().hex
            digest = hashlib.sha256(document.html).hexdigest()
            self.entries[key] = (now + self.ttl, owner, deepcopy(identity), document, digest)
            return key, digest

    def resolve(self, key, owner, identity, digest):
        with self.lock:
            item = self.entries.get(key)
            if not item or item[0] <= time.monotonic() or item[1] != owner:
                raise ValueError("采集候选已过期或不属于当前用户，请重新发现并确认")
            if item[2] != identity or item[4] != digest:
                raise ValueError("药品身份或内容版本已变化，请重新发现并确认")
            return item[3]


candidate_store = CandidateStore()
