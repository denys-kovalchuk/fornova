import json
from config import Variables


def cycle_through_json(json_data: dict[str: list, str: dict]) -> \
        list[tuple[tuple[tuple[str, float] | tuple[None, None], int | None], dict[str: float] | None]]:
    """Cycles the json data to find the necessary information"""
    cycle_result = []
    for element in json_data:
        if type(json_data[element]) == list:
            for entry in json_data[element]:
                try:
                    cheapest = determine_minimum(entry[Variables.SHOWN_PRICE])
                except KeyError:
                    try:
                        cheapest = determine_minimum(entry[Variables.NET_PRICE])
                    except KeyError:
                        print('No prices available')
                        cheapest = None, None
                try:
                    guests_number = int(entry[Variables.NUMBER_OF_GUESTS])
                except KeyError:
                    print('No guest number available')
                    guests_number = None
                try:
                    total_taxes = calculate_taxes(entry[Variables.EXT_DATA])
                except KeyError:
                    print('No taxes info available')
                    total_taxes = None
                try:
                    total = calculate_total_price(entry[Variables.NET_PRICE], total_taxes)
                except KeyError:
                    try:
                        total = calculate_total_price(entry[Variables.SHOWN_PRICE], total_taxes)
                    except KeyError:
                        print('No prices available')
                        total = None
                cycle_result.append(((cheapest, guests_number), total))
    return cycle_result


def determine_minimum(rooms: dict[str: str]) -> tuple[str, float]:
    """Determines the room with the minimum price without using min() function"""
    first_room = next(iter(rooms))
    cheapest = float(rooms[first_room])
    cheapest_room = first_room
    for room in rooms:
        price = rooms[room]
        if float(price) < cheapest:
            cheapest = float(price)
            cheapest_room = room
    return cheapest_room, round(cheapest, 2)


def calculate_taxes(ext_data: dict[str: float | str: None, str: json]) -> float:
    """Calculates total amount of taxes"""
    taxes = json.loads(ext_data[Variables.TAXES])
    total_taxes = 0
    for tax in taxes.values():
        total_taxes += float(tax)
    return total_taxes


def calculate_total_price(rooms: dict[str: str], taxes: float | None) -> dict[str: float]:
    """Calculates total price based on room price and total amount of taxes"""
    if taxes is None:
        return rooms
    total_price = {}
    for room, price in rooms.items():
        total_price[room] = round(float(price) + taxes, 2)
    return total_price


def write_output(output_data: list[tuple[tuple[tuple[str, float] |
                                               tuple[None, None], int | None], dict[str: float] | None]],
                 filename: str) -> bool:
    """Writes an output into a json file"""
    with open(f'./{filename}', 'w') as f:
        for entry in output_data:
            cheapest_room = {'cheapest_room_type': entry[0][0][0], 'cheapest_price': entry[0][0][1],
                             'number_of_guests': entry[0][1]}
            total_room_price = {room: price for room, price in entry[1].items()}
            output = {'cheapest_room': cheapest_room, 'total_room_price': total_room_price}
            json.dump(output, f, indent=4)
            print(f'Data written successfully to {filename} file')
    return True


if __name__ == '__main__':
    with open('./Python-task.json', 'r') as file:
        data = json.load(file)
    result = cycle_through_json(data)
    write_output(result, Variables.OUTPUT_FILE)
