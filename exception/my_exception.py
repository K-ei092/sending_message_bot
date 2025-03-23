class MyCustomException(Exception):
    def __init__(self, message, extra_info):
        super().__init__(message)
        self.extra_info = extra_info

# raise MyCustomException("Произошла ошибка", {"code": 400, "time": "12:34"})
