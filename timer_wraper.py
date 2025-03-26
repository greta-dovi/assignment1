import time
from functools import wraps


def timeit(func):
    @wraps(func) # Helps to easily extract name of the function (?)
    def timeit_wrapper(*args, **kwargs): # star allows to pass any parameter, any number
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper