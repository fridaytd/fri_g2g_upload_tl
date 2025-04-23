from datetime import datetime


def last_update_message(
    now: datetime,
) -> str:
    formatted_date = now.strftime("%d/%m/%Y %H:%M:%S")
    return formatted_date


def created_offer_message(now: datetime) -> str:
    return f"{last_update_message(now)}: Offer đã được tạo"


def listed_offer_message(now: datetime) -> str:
    return f"{last_update_message(now)}: Offer đã được list"


def listed_offer_no_change_message(now: datetime) -> str:
    return f"{last_update_message(now)}: Offer đã được list, Không cần cập nhật"


def edited_offer_message(now: datetime) -> str:
    return f"{last_update_message(now)}: Offer đã được cập nhật"


def delisted_offer_message(now: datetime) -> str:
    return f"{last_update_message(now)}: Offer đã được delist"


def delisted_offer_no_change_message(now: datetime) -> str:
    return f"{last_update_message(now)}: Offer đã được delist, Không cần cập nhật"
