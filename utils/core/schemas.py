from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserInfo:
    max_click_count: int
    today_click_count: int
    peel_count: int
