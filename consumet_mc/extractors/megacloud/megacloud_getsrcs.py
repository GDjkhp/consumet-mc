import base64
import json
import re
import struct
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, cast

import requests
from wasmer.wasmer import (
    Function,
    FunctionType,
    Instance,
    Module,
    Store,
    Type,
    engine,
)
from wasmer_compiler_cranelift.wasmer_compiler_cranelift import Compiler

from consumet_mc.extractors.megacloud.megacloud_decodedpng import decoded_png
from consumet_mc.utils import crypto

# pyright: reportUnusedParameter=false

wasm: Any
arr: List = [None] * 128
date_now: float = int(time.time() * 1000)
referer: str = ""
user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
store = Store(engine.Universal(Compiler))
data_view = None
memory_buff = None
size = 0


data_url = "data:image/png;base64,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JDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAtwCFrnv+pEcAAQQQECJAoQsZJDEQQAABBHQLUOi65096BBBAAAEhAhS6kEESAwEEEEBAt8D/ATY93seMmImHAAAAAElFTkSuQmCC"


class Undefined:
    pass


class F64:
    pass


@dataclass
class Meta:
    content: str


@dataclass
class ImageData:
    height: int
    width: int
    data: Any


@dataclass
class Image:
    src: str
    height: int
    width: int
    complete: bool


@dataclass
class NodeList:
    image: Image
    context2d: None
    length: int

    def __len__(self):
        return len(self.__dataclass_fields__)


class FakeStorage:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def setItem(self, key: str, value: Any):
        self._data[key] = value

    def getItem(self, key: str, default_return: Optional[Any] = None):
        return self._data.get(key, default_return)


@dataclass
class Navigator:
    webdriver: bool
    userAgent: str


@dataclass
class Performance:
    time_origin: float


@dataclass
class Document:
    cookie: str


@dataclass
class Location:
    href: str
    origin: str


class FakeWindow:
    def __init__(self) -> None:
        self.localStorage: FakeStorage = FakeStorage()
        self.error: bool = False
        self.navigator: Navigator = Navigator(False, user_agent)
        self.length: int = 0
        self.document: Document = Document("")
        self.origin: str = ""
        self.location: Location = Location("", "")
        self.performance: Performance = Performance(float(date_now))
        self.xrax: str = ""
        self.c: bool = False
        self.G: str = ""
        self.crypto = crypto
        self.msCrypto = crypto
        self.browser_version = 1878522368

    def z(self, a: Any):
        return [(4278190080 & a) >> 24, (16711680 & a) >> 16, (65280 & a) >> 8, 255 & a]


@dataclass
class Canvas:
    base_url: str
    width: int
    height: int
    style: Dict
    context2d: Any


undefined = Undefined()
arr.extend([Undefined, None, True, False])
pointer = len(arr)
image_data = ImageData(50, 65, decoded_png)
meta = Meta("")
fake_window = FakeWindow()
canvas = Canvas("", 0, 0, {"style": {"display": "inline"}}, None)
node_list = NodeList(Image("", 50, 65, True), None, 1)


def get_meta(url: str):
    headers = {"userAgent": user_agent, "Referrer": referer}
    resp = requests.get(url, headers=headers)
    txt = resp.text
    regx = r'name="j_crt" content="[A-Za-z0-9]*"'
    regx = r"name=\"j_crt\" content=\"[A-Za-z0-9]*"
    match = re.search(regx, txt)
    content: str = ""
    if match:
        content = match.group(0)[match.group(0).rindex('"') + 1 :]
    meta.content = content + "=="


def get(index: int):
    return arr[index]


def shift(QP: int):
    if QP >= 132:
        global pointer
        arr[QP] = pointer
        pointer = QP


def shift_get(QP: int):
    Qn = get(QP)
    shift(QP)
    return Qn


def add_to_stack(item: Any):
    global pointer
    if pointer == len(arr):
        arr.append(len(arr) + 1)
    Qn = pointer
    pointer = arr[Qn]
    arr[Qn] = item
    return Qn


def args(QP, Qn, QT, func):
    Qx = {
        "a": QP,
        "b": Qn,
        "cnt": 1,
        "dtor": QT,
    }

    def wrapper(*Qw):
        Qx["cnt"] += 1
        try:
            return func(Qx["a"], Qx["b"], *Qw)
        finally:
            Qx["cnt"] -= 1
            if Qx["cnt"] == 0:
                wasm.__wbindgen_export_2.get(Qx["dtor"])(Qx["a"], Qx["b"])
                Qx["a"] = 0

    return wrapper


def export3(QP: Any, Qn: Any):
    return shift_get(wasm.__wbindgen_export_3(QP, Qn))


def export4(Qy: Any, QO: Any, QX: Any):
    index = add_to_stack(QX)
    wasm.__wbindgen_export_4(Qy, QO, index)


def export5(QP: Any, Qn: Any):
    wasm.__wbindgen_export_5(QP, Qn)


def is_none(test: Any):
    return test is None


def is_detached(buf):
    try:
        _ = len(buf)
        return False
    except ValueError:
        return True


def get_data_view():
    global data_view

    if data_view is None or is_detached(data_view):
        data_view = memoryview(wasm.memory.buffer)
    return data_view


def write_int32_le(buf: memoryview, offset: int, value: int):
    struct.pack_into("<i", buf, offset, value)


def write_float64_le(buf: memoryview, offset: int, value: int):
    struct.pack_into("<d", buf, offset, value)


def read_int32_le(buf: memoryview, offset: int):
    return struct.unpack_from("<i", buf, offset)[0]


def decode_sub(index: int, offset: int):
    index &= 0xFFFFFFFF
    mem = get_mem_buff()
    slice_ = bytearray(mem[index : index + offset])
    slice_decoded = slice_.decode("utf-8")
    return slice_decoded


def apply_to_window(func: Callable[..., int], *args) -> int:
    try:
        return func(*args)
    except Exception as e:
        wasm.__wbindgen_export_6(add_to_stack(e))
        return -1


def encode(text: str, array: memoryview) -> dict:
    encoded = text.encode("utf-8")
    written = len(encoded)
    array[:written] = encoded
    return {"read": len(text), "written": written}


def get_mem_buff():
    global memory_buff
    if memory_buff is not None and len(memory_buff) > 0:
        return memory_buff

    memory_buff = wasm.memory.uint8_view()
    return memory_buff


def Qj(QP: Sequence[int], Qn: Any):
    global size
    Qn = Qn(len(QP), 1) & 0xFFFFFFFF
    _buffer = get_mem_buff()
    _buffer[Qn : Qn + len(QP)] = QP

    size = len(QP)
    return Qn


def parse(text: str, func, func2=None):
    global size
    buffer = get_mem_buff()

    if func2 is None:
        encoded = text.encode("utf-8")
        parsed_index = func(len(encoded), 1)
        parsed_index &= 0xFFFFFFFF
        buffer[parsed_index : parsed_index + len(encoded)] = encoded
        size = len(encoded)
        return parsed_index

    len_text = len(text)
    parsed_len = func(len_text, 1)
    parsed_len &= 0xFFFFFFFF

    i = 0
    for i in range(len_text):
        char = ord(text[i])
        if 127 < char:
            break
        buffer[parsed_len + i] = char

    i += 1
    if i != len_text:
        if i != 0:
            text = text[i:]
        len_text_mod = i + (3 * len(text))
        parsed_len = func2(parsed_len, len_text, len_text_mod, 1)
        len_text = len_text_mod
        parsed_len &= 0xFFFFFFFF

        encoded_buf = get_mem_buff()[parsed_len + i : parsed_len + len_text]
        # encode() writes to buffer and returns number of bytes written
        result = encode(text, encoded_buf)
        i += result["written"]

        parsed_len = func2(parsed_len, len_text, i, 1)
        parsed_len &= 0xFFFFFFFF

    size = i
    return parsed_len


def init_wasm():
    def __wbindgen_is_function(index: int) -> int:
        raise NotImplementedError("__wbindgen_is_function not implemented")

    def __wbindgen_is_string(index: int) -> int:
        raise NotImplementedError("__wbindgen_is_string not implemented")

    def __wbindgen_is_object(index: int) -> int:
        obj = get(index)
        is_object = isinstance(obj, object) and obj is not None
        return is_object

    def __wbindgen_number_get(offset: int, index: int):
        number = get(index)
        _view = get_data_view()
        write_float64_le(_view, offset + 8, 0 if number is None else number)
        write_int32_le(_view, offset, 0 if number is None else 1)

    def __wbindgen_string_get(offset: int, index: int):
        # todo
        str = get(index)
        val = parse(str, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1)
        _view = get_data_view()
        write_int32_le(_view, offset + 4, size)
        write_int32_le(_view, offset, val)

    def __wbindgen_object_drop_ref(index: int):
        shift_get(index)

    def __wbindgen_cb_drop(index: int) -> int:
        raise NotImplementedError("__wbindgen_cb_drop not implemented")

    def __wbindgen_string_new(index: int, offset: int) -> int:
        return add_to_stack(decode_sub(index, offset))

    def __wbindgen_is_null(index: int):
        return get(index) is None

    def __wbindgen_is_undefined(index: int) -> bool:
        return get(index) == undefined

    def __wbindgen_boolean_get(index: int) -> int:
        _boolean = get(index)
        if type(_boolean) is bool:
            if _boolean:
                return 1
            else:
                return 0
        else:
            return 2

    def __wbg_instanceof_CanvasRenderingContext2d_4ec30ddd3f29f8f9(val: int) -> int:
        return True

    def __wbg_subarray_adc418253d76e2f1(index: int, num1: int, num2: int) -> int:
        num1 = num1 & 0xFFFFFFFF
        num2 = num2 & 0xFFFFFFFF
        return add_to_stack(memoryview(get(index))[num1:num2])

    def __wbg_randomFillSync_5c9c955aa56b6049(val: int, val2: int):
        raise NotImplementedError(
            "__wbg_randomFillSync_5c9c955aa56b6049 not implemented"
        )

    def __wbg_getRandomValues_3aa56aa6edec874c(index: int, index2: int):
        return apply_to_window(get(index).get_random_values, get(index2))

    def __wbg_msCrypto_eb05e62b530a1508(index: int) -> int:
        raise NotImplementedError("__wbg_msCrypto_eb05e62b530a1508 not implemented")

    def __wbg_toString_6eb7c1f755c00453(index: int) -> int:
        fakestr = "[object Storage]"
        return add_to_stack(fakestr)

    def __wbg_toString_139023ab33acec36(index: int) -> int:
        return add_to_stack(str(get(index)))

    def __wbg_require_cca90b1a94a0255b() -> int:
        raise NotImplementedError("__wbg_require_cca90b1a94a0255b not implemented")

    def __wbg_crypto_1d1f22824a6a080c(index: int) -> int:
        return add_to_stack(get(index).crypto)

    def __wbg_process_4a72847cc503995b(index: int) -> int:
        return add_to_stack(get(index).process)

    def __wbg_versions_f686565e586dd935(index: int) -> int:
        raise NotImplementedError("__wbg_versions_f686565e586dd935 not implemented")

    def __wbg_node_104a2ff8d6ea03a2(index: int) -> int:
        raise NotImplementedError("__wbg_node_104a2ff8d6ea03a2 not implemented")

    def __wbg_localStorage_3d538af21ea07fcc(index: int) -> int:
        def _f(index):
            data = fake_window.localStorage
            return 0 if is_none(data) else add_to_stack(data)

        return apply_to_window(_f, index)

    def __wbg_setfillStyle_59f426135f52910f(val: int, val2: int):
        pass

    def __wbg_setshadowBlur_229c56539d02f401(val: int, val2: "F64"):  # type: ignore[name-defined] # noqa: F821
        pass

    def __wbg_setshadowColor_340d5290cdc4ae9d(val: int, val2: int, val3: int):
        pass

    def __wbg_setfont_16d6e31e06a420a5(val: int, val2: int, val3: int):
        pass

    def __wbg_settextBaseline_c3266d3bd4a6695c(val: int, val2: int, val3: int):
        pass

    def __wbg_drawImage_cb13768a1bdc04bd(val: int, val2: int, val3: "F64", val4: "F64"):  # type: ignore[name-defined] # noqa: F821
        pass

    def __wbg_getImageData_66269d289f37d3c7(
        val: int,
        val2: "F64",  # type: ignore[name-defined] # noqa: F821
        val3: "F64",  # type: ignore[name-defined] # noqa: F821
        val4: "F64",  # type: ignore[name-defined] # noqa: F821
        val5: "F64",  # type: ignore[name-defined] # noqa: F821
    ) -> int:
        return add_to_stack(image_data)

    def __wbg_rect_2fa1df87ef638738(
        val: int,
        val2: "F64",
        val3: "F64",
        val4: "F64",
        val5: "F64",
    ):
        pass

    def __wbg_fillRect_4dd28e628381d240(
        val: int, val2: "F64", val3: "F64", val4: "F64", val5: "F64"
    ):
        pass

    def __wbg_fillText_07e5da9e41652f20(
        val: int, val2: int, val3: int, val4: "F64", val5: "F64"
    ):
        pass

    def __wbg_setProperty_5144ddce66bbde41(
        val: int, val2: int, val3: int, val4: int, val5: int
    ):
        return 0

    def __wbg_createElement_03cf347ddad1c8c0(
        index: int, decodeIndex: int, decodeIndexOffset: int
    ) -> int:
        return apply_to_window(lambda: add_to_stack(canvas))

    def __wbg_querySelector_118a0639aa1f51cd(
        index: int, decodeIndex: int, decodeOffset: int
    ) -> int:
        return apply_to_window(lambda: add_to_stack(meta))

    def __wbg_querySelectorAll_50c79cd4f7573825(val: int, val2: int, val3: int) -> int:
        return apply_to_window(lambda: add_to_stack(node_list))

    def __wbg_getAttribute_706ae88bd37410fa(
        offset: int, index: int, decodeIndex: int, decodeOffset: int
    ):
        attr = meta.content
        todo = (
            0
            if is_none(attr)
            else parse(attr, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1)
        )
        _view = get_data_view()
        write_int32_le(_view, offset + 4, size)
        write_int32_le(_view, offset, todo)

    def __wbg_target_6795373f170fd786(index: int) -> int:
        raise NotImplementedError("__wbg_target_6795373f170fd786 not implemented")

    def __wbg_addEventListener_f984e99465a6a7f4(
        val: int, val2: int, val3: int, val4: int
    ):
        raise NotImplementedError(
            "__wbg_addEventListener_f984e99465a6a7f4 not implemented"
        )

    def __wbg_instanceof_HtmlCanvasElement_1e81f71f630e46bc(index: int) -> int:
        return True

    def __wbg_setwidth_233645b297bb3318(index: int, set: int):
        get(index).width = set & 0xFFFFFFFF

    def __wbg_setheight_fcb491cf54e3527c(index: int, set: int):
        get(index).height = set & 0xFFFFFFFF

    def __wbg_getContext_dfc91ab0837db1d1(index: int, val1: int, val2: int) -> int:
        def _f(x):
            return add_to_stack(get(x).context2d)

        return apply_to_window(_f, index)

    def __wbg_toDataURL_97b108dd1a4b7454(offset: int, index: int):
        def _f(offset, index):
            _data_url = parse(
                data_url, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1
            )
            _view = get_data_view()
            write_int32_le(_view, offset + 4, size)
            write_int32_le(_view, offset, _data_url)
            return 0

        return apply_to_window(_f, offset, index)

    def __wbg_instanceof_HtmlDocument_1100f8a983ca79f9():
        raise NotImplementedError(
            "__wbg_instanceof_HtmlDocument_1100f8a983ca79f9 not implemented"
        )

    def __wbg_style_ca229e3326b3c3fb(index: int) -> int:
        add_to_stack(get(index).style)
        return 0

    def __wbg_instanceof_HtmlImageElement_9c82d4e3651a8533(index: int) -> int:
        return True

    def __wbg_src_87a0e38af6229364(offset: int, index: int):
        _src = parse(get(index).src, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1)
        _view = get_data_view()
        write_int32_le(_view, offset + 4, size)
        write_int32_le(_view, offset, _src)

    def __wbg_width_e1a38bdd483e1283(index: int) -> int:
        return get(index).width

    def __wbg_height_e4cc2294187313c9(index: int) -> int:
        return get(index).height

    def __wbg_complete_1162c2697406af11(index: int) -> int:
        return get(index).complete

    def __wbg_data_d34dc554f90b8652(offset: int, index: int):
        _data = Qj(get(index).data, wasm.__wbindgen_export_0)
        _view = get_data_view()
        write_int32_le(_view, offset + 4, size)
        write_int32_le(_view, offset, _data)

    def __wbg_origin_305402044aa148ce(index: int, val2: int):
        def _f(offset, index):
            _origin = parse(
                get(index).origin, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1
            )
            _view = get_data_view()
            write_int32_le(_view, offset + 4, size)
            write_int32_le(_view, offset, _origin)
            return 0

        return apply_to_window(_f, index, val2)

    def __wbg_length_8a9352f7b7360c37(index: int) -> int:
        return get(index).length

    def __wbg_get_c30ae0782d86747f(index: int, offset: int) -> int:
        _image = get(index).image
        if _image is None:
            return 0
        return add_to_stack(_image)

    def __wbg_timeOrigin_f462952854d802ec(index: int) -> "F64":
        return get(index).time_origin

    def __wbg_instanceof_Window_cee7a886d55e7df5(val: int) -> int:
        return 1

    def __wbg_document_eb7fd66bde3ee213(index: int) -> int:
        doc = get(index).document
        if doc is None:
            return 0
        return add_to_stack(doc)

    def __wbg_location_b17760ac7977a47a(index: int) -> int:
        return add_to_stack(get(index).location)

    def __wbg_performance_4ca1873776fdb3d2(index: int) -> int:
        _performance = get(index).performance
        return 0 if is_none(_performance) else add_to_stack(_performance)

    def __wbg_origin_e1f8acdeb3a39a2b(offset: int, index: int):
        _origin = parse(
            get(index).origin, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1
        )
        _view = get_data_view()
        write_int32_le(_view, offset + 4, size)
        write_int32_le(_view, offset, _origin)

    def __wbg_get_8986951b1ee310e0(index: int, decode1: int, decode2: int) -> int:
        data = getattr(get(index), decode_sub(decode1, decode2), undefined)
        return 0 if is_none(data) else add_to_stack(data)

    def __wbg_setTimeout_6ed7182ebad5d297(val: int, val2: int, val3: int) -> int:
        return apply_to_window(lambda: 7)

    def __wbg_self_05040bd9523805b9() -> int:
        return apply_to_window(lambda: add_to_stack(fake_window))

    def __wbg_window_adc720039f2cb14f() -> int:
        raise NotImplementedError("__wbg_window_adc720039f2cb14f not implemented")

    def __wbg_globalThis_622105db80c1457d() -> int:
        raise NotImplementedError("__wbg_globalThis_622105db80c1457d not implemented")

    def __wbg_global_f56b013ed9bcf359() -> int:
        raise NotImplementedError("__wbg_global_f56b013ed9bcf359 not implemented")

    def __wbg_newnoargs_cfecb3965268594c(index: int, offset: int) -> int:
        raise NotImplementedError("__wbg_newnoargs_cfecb3965268594c not implemented")

    def __wbindgen_object_clone_ref(index: int) -> int:
        return add_to_stack(get(index))

    def __wbg_eval_c824e170787ad184(index: int, offset: int) -> int:
        def _f(index, offset):
            fake_str = "fake_" + decode_sub(index, offset)
            ev = None
            try:
                try:
                    ev = eval(fake_str)
                except AttributeError:
                    ev = undefined
            except SyntaxError:
                ev = exec(fake_str)

            return add_to_stack(ev)

        return apply_to_window(_f, index, offset)

    def __wbg_call_3f093dd26d5569f8(index: int, index2: int) -> int:
        raise NotImplementedError("__wbg_call_3f093dd26d5569f8 not implemented")

    def __wbg_call_67f2111acd2dfdb6(index: int, index2: int, index3: int) -> int:
        raise NotImplementedError("__wbg_call_67f2111acd2dfdb6 not implemented")

    def __wbg_set_961700853a212a39(index: int, index2: int, index3: int) -> int:
        def _f(index, index2, index3):
            obj = get(index)
            key = get(index2)
            value = get(index3)
            setattr(obj, key, value)
            return 0

        return apply_to_window(_f, index, index2, index3)

    def __wbg_buffer_b914fb8b50ebbc3e(index: int) -> int:
        return add_to_stack(memoryview(get(index).buffer))

    def __wbg_newwithbyteoffsetandlength_0de9ee56e9f6ee6e(
        index: int, val: int, val2: int
    ) -> int:
        val = val & 0xFFFFFFFF
        val2 = val2 & 0xFFFFFFFF
        return add_to_stack(memoryview(get(index))[val : val + val2].tobytes())

    def __wbg_newwithlength_0d03cef43b68a530(length: int) -> int:
        return add_to_stack(bytearray(int(length) & 0xFFFFFFFF))

    def __wbg_new_b1f2d6842d615181(index: int) -> int:
        return add_to_stack(memoryview(get(index)))

    def __wbg_buffer_67e624f5a0ab2319(index: int) -> int:
        return add_to_stack(get(index).obj)

    def __wbg_length_21c4b0ae73cba59d(index: int) -> int:
        return len(get(index))

    def __wbg_set_7d988c98e6ced92d(index: int, index2: int, val: int):
        val = val & 0xFFFFFFFF
        get(index)[val : val + len(get(index2))] = get(index2)

    def __wbindgen_debug_string():
        raise NotImplementedError("__wbindgen_debug_string not implemented")

    def __wbindgen_throw(index: int, offset: int):
        raise NotImplementedError("__wbindgen_throw not implemented")

    def __wbindgen_memory() -> int:
        return add_to_stack(wasm.memory)

    def __wbindgen_closure_wrapper117(Qn: int, QT: int, QV: int) -> int:
        return add_to_stack(args(Qn, QT, 2, export3))

    def __wbindgen_closure_wrapper119(Qn: int, QT: int, QV: int) -> int:
        return add_to_stack(args(Qn, QT, 2, export4))

    def __wbindgen_closure_wrapper121(Qn: int, QT: int, QV: int) -> int:
        return add_to_stack(args(Qn, QT, 2, export5))

    def __wbindgen_closure_wrapper123(Qn: int, QT: int, QV: int) -> int:
        return add_to_stack(args(Qn, QT, 9, export4))

    wasm_obj = {
        "wbg": {
            "__wbindgen_is_function": Function(store, __wbindgen_is_function),
            "__wbindgen_is_string": Function(store, __wbindgen_is_string),
            "__wbindgen_is_object": Function(store, __wbindgen_is_object),
            "__wbindgen_number_get": Function(store, __wbindgen_number_get),
            "__wbindgen_string_get": Function(store, __wbindgen_string_get),
            "__wbindgen_object_drop_ref": Function(store, __wbindgen_object_drop_ref),
            "__wbindgen_cb_drop": Function(store, __wbindgen_cb_drop),
            "__wbindgen_string_new": Function(store, __wbindgen_string_new),
            "__wbindgen_is_null": Function(
                store, __wbindgen_is_null, FunctionType([Type.I32], [Type.I32])
            ),
            "__wbindgen_is_undefined": Function(
                store, __wbindgen_is_undefined, FunctionType([Type.I32], [Type.I32])
            ),
            "__wbindgen_boolean_get": Function(store, __wbindgen_boolean_get),
            "__wbg_instanceof_CanvasRenderingContext2d_4ec30ddd3f29f8f9": Function(
                store, __wbg_instanceof_CanvasRenderingContext2d_4ec30ddd3f29f8f9
            ),
            "__wbg_subarray_adc418253d76e2f1": Function(
                store, __wbg_subarray_adc418253d76e2f1
            ),
            "__wbg_randomFillSync_5c9c955aa56b6049": Function(
                store, __wbg_randomFillSync_5c9c955aa56b6049
            ),
            "__wbg_getRandomValues_3aa56aa6edec874c": Function(
                store, __wbg_getRandomValues_3aa56aa6edec874c
            ),
            "__wbg_msCrypto_eb05e62b530a1508": Function(
                store, __wbg_msCrypto_eb05e62b530a1508
            ),
            "__wbg_toString_6eb7c1f755c00453": Function(
                store, __wbg_toString_6eb7c1f755c00453
            ),
            "__wbg_toString_139023ab33acec36": Function(
                store, __wbg_toString_139023ab33acec36
            ),
            "__wbg_require_cca90b1a94a0255b": Function(
                store, __wbg_require_cca90b1a94a0255b
            ),
            "__wbg_crypto_1d1f22824a6a080c": Function(
                store, __wbg_crypto_1d1f22824a6a080c
            ),
            "__wbg_process_4a72847cc503995b": Function(
                store, __wbg_process_4a72847cc503995b
            ),
            "__wbg_versions_f686565e586dd935": Function(
                store, __wbg_versions_f686565e586dd935
            ),
            "__wbg_node_104a2ff8d6ea03a2": Function(store, __wbg_node_104a2ff8d6ea03a2),
            "__wbg_localStorage_3d538af21ea07fcc": Function(
                store, __wbg_localStorage_3d538af21ea07fcc
            ),
            "__wbg_setfillStyle_59f426135f52910f": Function(
                store, __wbg_setfillStyle_59f426135f52910f
            ),
            "__wbg_setshadowBlur_229c56539d02f401": Function(
                store, __wbg_setshadowBlur_229c56539d02f401
            ),
            "__wbg_setshadowColor_340d5290cdc4ae9d": Function(
                store, __wbg_setshadowColor_340d5290cdc4ae9d
            ),
            "__wbg_setfont_16d6e31e06a420a5": Function(
                store, __wbg_setfont_16d6e31e06a420a5
            ),
            "__wbg_settextBaseline_c3266d3bd4a6695c": Function(
                store, __wbg_settextBaseline_c3266d3bd4a6695c
            ),
            "__wbg_drawImage_cb13768a1bdc04bd": Function(
                store, __wbg_drawImage_cb13768a1bdc04bd
            ),
            "__wbg_getImageData_66269d289f37d3c7": Function(
                store, __wbg_getImageData_66269d289f37d3c7
            ),
            "__wbg_rect_2fa1df87ef638738": Function(store, __wbg_rect_2fa1df87ef638738),
            "__wbg_fillRect_4dd28e628381d240": Function(
                store, __wbg_fillRect_4dd28e628381d240
            ),
            "__wbg_fillText_07e5da9e41652f20": Function(
                store, __wbg_fillText_07e5da9e41652f20
            ),
            "__wbg_setProperty_5144ddce66bbde41": Function(
                store, __wbg_setProperty_5144ddce66bbde41
            ),
            "__wbg_createElement_03cf347ddad1c8c0": Function(
                store, __wbg_createElement_03cf347ddad1c8c0
            ),
            "__wbg_querySelector_118a0639aa1f51cd": Function(
                store, __wbg_querySelector_118a0639aa1f51cd
            ),
            "__wbg_querySelectorAll_50c79cd4f7573825": Function(
                store, __wbg_querySelectorAll_50c79cd4f7573825
            ),
            "__wbg_getAttribute_706ae88bd37410fa": Function(
                store, __wbg_getAttribute_706ae88bd37410fa
            ),
            "__wbg_target_6795373f170fd786": Function(
                store, __wbg_target_6795373f170fd786
            ),
            "__wbg_addEventListener_f984e99465a6a7f4": Function(
                store, __wbg_addEventListener_f984e99465a6a7f4
            ),
            "__wbg_instanceof_HtmlCanvasElement_1e81f71f630e46bc": Function(
                store, __wbg_instanceof_HtmlCanvasElement_1e81f71f630e46bc
            ),
            "__wbg_setwidth_233645b297bb3318": Function(
                store, __wbg_setwidth_233645b297bb3318
            ),
            "__wbg_setheight_fcb491cf54e3527c": Function(
                store, __wbg_setheight_fcb491cf54e3527c
            ),
            "__wbg_getContext_dfc91ab0837db1d1": Function(
                store, __wbg_getContext_dfc91ab0837db1d1
            ),
            "__wbg_toDataURL_97b108dd1a4b7454": Function(
                store, __wbg_toDataURL_97b108dd1a4b7454
            ),
            "__wbg_instanceof_HtmlDocument_1100f8a983ca79f9": Function(
                store, __wbg_instanceof_HtmlDocument_1100f8a983ca79f9
            ),
            "__wbg_style_ca229e3326b3c3fb": Function(
                store, __wbg_style_ca229e3326b3c3fb
            ),
            "__wbg_instanceof_HtmlImageElement_9c82d4e3651a8533": Function(
                store, __wbg_instanceof_HtmlImageElement_9c82d4e3651a8533
            ),
            "__wbg_src_87a0e38af6229364": Function(store, __wbg_src_87a0e38af6229364),
            "__wbg_width_e1a38bdd483e1283": Function(
                store, __wbg_width_e1a38bdd483e1283
            ),
            "__wbg_height_e4cc2294187313c9": Function(
                store, __wbg_height_e4cc2294187313c9
            ),
            "__wbg_complete_1162c2697406af11": Function(
                store, __wbg_complete_1162c2697406af11
            ),
            "__wbg_data_d34dc554f90b8652": Function(store, __wbg_data_d34dc554f90b8652),
            "__wbg_origin_305402044aa148ce": Function(
                store, __wbg_origin_305402044aa148ce
            ),
            "__wbg_length_8a9352f7b7360c37": Function(
                store, __wbg_length_8a9352f7b7360c37
            ),
            "__wbg_get_c30ae0782d86747f": Function(store, __wbg_get_c30ae0782d86747f),
            "__wbg_timeOrigin_f462952854d802ec": Function(
                store, __wbg_timeOrigin_f462952854d802ec
            ),
            "__wbg_instanceof_Window_cee7a886d55e7df5": Function(
                store, __wbg_instanceof_Window_cee7a886d55e7df5
            ),
            "__wbg_document_eb7fd66bde3ee213": Function(
                store, __wbg_document_eb7fd66bde3ee213
            ),
            "__wbg_location_b17760ac7977a47a": Function(
                store, __wbg_location_b17760ac7977a47a
            ),
            "__wbg_performance_4ca1873776fdb3d2": Function(
                store, __wbg_performance_4ca1873776fdb3d2
            ),
            "__wbg_origin_e1f8acdeb3a39a2b": Function(
                store, __wbg_origin_e1f8acdeb3a39a2b
            ),
            "__wbg_get_8986951b1ee310e0": Function(store, __wbg_get_8986951b1ee310e0),
            "__wbg_setTimeout_6ed7182ebad5d297": Function(
                store, __wbg_setTimeout_6ed7182ebad5d297
            ),
            "__wbg_self_05040bd9523805b9": Function(store, __wbg_self_05040bd9523805b9),
            "__wbg_window_adc720039f2cb14f": Function(
                store, __wbg_window_adc720039f2cb14f
            ),
            "__wbg_globalThis_622105db80c1457d": Function(
                store, __wbg_globalThis_622105db80c1457d
            ),
            "__wbg_global_f56b013ed9bcf359": Function(
                store, __wbg_global_f56b013ed9bcf359
            ),
            "__wbg_newnoargs_cfecb3965268594c": Function(
                store, __wbg_newnoargs_cfecb3965268594c
            ),
            "__wbindgen_object_clone_ref": Function(store, __wbindgen_object_clone_ref),
            "__wbg_eval_c824e170787ad184": Function(store, __wbg_eval_c824e170787ad184),
            "__wbg_call_3f093dd26d5569f8": Function(store, __wbg_call_3f093dd26d5569f8),
            "__wbg_call_67f2111acd2dfdb6": Function(store, __wbg_call_67f2111acd2dfdb6),
            "__wbg_set_961700853a212a39": Function(store, __wbg_set_961700853a212a39),
            "__wbg_buffer_b914fb8b50ebbc3e": Function(
                store, __wbg_buffer_b914fb8b50ebbc3e
            ),
            "__wbg_newwithbyteoffsetandlength_0de9ee56e9f6ee6e": Function(
                store, __wbg_newwithbyteoffsetandlength_0de9ee56e9f6ee6e
            ),
            "__wbg_newwithlength_0d03cef43b68a530": Function(
                store, __wbg_newwithlength_0d03cef43b68a530
            ),
            "__wbg_new_b1f2d6842d615181": Function(store, __wbg_new_b1f2d6842d615181),
            "__wbg_buffer_67e624f5a0ab2319": Function(
                store, __wbg_buffer_67e624f5a0ab2319
            ),
            "__wbg_length_21c4b0ae73cba59d": Function(
                store, __wbg_length_21c4b0ae73cba59d
            ),
            "__wbg_set_7d988c98e6ced92d": Function(store, __wbg_set_7d988c98e6ced92d),
            "__wbindgen_debug_string": Function(store, __wbindgen_debug_string),
            "__wbindgen_throw": Function(store, __wbindgen_throw),
            "__wbindgen_memory": Function(store, __wbindgen_memory),
            "__wbindgen_closure_wrapper117": Function(
                store, __wbindgen_closure_wrapper117
            ),
            "__wbindgen_closure_wrapper119": Function(
                store, __wbindgen_closure_wrapper119
            ),
            "__wbindgen_closure_wrapper121": Function(
                store, __wbindgen_closure_wrapper121
            ),
            "__wbindgen_closure_wrapper123": Function(
                store, __wbindgen_closure_wrapper123
            ),
        }
    }

    return wasm_obj


def QN(QP, Qn):
    QT = None
    Qt = None

    if isinstance(QP, requests.Response):
        QT = QP.raw.data
        module = Module(store, QT)
        Qt = Instance(module, Qn)
        return {"bytes": QT, "instance": Qt, "module": module}
    else:
        if isinstance(QP, Module):
            Qt = Instance(QP, Qn)
            return {
                "instance": Qt,
                "module": QP,
            }
        else:
            module = Module(store, QP)
            Qt = Instance(module, Qn)
            return {"bytes": QP, "instance": Qt, "module": module}


def assign_wasm(instance):
    global wasm
    global data_view
    global memory_buff
    wasm = instance.exports
    data_view = None
    memory_buff = None


def QZ(QP):
    global wasm

    if wasm is not None:
        return wasm
    else:
        Qn = init_wasm()

        if not isinstance(QP, Module):
            QP = Module(store, QP)

        instance = Instance(QP, Qn)
        wasm = assign_wasm(instance)
        return wasm


def load_wasm(url: Any):
    mod = init_wasm()

    response = requests.get(url, stream=True)
    response.raise_for_status()
    result = QN(response, mod)

    instance = result.get("instance", url)
    buffer = result.get("bytes")

    assign_wasm(instance)

    return buffer


def groot():
    global wasm
    wasm.groot()


def init(QP: Any):
    QZ(QP)


wasm_loader = {"load_wasm": load_wasm, "groot": groot, "init": init}


def V(url: str):
    try:
        Q0 = wasm_loader["load_wasm"](url)
        wasm_loader["groot"]()
        jwt_plugin = getattr(fake_window, "jwt_plugin")
        jwt_plugin(Q0)
    except Exception as e:
        raise Exception("wasm_load_error: ", e)


def i(a: bytearray, P: List[int]):
    try:
        for Q0 in range(len(a)):
            a[Q0] = a[Q0] ^ P[Q0 % len(P)]
    except Exception:
        return None


def M(a: Any, P: Any):
    try:
        Q0 = crypto.aes_decrypt(a, P)
        return json.loads(Q0)
    except Exception:
        return {}


def z(a: Any):
    return [(a & 4278190080) >> 24, (a & 16711680) >> 16, (a & 65280) >> 8, a & 255]


def get_sources(embed_url: str, site: str):
    global referer
    referer = site
    parts = embed_url.split("/")
    last_part = parts[-1] if parts else ""
    xrax = last_part.split("?")[0] if last_part else ""

    regx = r"https://[a-zA-Z0-9.]*"
    base_url_match = re.match(regx, embed_url)
    if not base_url_match:
        return
    base_url = base_url_match.group(0)
    node_list.image.src = "{}/images/image.png?v=0.0.9".format(base_url)
    test = embed_url.split("/")

    fake_window.xrax = xrax
    fake_window.G = xrax
    canvas.base_url = base_url
    fake_window.origin = base_url
    fake_window.location.origin = base_url
    fake_window.location.href = embed_url

    get_meta(embed_url)

    browser_version = 1878522368

    try:
        V(base_url + "/images/loading.png?v=0.0.9")
        get_sources_url = ""
        if "mega" in base_url:
            get_sources_url = (
                base_url
                + "/"
                + test[3]
                + "/ajax/"
                + test[4]
                + "/getSources?id="
                + getattr(fake_window, "pid", "undefined")
                + "&v="
                + str(fake_window.localStorage.getItem("kversion", "undefined"))
                + "&h="
                + str(fake_window.localStorage.getItem("kid", "undefined"))
                + "&b="
                + str(browser_version)
            )
        else:
            get_sources_url = (
                base_url
                + "/ajax/"
                + test[3]
                + "/"
                + test[4]
                + "/getSources?id="
                + getattr(fake_window, "pid", "undefined")
                + "&v="
                + str(fake_window.localStorage.getItem("kversion", "undefined"))
                + "&h="
                + str(fake_window.localStorage.getItem("kid", "undefined"))
                + "&b="
                + str(browser_version)
            )
        headers = {
            "User-Agent": user_agent,
            "Referer": embed_url,
            "X-Requested-With": "XMLHttpRequest",
        }
        response = requests.get(get_sources_url, headers=headers)
        response.raise_for_status()
        response_dict = response.json()

        Q3 = cast(int, fake_window.localStorage.getItem("kversion", 0))
        Q1 = fake_window.z(int(Q3))
        navigate = getattr(fake_window, "navigate")
        Q5 = navigate()
        q5_byte_arr = bytearray(Q5)
        Q8: Any = None

        if "t" in response_dict and response_dict["t"] != 0:
            i(q5_byte_arr, Q1)
            Q8 = q5_byte_arr
        elif "k" in response_dict:
            Q8 = bytearray(response_dict.k)
            i(Q8, Q1)

        if Q8:
            key = str(base64.b64encode(Q8).decode("utf-8"))
            sources = M(response_dict["sources"], key)
            if sources:
                response_dict["sources"] = sources
        return response_dict

    except Exception as e:
        raise e
