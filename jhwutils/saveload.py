import lzma, base64
import inspect, pickle


def tob64lzma(bytes):
    return base64.b64encode(lzma.compress(bytes))


def fromb64lzma(bytes):
    return lzma.decompress(base64.b64decode(bytes))


def loadfunc(bytes):
    exec(fromb64lzma(bytes))


def loadobj(bytes):
    return pickle.loads(fromb64lzma(bytes))


def savefunc(func):
    return tob64lzma(inspect.getsource(func).encode("utf-8"))


def saveobj(obj):
    return tob64lzma(pickle.dumps(obj))
