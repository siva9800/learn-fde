"""The same pickup over real SFTP, against a throwaway paramiko server on 127.0.0.1 (optional).

Skipped unless paramiko is installed (pip install -r requirements-sftp.txt). The server serves a local
folder read-only; the client is paramiko's real SFTPClient; the pickup report must equal the local one.
"""

from __future__ import annotations

import os
import socket
import threading
from datetime import date
from pathlib import Path

import pytest

paramiko = pytest.importorskip("paramiko")

from godavari_integration import synth_sources as ss  # noqa: E402
from godavari_integration.sftp_batch import LocalFolderSource, PickupLedger, pickup, write_region_drop  # noqa: E402
from godavari_integration.sftp_paramiko import ParamikoSource  # noqa: E402

NIGHT = date(2026, 11, 12)


class _ReadOnlySFTP(paramiko.SFTPServerInterface):
    ROOT = Path(".")

    def _real(self, path: str) -> Path:
        return self.ROOT / path.lstrip("/")

    def list_folder(self, path: str):  # noqa: ANN201
        real = self._real(path)
        if not real.is_dir():
            return paramiko.SFTP_NO_SUCH_FILE
        out = []
        for name in os.listdir(real):
            attr = paramiko.SFTPAttributes.from_stat(os.stat(real / name))
            attr.filename = name
            out.append(attr)
        return out

    def stat(self, path: str):  # noqa: ANN201
        real = self._real(path)
        return paramiko.SFTPAttributes.from_stat(os.stat(real)) if real.exists() else paramiko.SFTP_NO_SUCH_FILE

    lstat = stat

    def open(self, path: str, flags: int, attr):  # noqa: ANN001, ANN201
        if flags & (os.O_WRONLY | os.O_RDWR):
            return paramiko.SFTP_PERMISSION_DENIED                     # a read-only account, as at Godavari
        handle = paramiko.SFTPHandle(flags)
        handle.readfile = open(self._real(path), "rb")                  # noqa: SIM115
        return handle


class _Server(paramiko.ServerInterface):
    def check_auth_password(self, username: str, password: str) -> int:
        return paramiko.AUTH_SUCCESSFUL if (username, password) == ("kaagaz_ro", "test-only") else paramiko.AUTH_FAILED

    def check_channel_request(self, kind: str, chanid: int) -> int:
        return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username: str) -> str:
        return "password"


@pytest.fixture
def sftp_server(tmp_path):
    _ReadOnlySFTP.ROOT = tmp_path / "src"
    host_key = paramiko.RSAKey.generate(2048)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]

    def serve() -> None:
        conn, _ = listener.accept()
        transport = paramiko.Transport(conn)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler("sftp", paramiko.SFTPServer, _ReadOnlySFTP)
        transport.start_server(server=_Server())
        channel = transport.accept(10)               # keep a reference: a collected channel closes itself
        while transport.is_active() and channel is not None:
            transport.join(0.2)

    threading.Thread(target=serve, daemon=True).start()
    yield port, host_key
    listener.close()


def test_pickup_over_sftp_matches_the_local_folder(tmp_path, facts, sftp_server):
    port, host_key = sftp_server
    drops = ss.drop_files(sorted(ss.night_files(facts), key=lambda f: f.file_no)[:4])
    write_region_drop(tmp_path / "src", "HYD", NIGHT, drops, partial=[drops[1].file_no])
    local = pickup(LocalFolderSource(tmp_path / "src"), "HYD", NIGHT, tmp_path / "stage-local", PickupLedger())

    client = paramiko.SSHClient()
    client.get_host_keys().add(f"[127.0.0.1]:{port}", host_key.get_name(), host_key)      # pinned, not auto-added
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("127.0.0.1", port=port, username="kaagaz_ro", password="test-only", allow_agent=False,
                   look_for_keys=False, timeout=10)
    try:
        sftp = client.open_sftp()
        remote = pickup(ParamikoSource(sftp), "HYD", NIGHT, tmp_path / "stage-sftp", PickupLedger())
        with pytest.raises(PermissionError):
            sftp.open("HYD/20261112/x.pdf", "wb")
    finally:
        client.close()
    assert [(i.file_no, i.status) for i in remote.items] == [(i.file_no, i.status) for i in local.items]
    assert remote.count("PARTIAL") == 1 and remote.count("PICKED") == 3
