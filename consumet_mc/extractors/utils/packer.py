import re


def unpack(source):
    """Unpacks P.A.C.K.E.R packed js code"""
    function_regex = r"eval\(function\((.*?)\)\{.*?return p\}.*?\('(.*?)'.split"
    match = re.search(function_regex, source)
    if not match:
        return

    encoded_string = match.group(0)
    p = encoded_string.split("',36,")[0].strip()
    a = 36
    c = len(encoded_string.split("',36,")[1][2:].split("|"))
    k = encoded_string.split("',36,")[1][2:].split("|")

    for i in range(c - 1, 0, -1):
        if k[i]:
            regex = r"\b" + _to_base(i, a) + r"\b"
            p = re.sub(regex, k[i], p)

    return p


def _to_base(num, base=36):
    if num == 0:
        return "0"
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""
    while num:
        result = digits[num % base] + result
        num //= base
    return result
