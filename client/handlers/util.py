from log import GlobalLogger as logger


# 从多个待选key中提取出唯一的val
def extract_kwargs(kwargs, key_list):
    hit_count = 0
    final_val = None

    for key in key_list:
        val = kwargs.get(key, None)
        if val is not None:
            hit_count += 1
            final_val = val

    if hit_count == 0:
        logger.warning('client.handlers.extract_kwargs',
                       f'no hit of keys: {key_list} in kwargs: {kwargs}')
        return None
    elif hit_count == 1:
        return final_val
    else:
        logger.warning('client.handlers.extract_kwargs',
                       f'more than 1 hit of keys: {key_list} in kwargs: {kwargs}')
        return None