from parsers.row_item.row_item import RowItem


class CommonPriceGrouper:
    """Группировка результата разбора прайсов поставщиков по параметрам наименований"""

    def __init__(self, items: list[RowItem]):
        self.items = items
        self._is_grouped_items = None

    def group_by_params(self):
        """Группировка списка по параметрам"""
        self.set_order()
        group_id = 0
        current_key = None
        double_items = []
        models = []
        result = sorted(self.items, key=self.group_key)
        for item in result:
            if item.model and item.model not in models:
                models.append(item.model)
            _key = self.group_key(item)
            if current_key != _key:
                current_key = _key
                group_id += 1
                self.mark_double_items(double_items)
                double_items = []
            else:
                double_items.append(item)
            item.group_by_params = group_id

        self.items = sorted(result, key=lambda x: x.order)
        self._is_grouped_items = True
        return self

    def get_items(self):
        return self.items

    @classmethod
    def mark_double_items(cls, items: list[RowItem]):
        """Проставить признаки дублей"""
        if len(items) < 2:
            return

        min_price_item = sorted(items, key=lambda x: x.price_markup)[0]
        for item in items:
            if item.order == min_price_item.order:
                item.double_candidate = True
            else:
                item.is_double = True

    def get_double_count(self) -> int:
        """Получить количество дублей"""
        if not self._is_grouped_items:
            self.group_by_params()
        return len([item for item in self.get_double_items() if item.is_double])

    def get_double_items(self) -> list[RowItem]:
        """Получить список дублей"""
        if not self._is_grouped_items:
            self.group_by_params()
        return [item for item in self.items if item.is_double or item.double_candidate]

    def set_order(self):
        """set order"""
        current_order = 1
        for item in self.items:
            item.order = current_order
            current_order += 1

    @classmethod
    def group_key(cls, item_: RowItem):
        """Ключ группировки"""
        width = item_.width
        diameter = item_.diameter
        profile = item_.height_percent
        velocity = item_.index_velocity
        load = item_.index_load
        model = cls.clear_model(item_.model)
        mark = (item_.manufacturer or "").lower()

        axis = item_.axis
        layering = item_.layering
        intimacy = item_.intimacy or cls.define_intimacy(item_)

        slot_count = item_.slot_count
        dia = item_.central_diameter
        slot_diameter = item_.slot_diameter
        color = item_.color
        _et = item_.eet
        brand = (item_.brand or "").lower()
        if brand == mark:
            brand = ""
        type_prod = (item_.type_production or "").lower()

        return sanitize_value(
            [
                type_prod,
                width,
                diameter,
                profile,
                velocity,
                load,
                model,
                mark,
                axis,
                layering,
                slot_count,
                dia,
                slot_diameter,
                color,
                brand,
                _et,
                intimacy,
            ]
        )

    @classmethod
    def define_intimacy(cls, item: RowItem) -> str | None:
        l_title = item.title.lower()
        diameter = str(item.diameter or 0).replace(",", ".")
        try:
            is_float_diameter = not float(diameter).is_integer()
        except ValueError:
            is_float_diameter = False
        title_chunks = l_title.split(" ")
        title_chunks = [ch.strip() for ch in title_chunks]
        for intimacy_ in ["tl", "tt", "ttf"]:
            if intimacy_ in title_chunks:
                return intimacy_.upper()

        if ("грузовая" in item.type_production.lower()) and is_float_diameter:
            return "TL"
        return None

    @classmethod
    def clear_model(cls, model: str) -> str:
        model = model.replace(" ", "")
        model = model.split("-")
        if len(model) == 1:
            return model[0]
        elif len(model) == 2:
            return model[1]
        else:
            return model[1]
            # raise ValueError("Incorrect value")


def sanitize_value(values: list):
    return tuple([str(value) or "" for value in values])
