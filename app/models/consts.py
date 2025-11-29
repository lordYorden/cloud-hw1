from zoneinfo import ZoneInfo
from enum import Enum

ZONE = ZoneInfo('Asia/Jerusalem')

class Criteria(Enum):
    ROLE = "byRole"
    EMAIL_DOMAIN = "byEmailDomain"
    REGISTERATION_TODAY = "byRegistrationToday"
