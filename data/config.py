from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    DELAY_CONN_ACCOUNT: list[int] = [5, 15]
    RANDOM_TAPS_COUNT: list[int] = [5, 200]
    SLEEP_BETWEEN_TAPS: list[int] = [10, 25]
    SLEEP_BY_MIN_TAPS: list[int] = [800, 1200]

    AUTO_EQUIP_BANANA: bool = True

    BLACKLIST_QUESTS: list[str] = ['Bind CARV ID', 'Bind Your Email', 'Bind Your X']

    USE_PROXY_FROM_FILE: bool = False  # True - if use proxy from file, False - if use proxy from accounts.json
    PROXY_PATH: str = "data/proxy.txt"
    PROXY_TYPE_TG: str = "socks5"  # proxy type for tg client. "socks4", "socks5" and "http" are supported
    # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
    PROXY_TYPE_REQUESTS: str = "socks5"

    WORKDIR: str = 'sessions/'

    # timeout in seconds for checking accounts on valid
    TIMEOUT: int = 30


config = Settings()
