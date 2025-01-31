import queue
import threading
from contextlib import contextmanager
from queue import Queue

from DrissionPage import ChromiumPage
from DrissionPage._configs.chromium_options import ChromiumOptions


class BrowserPool:
    def __init__(self, max_browsers=4):
        self.max_browsers = max_browsers
        self._browsers = Queue(maxsize=max_browsers)
        self._lock = threading.Lock()
        self._condition = threading.Condition()

        # Pre-warm pool
        for _ in range(max_browsers):
            self._browsers.put(self._create_browser())

    def _create_browser(self) -> ChromiumPage:
        try:
            opts = ChromiumOptions()
            opts.headless()
            opts.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
            opts.args = ["--no-sandbox", "--headless", "--remote-debugging-port=9222"]
            browser = ChromiumPage(addr_or_opts=opts)

            browser.get("https://www.google.com")
            return browser
        except Exception as e:
            print(f"Error creating browser: {e}")
            raise RuntimeError("Failed to create browser")

    @contextmanager
    def browser(self):
        with self._condition:
            # Wait for browser to become available
            while self._browsers.empty() and len(self._browsers.queue) < self.max_browsers:
                self._condition.wait(timeout=5)

            try:
                browser = self._browsers.get_nowait()
            except queue.Empty:
                # Create new browser if under max limit
                with self._lock:
                    if len(self._browsers.queue) < self.max_browsers:
                        browser = self._create_browser()
                    else:
                        raise RuntimeError("Browser pool exhausted")

        try:
            # Reset browser state
            browser.set.cookies.clear()
            browser.run_js("localStorage.clear();")
            browser.run_js("sessionStorage.clear();")
            yield browser
        finally:
            # Return browser to pool
            with self._condition:
                self._browsers.put(browser)
                self._condition.notify_all()

    def cleanup(self):
        while not self._browsers.empty():
            browser = self._browsers.get()
            try:
                browser.quit()
            except Exception as e:
                print(f"Error quitting browser: {e}")
