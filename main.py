import asyncio
import copy

from math import ceil
from stepn.search import *
from stepn.util import login

queries = [
    # By quality
    OrderQuery().set_item_type(ItemType.SNEAKERS).set_quality(Quality.COMMON).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.SNEAKERS).set_quality(Quality.UNCOMMON).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.SNEAKERS).set_quality(Quality.RARE).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.SNEAKERS).set_quality(Quality.EPIC).set_filter(Filter.LATEST),
    # By rarity
    OrderQuery().set_item_type(ItemType.SNEAKERS).set_rarity(Rarity.OG).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.SNEAKERS).set_rarity(Rarity.GENESIS).set_filter(Filter.LATEST),
    # Boxes
    OrderQuery().set_item_type(ItemType.BOXES).set_quality(Quality.COMMON).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.BOXES).set_quality(Quality.UNCOMMON).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.BOXES).set_quality(Quality.RARE).set_filter(Filter.LATEST),
    OrderQuery().set_item_type(ItemType.BOXES).set_quality(Quality.EPIC).set_filter(Filter.LATEST),
    # Gems
]
update_queries = [copy.copy(q).set_filter(Filter.LOWEST_PRICE) for q in queries]
query_to_floor = dict()

orders = dict()
running = True


def get_selling_price(price, basis_unit: int):
    return ceil(price / 0.94 + 0.01 * basis_unit)


def can_buy(price, floor):
    return get_selling_price(price, 1000000) <= floor


def fp(x):
    return str(x / 1e6)


async def update_floors(client):
    global query_to_floor
    while running:
        for i in range(len(queries)):
            query_to_floor[queries[i]] = get_floor_price(client, update_queries[i].compile())
        print("Floor prices updated")
        await asyncio.sleep(1800)  # half an hour


def get_floor_price(client, query: dict):
    # check not single and not very small
    shoes = client.list_orders(**query)
    return shoes[0]['sellPrice'] if shoes and len(shoes) > 0 else 0


async def seller_task(client):
    while running:
        processed = 0
        for q in queries:
            if q in query_to_floor:
                # can process
                q_orders = client.list_orders(**q.compile())
                for order in q_orders:
                    processed += 1
                    order_id = order['id']
                    price = order['sellPrice']
                    floor = query_to_floor[q]
                    if can_buy(price, floor):
                        if input(
                                f"Buy item for query ({q.compile()}) for {fp(price)} (floor = {fp(floor)})? (Y):") == "Y":
                            if client.buy_prop(order_id, price):
                                print(f"Bought prop #{order_id} for {fp(price)}")
                                orders[order['id']] = order['sellPrice']
        print(f"Scanned {processed} props")
        await asyncio.sleep(10)


async def main():
    if client := login(anonymous_mode=False):
        print("Logged in!")
        tasks = set()
        sol_asset = list(filter(lambda asset: asset['token'] == 1003, client.userbasic().get_data()['asset']))[0]

        solana = sol_asset['value']

        updater = asyncio.create_task(update_floors(client))
        seller = asyncio.create_task(seller_task(client))

        tasks.add(updater)
        tasks.add(seller)

        await asyncio.wait(tasks)


if __name__ == '__main__':
    asyncio.run(main())
