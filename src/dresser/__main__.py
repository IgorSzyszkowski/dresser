from dresser.select_clothes import Selector
from dresser.get_clothes import ClothingItem

def print_items(clothes: dict[str, ClothingItem | list[ClothingItem]]) -> None:
    categories = ["top_base", "top_mid", "outerwear", "bottoms", "footwear"]
    for key in categories:
        item = clothes.get(key, None)
        print(f"{key}: {None if item == None else item.name}")
    print("accessories: ", end="")
    if clothes.get("accessories", None):
        accessories_str = ""
        for acc in clothes["accessories"]:
            accessories_str += f"{acc}, "
        accessories_str.removesuffix(", ")
        print(accessories_str)
    else:
        print(None)

def main():
    selector = Selector("Manchester", "2026-08-28 20:00", "2026-08-28 21:00")
    clothes = selector.select_clothes()
    print(selector)
    print_items(clothes)
