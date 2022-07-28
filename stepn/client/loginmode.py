from enum import Enum


class LoginMode(Enum):
    AUTHCODE = 4  # 2-factor authentication code
    PASSWORD = 3  # real password
