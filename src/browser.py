import queue
import threading
import logging
from contextlib import contextmanager
from queue import Queue

from DrissionPage import ChromiumPage
from DrissionPage._configs.chromium_options import ChromiumOptions

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


class BrowserPool:
    def __init__(self, max_browsers=4):
        self.max_browsers = max_browsers
        self._browsers = Queue(maxsize=max_browsers)
        self._lock = threading.Lock()
        self._condition = threading.Condition()

        logging.info(f"Initializing browser pool with {max_browsers} Chromium instances...")

        # Pre-warm pool
        for _ in range(max_browsers):
            browser = self._create_browser()
            if browser:
                self._browsers.put(browser)

    def _create_browser(self) -> ChromiumPage:
        opts = ChromiumOptions()
        opts.headless(True)  # Paksa mode headless
        opts.set_argument("--no-sandbox")  # Hindari masalah hak akses
        opts.set_argument("--disable-dev-shm-usage")  # Kurangi penggunaan shared memory
        opts.set_argument("--disable-gpu")  # Nonaktifkan GPU untuk mode headless
        opts.set_argument("--remote-debugging-port=9222")  # Gunakan port debugging

        try:
            logging.debug("Starting Chromium...")
            browser = ChromiumPage(addr_or_opts=opts)

            # Cek apakah browser bisa mengakses halaman
            browser.get("https://www.google.com")
            logging.info("Chromium started successfully.")

            return browser
        except Exception as e:
            logging.error(f"Failed to start Chromium: {e}")
            return None

    @contextmanager
    def browser(self):
        with self._condition:
            # Tunggu hingga browser tersedia
            while self._browsers.empty() and len(self._browsers.queue) >= self.max_browsers:
                self._condition.wait(timeout=5)

            try:
                browser = self._browsers.get_nowait()
            except queue.Empty:
                # Jika pool kosong, buat browser baru jika belum mencapai batas maksimum
                with self._lock:
                    if len(self._browsers.queue) < self.max_browsers:
                        browser = self._create_browser()
                    else:
                        logging.error("Browser pool exhausted")
                        raise RuntimeError("Browser pool exhausted")

        try:
            if browser:
                # Reset browser state sebelum digunakan kembali
                browser.set.cookies.clear()
                browser.run_js("localStorage.clear();")
                browser.run_js("sessionStorage.clear();")
                yield browser
        finally:
            # Kembalikan browser ke pool jika masih valid
            with self._condition:
                if browser:
                    self._browsers.put(browser)
                    self._condition.notify_all()

    def cleanup(self):
        logging.info("Cleaning up browser pool...")
        while not self._browsers.empty():
            browser = self._browsers.get()
            try:
                browser.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {e}")
