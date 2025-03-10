from typing import Any
import copy
import functools


class SnapshotList:
    class Node:
        def __init__(
            self, commit_hash: str, payload: dict[str, Any], payload_key: str
        ) -> None:
            self.commit_hash = commit_hash
            self._previous_node = None
            self._next_node = None
            self.payload = payload
            self._payload_key = payload_key

        @property
        def next_node(self):
            return self._next_node

        @property
        @functools.cache
        def payload_data(self):
            return {self._payload_key: self.payload[self._payload_key]}

        @property
        def previous_node(self):
            return self._previous_node

        @next_node.setter
        def next_node(self, value: 'Node'):
            self._next_node = value
            if value is not None:
                self.payload['next_snapshot'] = value.commit_hash

        @previous_node.setter
        def previous_node(self, value: 'Node'):
            self._previous_node = value
            if value is not None:
                self.payload['previous_snapshot'] = value.commit_hash

    class Iterator:
        def __init__(self, first: 'Node'):
            self.at = first

        def __next__(self):
            if self.at is None:
                raise StopIteration
            ret = self.at
            self.at = self.at.next_node
            return ret

    def __init__(self):
        self.first_node = None
        self.last_node = None
        self._size = 0

    def size(self):
        return self._size

    def append(self, node: Node) -> None:
        node.previous_node = self.last_node
        self.last_node = node
        if self.first_node is None:
            self.first_node = node
        self._size += 1

    def __iter__(self) -> Iterator:
        return SnapshotList.Iterator(self.first_node)

    def __getitem__(self, index: slice) -> 'SnapshotList':
        ix = 0
        if isinstance(index, slice):
            res = SnapshotList()
            for d in copy.deepcopy(self):
                if ix == index.start:
                    res.first_node = d
                if ix == index.stop or d.next_node is None:
                    res.last_node = d
                ix += 1
            res.last_node.next_node = None
            res.first_node.previous_node = None
        else:
            raise NotImplementedError
        return res

    @staticmethod
    def from_snapshot_dict(snapshot_dict: dict[str, Node]) -> 'SnapshotList':
        res: SnapshotList = SnapshotList()
        for name, definition in snapshot_dict.items():
            if definition.payload['previous_snapshot'] is None and definition.payload['next_snapshot'] is None:
                pass
            elif definition.payload['previous_snapshot'] is None:
                definition.next_node = snapshot_dict[definition.payload['next_snapshot']]
            elif definition.payload['next_snapshot'] is None:
                definition.previous_node = snapshot_dict[definition.payload['previous_snapshot']]
            else:
                definition.next_node = snapshot_dict[definition.payload['next_snapshot']]
                definition.previous_node = snapshot_dict[definition.payload['previous_snapshot']]
            res.append(definition)
        return res

