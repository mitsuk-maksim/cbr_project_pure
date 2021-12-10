from typing import Optional, Union, List


def parse_int_param(value: str) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError):
        return


def parse_int_params(source: Union[str, List[str]]) -> Union[int, List[int]]:
    """
    parse str to int for list of values
    :param source: ["1,2"] or "1,2,3" or ["1", "2", 3"]
    :return:
    """
    if type(source) == str:
        source = source.split(',')
    try:
        ids = [parse_int_param(value) for value in source]
    except (AttributeError, TypeError):
        return []
    return list(filter(lambda x: x, ids))
