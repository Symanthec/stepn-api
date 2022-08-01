from ..util import URLParams
from .enums import *

from typing import *


class OrderQuery(URLParams):
    __parameters: Optional[Dict[str, Any]] = None

    __param_labels = {
        Filter: "order",
        Chain: "chain",
        "refresh": "refresh",
        "page": "page",
        Rarity: "otd",
        "type": "type",
        GemType: "gType",
        Quality: "quality",
        "level": "level",
        "mints": "bread"
    }

    __primary_type: ItemType = ItemType.SHOES_AND_BOXES
    __secondary_type: Optional[str] = None

    def __label_for(self, key):
        if key in self.__param_labels:
            return self.__param_labels[key]
        return ''

    @property
    def parameters(self) -> Optional[Dict[Any, str]]:
        return self.__parameters

    @parameters.setter
    def parameters(self, value: dict):
        if not self.__parameters and type(value) == dict:
            self.__parameters = value
        pass

    def set_param(self, param_label_key: Any, value: Union[str, int, bool, None, Enum]):
        self.parameters[self.__label_for(param_label_key)] = value.value if isinstance(value, Enum) else value
        return self

    def get_param(self, param_label_key: Any):
        return self.parameters[self.__label_for(param_label_key)]

    def __init__(self):
        self.parameters = dict()
        self.default_request()

    def default_request(self):
        return (self.set_filter(Filter.LOWEST_PRICE)
                .set_chain(Chain.SOLANA)
                .do_refresh(True)
                .set_page(0)
                .set_rarity(Rarity.ANY)
                .set_item_type(ItemType.SHOES_AND_BOXES)
                .set_shoe_type(SneakersType.ANY)
                .set_gem_type(GemType.ANY)
                .set_quality(Quality.ANY)
                .set_shoe_levels(None))

    def set_filter(self, item_filter: Filter):
        """ Finished """
        return self.set_param(Filter, item_filter)

    def set_chain(self, chain: Chain):
        """ Finished """
        return self.set_param(Chain, chain)

    def do_refresh(self, do_refresh: bool):
        """ Finished """
        return self.set_param("refresh", do_refresh)

    def set_page(self, page: int):
        """ Finished """
        return self.set_param("page", page)

    def set_rarity(self, rarity: Rarity):
        """ Finished """
        return self.set_param(Rarity, rarity)

    def set_item_type(self, item_type: ItemType):
        """ Finished """
        self.__primary_type = item_type
        return self

    def set_shoe_type(self, shoe_type: Optional[SneakersType]):
        """ Finished """
        self.__secondary_type = shoe_type.value
        return self

    def set_gem_type(self, gem_type: GemType):
        """ Finished """
        return self.set_param(GemType, gem_type)

    def set_quality(self, quality: Quality):
        """ Finished """
        return self.set_param(Quality, quality)

    def set_gem_quality(self, levels: Optional[List[int]]):
        """ Finished """
        return self.set_param('level', bake_range(levels, [1, 9]) if levels else '0')

    def set_shoe_levels(self, levels: Optional[List[int]]):
        """ Finished """
        return self.set_param('level', bake_range(levels, [0, 30]) if levels else '0')

    def set_mint_range(self, mint_range: Optional[List[int]]):
        """ Finished """
        return self.set_param('mints', bake_range(mint_range, [0, 7]) if mint_range else '0')

    def compile(self) -> dict:
        # type finalization
        if self.__primary_type is ItemType.SHOES_AND_BOXES:
            final_type = self.__primary_type.value
        elif self.__primary_type is ItemType.SNEAKERS:
            final_type = self.__primary_type.value + '0' + str(self.__secondary_type or SneakersType.ANY.value)
        else:
            final_type = self.__primary_type.value + '0' + '1'
        self.set_param('type', final_type)

        if self.__primary_type is not ItemType.SNEAKERS:
            # mint is only with sneakers
            self.set_mint_range(None)
            if self.__primary_type is not ItemType.GEMS:
                self.set_shoe_levels(None)

        if self.__primary_type is ItemType.GEMS:
            # quality is not present in gems
            self.set_quality(Quality.ANY)
        else:
            # gem type is not present outside gems
            self.set_gem_type(GemType.ANY)

        return self.parameters

    def clear(self) -> None:
        self.parameters.clear()


def bake_range(level_range: List[int], caps: List[int]):
    level_range.sort()
    caps.sort()
    start, end = map(lambda x: clamp(caps[0], x, caps[1]) + 1, level_range)
    return "%d0%02d" % (start, end)


def clamp(minimum, value, maximum):
    return max(minimum, min(value, maximum))
