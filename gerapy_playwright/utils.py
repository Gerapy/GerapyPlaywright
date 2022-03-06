from subprocess import Popen, PIPE
from playwright.async_api import async_playwright
from os.path import exists
import functools


def bytes2str(data):
    """
    bytes2str
    :param data: origin data
    :return: str
    """
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    data = data.strip()
    return data


def install_playwright():
    """
    install playwright
    """
    p = Popen(['playwright', 'install'], shell=False,
              stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.wait()
    stdout, stderr = bytes2str(p.stdout.read()), bytes2str(p.stderr.read())
    if not stderr:
        return True


def async_to_sync(fn):
    '''
    turn an async function to sync function
    '''
    import asyncio

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return asyncio.get_event_loop().run_until_complete(res)
        return res

    return wrapper


@async_to_sync
async def is_playwright_installed():
    """
    check if playwright is installed
    """
    async with async_playwright() as playwright:
        return exists(playwright.chromium.executable_path)
