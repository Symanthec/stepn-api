from enum import Enum


class ItemType(Enum):
    SHOES_AND_BOXES = None
    SNEAKERS = '6'
    BOXES = '3'
    GEMS = '5'
    OTHERS = '7'


class Filter(Enum):
    LOWEST_PRICE = 2001
    HIGHEST_PRICE = 2002
    LATEST = 1002


class Chain(Enum):
    SOLANA = 103
    BINANCE = 104
    ETHEREUM = 101


class Rarity(Enum):
    ANY = None
    GENESIS = 1
    OG = 2


class SneakersType(Enum):
    ANY = 0
    WALKER = 1
    JOGGER = 2
    RUNNER = 3
    TRAINER = 4


class GemType(Enum):
    ANY = None
    EFFICIENCY = '1'
    LUCK = '2'
    COMFORT = '3'
    RESILIENCE = '4'


class Quality(Enum):
    ANY = None
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5