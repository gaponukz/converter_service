from converter_script import utils

def convert_tdata(path: str) -> list[str]:
    stream = utils.read_file(f"{path}/key_datas")
    salt = stream.read_buffer()

    if len(salt) != 32:
        raise Exception("invalid salt length")

    key_encrypted = stream.read_buffer()
    info_encrypted = stream.read_buffer()

    passcode_key = utils.create_local_key(b"", salt)
    key_inner_data = utils.decrypt_local(key_encrypted, passcode_key)
    local_key = key_inner_data.read(256)

    if len(local_key) != 256:
        raise Exception("invalid local key")

    sessions = []
    info_data = utils.decrypt_local(info_encrypted, local_key)
    count = info_data.read_uint32()

    for _ in range(count):
        index = info_data.read_uint32()
        dc, key = utils.read_user_auth(path, local_key, index)
        ip, port = utils.DC_TABLE[dc]
        sessions.append(utils.build_session(dc, ip, port, key))

    return sessions
