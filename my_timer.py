from time import time

def timer(func):

    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        finish = time() - start
        print('Done: {} sec'.format(round(finish, 3)))
        # print(round(finish, 3))
        return result

    return wrapper