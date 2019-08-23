import ipaddress
import os
import errno


def is_ip(string):
    try:
        ipaddress.ip_address(string)
        return True
    except ValueError:
        return False


def check_directory(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
