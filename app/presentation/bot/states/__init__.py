from aiogram.fsm.state import State, StatesGroup


class RecommendationStates(StatesGroup):
    budget = State()
    use_case = State()
    brand = State()
    ram = State()
    storage = State()
    five_g = State()
    nfc = State()
    wireless_charging = State()
    esim = State()
    amoled = State()
    high_refresh = State()
    confirm = State()
    results = State()


class SearchStates(StatesGroup):
    query = State()


class FilterStates(StatesGroup):
    query = State()


class CompareStates(StatesGroup):
    selecting = State()


class AdminStates(StatesGroup):
    add_name = State()
    add_brand = State()
    add_price = State()
    add_specs = State()
    add_image = State()
    update_price = State()
