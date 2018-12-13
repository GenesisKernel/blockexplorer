import os
import time
import random

class Error(Exception): pass
class GetFakePidTimeoutError(Error): pass

def check_pid(pid):        
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def get_fake_pid(**kwargs):
    timeout_secs = kwargs.get('timeout_secs', 10)
    end_time = time.time() + timeout_secs
    fake_pid = -1
    while True:
        if time.time() > end_time:
            raise GetFakePidTimeoutError("timeout %d exceeded" % timeout_secs)
        fake_pid = random.randint(1000, 10000)
        if not check_pid(fake_pid):
            break
    return fake_pid

