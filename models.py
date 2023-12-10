from dataclasses import dataclass, field, astuple


@dataclass
class Item:
    title: str = field(default='')
    price: int = field(default=0)
    discription: str = field(default='')
    manufacturer: str = field(default='')
    screen_diagonal: str = field(default='')
    screen_resolution: str = field(default='')
    operating_system: str = field(default='')
    processor: str = field(default='')
    ram: str = field(default='')
    video_card_type: str = field(default='')
    video_card: str = field(default='')
    storage_type: str = field(default='')
    storage_capacity: str = field(default='')
    battery_life: str = field(default='')
    status: str = field(default='')
    picture: list = field(default_factory=list)


