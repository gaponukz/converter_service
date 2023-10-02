import os
import io
import json
import struct
import cryptg
import base64
import random
import hashlib
import asyncio
import datetime
import ipaddress
import telethon

from src.infrastructure.converter.utils import entities

DC_TABLE = {
    1: ("149.154.175.50", 443),
    2: ("149.154.167.51", 443),
    3: ("149.154.175.100", 443),
    4: ("149.154.167.91", 443),
    5: ("149.154.171.5", 443),
}


class QDataStream:
    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def read(self, n=None):
        if n < 0:
            n = 0

        data = self.stream.read(n)

        if n != 0 and len(data) == 0:
            return None

        if n is not None and len(data) != n:
            raise Exception("unexpected eof")

        return data

    def read_buffer(self):
        length_bytes = self.read(4)

        if length_bytes is None:
            return None

        length = int.from_bytes(length_bytes, "big", signed=True)
        data = self.read(length)

        if data is None:
            raise Exception("unexpected eof")

        return data

    def read_uint32(self):
        data = self.read(4)

        if data is None:
            return None

        return int.from_bytes(data, "big")

    def read_uint64(self):
        data = self.read(8)

        if data is None:
            return None

        return int.from_bytes(data, "big")

    def read_int32(self):
        data = self.read(4)

        if data is None:
            return None

        return int.from_bytes(data, "big", signed=True)


def create_local_key(passcode, salt):
    if passcode:
        iterations = 100_000

    else:
        iterations = 1

    _hash = hashlib.sha512(salt + passcode + salt).digest()

    return hashlib.pbkdf2_hmac("sha512", _hash, salt, iterations, 256)


def prepare_aes_oldmtp(auth_key, msg_key, send):
    if send:
        x = 0

    else:
        x = 8

    sha1 = hashlib.sha1()
    sha1.update(msg_key)
    sha1.update(auth_key[x:][:32])
    a = sha1.digest()

    sha1 = hashlib.sha1()
    sha1.update(auth_key[32 + x :][:16])
    sha1.update(msg_key)
    sha1.update(auth_key[48 + x :][:16])
    b = sha1.digest()

    sha1 = hashlib.sha1()
    sha1.update(auth_key[64 + x :][:32])
    sha1.update(msg_key)
    c = sha1.digest()

    sha1 = hashlib.sha1()
    sha1.update(msg_key)
    sha1.update(auth_key[96 + x :][:32])
    d = sha1.digest()

    key = a[:8] + b[8:] + c[4:16]
    iv = a[8:] + b[:8] + c[16:] + d[:8]

    return key, iv


def aes_decrypt_local(ciphertext, auth_key, key_128):
    key, iv = prepare_aes_oldmtp(auth_key, key_128, False)

    return cryptg.decrypt_ige(ciphertext, key, iv)


def decrypt_local(data, key):
    encrypted_key = data[:16]
    data = aes_decrypt_local(data[16:], key, encrypted_key)
    sha1 = hashlib.sha1()
    sha1.update(data)

    if encrypted_key != sha1.digest()[:16]:
        raise Exception("failed to decrypt")

    length = int.from_bytes(data[:4], "little")
    data = data[4:length]

    return QDataStream(data)


def read_file(name):
    with open(name, "rb") as f:
        magic = f.read(4)

        if magic != b"TDF$":
            raise Exception("invalid magic")

        version_bytes = f.read(4)
        data = f.read()

    data, digest = data[:-16], data[-16:]
    data_len_bytes = len(data).to_bytes(4, "little")
    md5 = hashlib.md5()

    md5.update(data)
    md5.update(data_len_bytes)
    md5.update(version_bytes)
    md5.update(magic)

    digest = md5.digest()

    if md5.digest() != digest:
        raise Exception("invalid digest")

    return QDataStream(data)


def read_encrypted_file(name, key):
    stream = read_file(name)
    encrypted_data = stream.read_buffer()

    return decrypt_local(encrypted_data, key)


def account_data_string(index=0):
    s = "data"

    if index > 0:
        s += f"#{index+1}"

    md5 = hashlib.md5()
    md5.update(bytes(s, "utf-8"))

    digest = md5.digest()

    return digest[:8][::-1].hex().upper()[::-1]


def read_user_auth(directory, local_key, index=0):
    name = account_data_string(index)
    path = os.path.join(directory, f"{name}s")
    stream = read_encrypted_file(path, local_key)

    if stream.read_uint32() != 0x4B:
        raise Exception("unsupported user auth config")

    stream = QDataStream(stream.read_buffer())
    user_id = stream.read_uint32()
    main_dc = stream.read_uint32()

    if user_id == 0xFFFFFFFF and main_dc == 0xFFFFFFFF:
        user_id = stream.read_uint64()
        main_dc = stream.read_uint32()

    if main_dc not in DC_TABLE:
        raise Exception(f"unsupported main dc: {main_dc}")

    length = stream.read_uint32()

    for _ in range(length):
        auth_dc = stream.read_uint32()
        auth_key = stream.read(256)
        if auth_dc == main_dc:
            return auth_dc, auth_key

    raise Exception("invalid user auth config")


def build_session(dc, ip, port, key):
    ip_bytes = ipaddress.ip_address(ip).packed
    data = struct.pack(">B4sH256s", dc, ip_bytes, port, key)
    encoded_data = base64.urlsafe_b64encode(data).decode("ascii")

    return "1" + encoded_data


def get_random_client() -> entities.UserAgent:
    with open("telegram_useragents.json", "r", encoding="utf-8") as out:
        telegram_useragents = json.load(out)

    device = random.choice(list(telegram_useragents.keys()))
    api_agent = random.choice(telegram_useragents[device])

    return entities.UserAgent(
        api_hash=api_agent["app_hash"],
        api_id=api_agent["app_id"],
        device_model=random.choice(telegram_useragents[device])["device"],
        lang_code=random.choice(telegram_useragents[device])["lang_pack"],
        system_lang_code=random.choice(telegram_useragents[device])["system_lang_pack"],
        system_version=random.choice(telegram_useragents[device])["sdk"],
        app_version=random.choice(telegram_useragents[device])["app_version"],
        proxy=entities.Proxy.from_json_file("proxy.json").to_tuple(),
        use_ipv6=False,
        connection_retries=2,
    )


def setup_client_from_string_session(client: telethon.TelegramClient, session: str):
    dc, ip_bytes, port, key = struct.unpack(
        ">B4sH256s", base64.urlsafe_b64decode(session[1:].encode("ascii"))
    )

    client.session.set_dc(dc, str(ipaddress.ip_address(ip_bytes)), port)
    client.session.auth_key = telethon.crypto.authkey.AuthKey(key)  # ?
    client.session.save()

    client._sender = telethon.network.mtprotosender.MTProtoSender(
        telethon.crypto.authkey.AuthKey(key),
        loggers=client._log,
        retries=client._connection_retries,
        delay=client._retry_delay,
        auto_reconnect=client._auto_reconnect,
        connect_timeout=client._timeout,
        auth_key_callback=client._auth_key_callback,
        auto_reconnect_callback=client._handle_auto_reconnect,
    )


async def get_client_creation_timestamp(client: telethon.TelegramClient) -> float:
    await client.send_message("@creationdatebot", "/start")
    await asyncio.sleep(0.5)

    messages: list[telethon.types.Message] = await client.get_messages(
        "@creationdatebot"
    )
    last_message_text = messages[0].message
    registered = datetime.datetime.strptime(
        last_message_text.split(" registered: ")[-1].split()[0], "%Y-%m-%d"
    )

    return datetime.datetime.timestamp(registered)
