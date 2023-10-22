class AccountBannedException(Exception):
    def __init__(self, name: str):
        super().__init__(f"Account {name} banned, we cannot convert")
        self.name = name


class AccountNotFoundException(Exception):
    def __init__(self, name: str):
        super().__init__(f"We can not find {name}")
        self.name = name
