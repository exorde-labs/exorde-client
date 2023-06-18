import pickle

class SingletonDriver:
    _instance = None
    _driver = None
    _cookies_file = 'cookies.pkl'
    _site = 'https://twitter.com'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonDriver, cls).__new__(cls)
        return cls._instance

    @property
    def driver(self):
        return self._driver

    @property
    def is_driver_initialized(self):
        return self._driver is not None

    def set_driver(self, driver):
        self._driver = driver
        self.load_cookies()

    def load_cookies(self):
        if self._driver is not None:
            self._driver.get(self._site)
            try:
                cookies = pickle.load(open(self._cookies_file, "rb"))
                for cookie in cookies:
                    self._driver.add_cookie(cookie)
            except FileNotFoundError:
                pass

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self._cookies_file, "wb"))

    def quit_driver(self):
        self.save_cookies()
        if self._driver:
            self._driver.quit()
            self._driver = None

    @staticmethod
    def refresh_session():
        instance = SingletonDriver()
        if instance.is_driver_initialized:
            instance.driver.refresh()
