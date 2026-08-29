"""Main entry point for the Dresser application.

Executes the clothing selection workflow for a specified city and time window,
then formats and prints the weather summary and outfit recommendations to stdout.
"""

from dresser.get_clothes import ClothingItem
from dresser.select_clothes import Selector


def print_items(clothes: dict[str, ClothingItem | list[str]]) -> None:
    """Formats and prints selected clothing items and accessories to the console.

    Args:
        clothes (dict[str, ClothingItem | list[str]]): Dictionary mapping clothing
            category keys ('top_base', 'top_mid', 'outerwear', 'bottoms', 'footwear') to
            ClothingItem instances, and 'accessories' to a list of accessory names.
    """
    categories = ["top_base", "top_mid", "outerwear", "bottoms", "footwear"]
    for key in categories:
        item = clothes.get(key, None)
        name = item.name if isinstance(item, ClothingItem) else None
        print(f"{key}: {name}")

    print("accessories: ", end="")
    accessories = clothes.get("accessories", [])
    if isinstance(accessories, list) and accessories:
        print(", ".join(accessories))
    else:
        print(None)

def main() -> None:
    """Runs the clothing selection workflow for Kraków over a 4-hour forecast window."""
    selector = Selector("Krasnystaw", hours=4)
    clothes = selector.select_clothes()
    print(selector)
    print_items(clothes)


if __name__ == "__main__":
    main()
