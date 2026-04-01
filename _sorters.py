def dismantling_method(**metadata):
    def decorator(func):
        func.method_info = metadata
        return func

    return decorator
