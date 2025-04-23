from enum import Enum


class OfferStatus(Enum):
    LIVE = "live"
    DELISTED = "delisted"
    DELISTED_BY_G2G = "delisted_by_g2g"
