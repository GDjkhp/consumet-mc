import re


def unpack(source: str):
    """Unpacks P.A.C.K.E.R packed js code"""
    function_regex = r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('.*?'.split"
    parameter_regex = r"\}\('(.*?);?',(\d+),(\d+),'(.*)'"

    match_all = re.findall(function_regex, source)

    if not match_all:
        return

    encoded_string = match_all[-1]

    match = re.search(parameter_regex, encoded_string)

    if not match:
        return

    p = str(match.group(1))
    a = int(match.group(2))
    c = int(match.group(3))
    k = match.group(4).split("|")

    for i in range(c - 1, 0, -1):
        if k[i]:
            regex = r"\b" + _to_base(i, a) + r"\b"
            p = re.sub(regex, k[i], p)

    p = p.replace("\\", "")
    return p


def _to_base(num, base=36):
    if num == 0:
        return "0"
    base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    while num:
        num, rem = divmod(num, base)
        result = base62_chars[rem] + result

    return result
