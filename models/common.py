class Page:
    def __init__(self, items, page, page_count):
        self.items = items
        self.page = page
        self.page_count = page_count


class Sorting:
    def __init__(self):
        self.field = None
        self.direction = None

    @staticmethod
    def from_request(request):
        sorting = Sorting()
        sorting.field = request.args.get("sort_field")
        sorting.direction = request.args.get("sort_dir", "desc").lower()
        return sorting


class ValueFilter:
    def __init__(self, field, value):
        self.field = field
        self.value = value

    @staticmethod
    def extract_list_from_request(request, keys):
        result = []
        request_keys = list(request.args.keys())
        for key in keys:
            if key not in request_keys:
                continue

            result.append(ValueFilter(key, request.args[key]))
        return result


class IntervalFilter:
    def __init__(self, field, value_from, value_to):
        self.field = field
        self.value_from = value_from
        self.value_to = value_to


class Paging:
    def __init__(self):
        self.page = None
        self.page_size = None

    @staticmethod
    def from_request(request):
        def to_int(value, default_value=0) -> int:
            try:
                return int(value)
            except ValueError:
                return default_value
            except TypeError:
                return default_value

        result = Paging()
        result.page = to_int(request.args.get("page"), 1)
        result.page_size = to_int(request.args.get("page_size"), 10)
        return result
