class Result:
    def __init__(self, data: dict):
        self.__data = data

    def __getattr__(self, name):
        if name in self.__data:
            return self.__data[name]
        raise AttributeError(f"'Result' object has no attribute '{name}'")

    def as_dict(self):
        return self.__data
