from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserInfo:
    max_click_count: int
    peel_count: int
    equiped_banana_peel_limit: int
    can_claim_lottery: bool
