import threading
import time

from DrissionPage.common import Settings
from sanic.log import logger

from browser import BrowserPool
from debouncer import Debouncer

Settings.set_language("en")
pool = BrowserPool(max_browsers=4)


def turnstile(url: str) -> str:
	with pool.browser() as browser:
		page = browser.get_tabs()[-1]

		if isinstance(page, str):
			logger.warning(f"Failed to connect to target: {page}")
			raise Exception("Failure during connection to target")

		browser.listen.start("cdn-cgi")
		debouncer = Debouncer(0.5)
		page.get(url)

		def intercept_turnstile_background():
			try:
				for _ in browser.listen.steps():
					if not debouncer.call():  # Will return False when expired
						break
			except Exception as e:
				logger.error(f"Listener error: {e}")

		logger.debug("Waiting for turnstile to finish loading...")
		thread = threading.Thread(target=intercept_turnstile_background)
		thread.start()

		try:
			debouncer.wait()
		finally:
			browser.listen.stop()
			debouncer.stop()
			thread.join(timeout=1)  # Wait max 1 second for thread to finish

		logger.debug("Turnstile javascript loaded, getting token...")

		def get_token() -> str:
			page.wait.doc_loaded()

			for _ in range(0, 15):
				try:
					token = page.run_js(
						"try { return turnstile.getResponse() } catch(e) { return null }"
					)
					if token:
						return token
				except Exception:
					pass

				time.sleep(1)

			raise Exception(
				"Exceeded 15 attempts to solve turnstile, please try again later."
			)

		return get_token()
