"""
Playwright helper - finds system Chrome/Edge/Brave so we don't need
to download Playwright's bundled Chromium (which is blocked in Iran).

Usage:
    from core.crawlers.playwright_helper import get_chromium_executable, launch_browser
    exe = get_chromium_executable()  # returns path or None
    with launch_browser() as (browser, context): ...
"""
import os
import sys
import logging
import subprocess

logger = logging.getLogger(__name__)

# Common browser executable paths on Windows
_WIN_BROWSER_PATHS = [
    # Google Chrome
    os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
    os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
    os.path.expandvars(r'%LocalAppData%\Google\Chrome\Application\chrome.exe'),
    # Microsoft Edge (Chromium-based)
    os.path.expandvars(r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe'),
    os.path.expandvars(r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe'),
    # Brave
    os.path.expandvars(r'%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe'),
    os.path.expandvars(r'%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe'),
    # Opera
    os.path.expandvars(r'%LocalAppData%\Programs\Opera\launcher.exe'),
    # Firefox (Gecko, not Chromium - won't work with playwright chromium)
]

# Common browser paths on Linux
_LINUX_BROWSER_PATHS = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/snap/bin/chromium',
    '/usr/bin/microsoft-edge',
    '/usr/bin/brave-browser',
]

# Common browser paths on macOS
_MAC_BROWSER_PATHS = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
]

_cached_path = None


def get_chromium_executable() -> str | None:
    """
    Find a Chromium-based browser on the system.
    Returns the path to the executable, or None if not found.
    Result is cached after first call.
    """
    global _cached_path
    if _cached_path is not None:
        return _cached_path

    paths = []
    if sys.platform == 'win32':
        paths = _WIN_BROWSER_PATHS
    elif sys.platform == 'darwin':
        paths = _MAC_BROWSER_PATHS
    else:
        paths = _LINUX_BROWSER_PATHS

    for path in paths:
        if os.path.isfile(path):
            _cached_path = path
            logger.info(f"Found system browser: {path}")
            return path

    # Try 'which' / 'where' as fallback
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['where', 'chrome'], capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['which', 'google-chrome', 'chromium', 'chromium-browser'],
                                    capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            found = result.stdout.strip().split('\n')[0]
            _cached_path = found
            logger.info(f"Found browser via which/where: {found}")
            return found
    except Exception:
        pass

    logger.warning("No Chromium-based browser found on system")
    _cached_path = ''  # cache "not found"
    return None


def is_playwright_ready() -> bool:
    """Quick check if Playwright can launch a browser (no actual launch)."""
    try:
        import playwright  # noqa: F401
    except ImportError:
        return False
    return True


def launch_browser(headless=True, user_agent=None, locale='fa-IR'):
    """
    Context manager that launches a browser using the best available method.
    Uses system Chrome if Playwright's Chromium is not installed.

    Yields: (browser, context) tuple

    Usage:
        from core.crawlers.playwright_helper import launch_browser
        with launch_browser(headless=True, user_agent="...") as (browser, context):
            page = context.new_page()
            page.goto("https://...")
    """
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = None

    try:
        # Try launching Playwright's bundled Chromium first
        try:
            browser = pw.chromium.launch(headless=headless, timeout=15000)
            logger.info("Launched Playwright bundled Chromium")
        except Exception:
            logger.info("Playwright bundled Chromium not available, trying system browser...")
            browser = None

        # Fallback: use system Chrome/Edge
        if browser is None:
            exe = get_chromium_executable()
            if exe:
                try:
                    browser = pw.chromium.launch(
                        headless=headless,
                        executable_path=exe,
                        timeout=15000,
                    )
                    logger.info(f"Launched system browser: {exe}")
                except Exception as e:
                    logger.error(f"Failed to launch system browser: {e}")
                    browser = None

        if browser is None:
            pw.stop()
            return None, None

        # Create context
        context_kwargs = {'locale': locale}
        if user_agent:
            context_kwargs['user_agent'] = user_agent
        context = browser.new_context(**context_kwargs)

        yield browser, context

    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


class BrowserContext:
    """Reusable wrapper for Playwright browser operations."""

    def __init__(self, headless=True, user_agent=None, locale='fa-IR'):
        self.headless = headless
        self.user_agent = user_agent
        self.locale = locale
        self._pw = None
        self._browser = None
        self._context = None

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()

        # Try bundled Chromium first
        try:
            self._browser = self._pw.chromium.launch(
                headless=self.headless, timeout=15000
            )
            logger.info("Launched Playwright bundled Chromium")
        except Exception:
            logger.info("Bundled Chromium unavailable, trying system browser...")
            self._browser = None

        if self._browser is None:
            exe = get_chromium_executable()
            if exe:
                try:
                    self._browser = self._pw.chromium.launch(
                        headless=self.headless,
                        executable_path=exe,
                        timeout=15000,
                    )
                    logger.info(f"Launched system browser: {exe}")
                except Exception as e:
                    logger.error(f"System browser launch failed: {e}")
                    self._browser = None

        if self._browser is None:
            self.__exit__(None, None, None)
            return self  # caller should check .context

        ctx_kwargs = {'locale': self.locale}
        if self.user_agent:
            ctx_kwargs['user_agent'] = self.user_agent
        self._context = self._browser.new_context(**ctx_kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                self._pw.stop()
        except Exception:
            pass
        self._context = None
        self._browser = None
        self._pw = None

    @property
    def context(self):
        return self._context

    @property
    def is_available(self):
        return self._context is not None