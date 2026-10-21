"""The same BatchSource over real SFTP, with paramiko (optional: pip install -r requirements-sftp.txt).

Read-only by construction: the class has no method that writes, renames or deletes on Godavari's server.
Host keys are checked against a known_hosts file the CISO's team provides; AutoAddPolicy is refused,
because "trust whatever answers" is how a vendor ends up sending credentials to the wrong machine.
"""

from __future__ import annotations

import stat as stat_mod
from typing import Any


class ParamikoSource:
    def __init__(self, sftp: Any, root: str = ".") -> None:
        """`sftp` is a paramiko.SFTPClient (or anything with listdir_attr, stat and open)."""
        self.sftp = sftp
        self.root = root.rstrip("/")

    def _p(self, path: str) -> str:
        return f"{self.root}/{path}" if self.root not in ("", ".") else path

    def list_names(self, folder: str) -> list[str]:
        try:
            entries = self.sftp.listdir_attr(self._p(folder))
        except FileNotFoundError:
            return []
        return sorted(e.filename for e in entries if stat_mod.S_ISREG(e.st_mode or 0))

    def size(self, path: str) -> int:
        return int(self.sftp.stat(self._p(path)).st_size)

    def read_bytes(self, path: str) -> bytes:
        with self.sftp.open(self._p(path), "rb") as fh:
            return fh.read()


def connect(host: str, port: int, username: str, key_path: str, known_hosts: str) -> tuple[Any, ParamikoSource]:
    """Open an SFTP session with a key and a pinned host key. Returns (ssh client, source)."""
    import paramiko

    client = paramiko.SSHClient()
    client.load_host_keys(known_hosts)
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, port=port, username=username, key_filename=key_path, allow_agent=False,
                   look_for_keys=False, timeout=15)
    return client, ParamikoSource(client.open_sftp())
