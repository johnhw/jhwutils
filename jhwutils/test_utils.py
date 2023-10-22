from hashlib import sha1
import sys
from IPython.display import display, HTML
import inspect
import timeit
import binascii 

def case_crc(s):
    h_crc = binascii.crc32(bytes(s.lower(), "ascii"))
    print(h_crc)
    return h_crc

def anagram_crc(l):
    return case_crc("".join(sorted(l)))

def should_fail(test_fn, *args, **kwargs):
    try:
        test_fn(*args, **kwargs)
    except AssertionError:
        return True
    except Exception:		
        return True
    raise AssertionError("Test passed but should not have!")

def should_pass(test_fn, *args, **kwargs):
    try:
        test_fn(*args, **kwargs)
    except AssertionError:
        raise AssertionError("Test did not pass but should have!")    
    return True



def test_execution_time(slow, fast):
    
    base_time = timeit.timeit("slow()", globals={"slow":slow}, number=1)
    fast_time = timeit.timeit("fast()", globals={"fast":fast}, number=1)

    ratio = base_time / fast_time
    return ratio


def report_execution_time(fast):

    ratio = test_execution_time(_crack_the_code_slow, fast)
    print()
    print("Speed ratio: {ratio:.1f}x faster".format(ratio=ratio))

    if ratio>2 and ratio<5:
        print("A little faster, but way too slow")
        boom()
    
    if ratio>5 and ratio<10:
        print("Faster, but not fast enough")
        boom()
    if ratio>10 and ratio<100:
        print("10x faster, but the bomb will still relock")
        boom()
    if ratio>100 and ratio<1000:
        print("100x faster, still too slow")
        boom()
    if ratio>1000 and ratio<5000:
        print("More than 1000x faster, unlocked in time!")
    if ratio>5000:
        print("More than 5000x faster, good job!")



def short_hash(v):
    sha = sha1(str(v).encode('utf8')).hexdigest()[0:8]
    return sha

def fail_if_debug():
    debugging = any(['bdb' in f.filename for f in inspect.getouterframes(inspect.currentframe())])
    if debugging or sys.gettrace() is not None:
        display(HTML('<marquee> <div class="alert alert-box alert-danger"> <h1> Hey, I told you not to use the debugger </h1> </div> </marquee>'))
        boom(shake_times=5, duration=10.5, p=1.0)
        raise Exception("User cannot follow instructions, cat detonated.")        


