"""Authentication handler for LinkedIn."""

import asyncio
import pyotp
from typing import Optional
from playwright.async_api import Page

from ..config.settings import LinkedInCredentials, Settings
from ..utils.exceptions import AuthenticationError, TwoFactorAuthError
from ..utils.logging import get_logger


logger = get_logger(__name__)


class AuthenticationHandler:
    """Handles LinkedIn authentication including 2FA."""
    
    def __init__(self, credentials: LinkedInCredentials, settings: Settings):
        self.credentials = credentials
        self.settings = settings
        self.logger = logger.bind(component="authentication")
    
    async def authenticate(self, page: Page) -> bool:
        """
        Authenticate with LinkedIn.
        
        Args:
            page: Playwright page instance
            
        Returns:
            True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
            TwoFactorAuthError: If 2FA fails
        """
        try:
            self.logger.info("Starting LinkedIn authentication")
            
            # Navigate to LinkedIn login
            await page.goto("https://www.linkedin.com/login", timeout=self.settings.scraping.timeout * 1000)
            await page.wait_for_load_state("networkidle")
            
            # Check if already logged in
            if await self._is_already_logged_in(page):
                self.logger.info("Already logged in to LinkedIn")
                return True
            
            # Enter credentials
            await self._enter_credentials(page)
            
            # Handle 2FA if required
            if await self._is_2fa_required(page):
                if not self.credentials.totp_secret:
                    raise TwoFactorAuthError("2FA required but no TOTP secret provided")
                await self._handle_2fa(page)
            
            # Verify successful login
            if not await self._verify_login_success(page):
                raise AuthenticationError("Login verification failed")
            
            self.logger.info("LinkedIn authentication successful")
            return True
            
        except Exception as e:
            self.logger.error("Authentication failed", error=str(e))
            if isinstance(e, (AuthenticationError, TwoFactorAuthError)):
                raise
            raise AuthenticationError(f"Unexpected authentication error: {e}")
    
    async def _is_already_logged_in(self, page: Page) -> bool:
        """Check if already logged in to LinkedIn."""
        try:
            # Look for elements that indicate logged-in state
            selectors = [
                "nav.global-nav",
                ".global-nav__me",
                "[data-test-id='nav-top-profile']"
            ]
            
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    return True
            
            return False
        except Exception:
            return False
    
    async def _enter_credentials(self, page: Page) -> None:
        """Enter email and password."""
        try:
            # Try multiple selectors for email field (LinkedIn may use different ones)
            email_selectors = ["#username", "input[name='session_key']", "[type='text']"]
            
            email_entered = False
            for selector in email_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000, state="visible")
                    if element:
                        await element.fill("")  # Clear field first
                        await element.fill(self.credentials.email)
                        self.logger.debug(f"Email entered using selector: {selector}")
                        email_entered = True
                        break
                except Exception:
                    continue
            
            if not email_entered:
                raise AuthenticationError("Could not find email input field")
            
            # Try multiple selectors for password field
            password_selectors = ["#password", "input[name='session_password']", "[type='password']"]
            
            password_entered = False
            for selector in password_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000, state="visible")
                    if element:
                        await element.fill("")  # Clear field first
                        await element.fill(self.credentials.password)
                        self.logger.debug(f"Password entered using selector: {selector}")
                        password_entered = True
                        break
                except Exception:
                    continue
            
            if not password_entered:
                raise AuthenticationError("Could not find password input field")
            
            # Wait a bit before clicking submit
            await asyncio.sleep(0.5)
            
            # Try multiple selectors for login button
            login_selectors = [
                "[type='submit']",
                "button[data-litms-control-urn='login-submit']",
                "button.sign-in-form__submit-button",
                "button[aria-label='Sign in']"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000, state="visible")
                    if element:
                        await element.click()
                        self.logger.debug(f"Login button clicked using selector: {selector}")
                        login_clicked = True
                        break
                except Exception:
                    continue
            
            if not login_clicked:
                raise AuthenticationError("Could not find login submit button")
            
            # Wait for navigation or error
            await page.wait_for_load_state("networkidle", timeout=self.settings.scraping.timeout * 1000)
            
            self.logger.debug("Credentials entered successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to enter credentials: {e}")
            raise AuthenticationError(f"Failed to enter credentials: {e}")
    
    async def _is_2fa_required(self, page: Page) -> bool:
        """Check if 2FA verification is required."""
        try:
            await asyncio.sleep(2)  # Wait for potential redirect
            
            # Look for 2FA challenge elements
            selectors = [
                "input[name='pin']",
                "[data-test-id='challenge-form']",
                ".challenge-form",
                "input[placeholder*='verification']"
            ]
            
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    self.logger.debug("2FA challenge detected")
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _handle_2fa(self, page: Page) -> None:
        """Handle 2FA verification."""
        try:
            # Generate TOTP code
            totp = pyotp.TOTP(self.credentials.totp_secret)
            code = totp.now()
            
            self.logger.debug("Generated 2FA code")
            
            # Enter the code
            pin_selectors = [
                "input[name='pin']",
                "input[id='input__phone_verification_pin']",
                "input[placeholder*='verification']"
            ]
            
            code_entered = False
            for selector in pin_selectors:
                element = await page.query_selector(selector)
                if element:
                    await page.fill(selector, code)
                    code_entered = True
                    break
            
            if not code_entered:
                raise TwoFactorAuthError("Could not find 2FA input field")
            
            # Submit the form
            submit_selectors = [
                "[type='submit']",
                "button[data-test-id='challenge-form-submit-btn']",
                ".challenge-form button"
            ]
            
            for selector in submit_selectors:
                element = await page.query_selector(selector)
                if element:
                    await page.click(selector)
                    break
            
            # Wait for verification
            await page.wait_for_load_state("networkidle", timeout=self.settings.scraping.timeout * 1000)
            
            self.logger.debug("2FA code submitted")
            
        except Exception as e:
            raise TwoFactorAuthError(f"2FA verification failed: {e}")
    
    async def _verify_login_success(self, page: Page) -> bool:
        """Verify that login was successful."""
        try:
            # Wait a moment for any redirects
            await asyncio.sleep(3)
            
            # Check current URL and log it for debugging
            current_url = page.url
            self.logger.debug(f"Current URL after login attempt: {current_url}")
            
            # Check for specific error messages
            error_selectors = [
                "div[role='alert']",
                ".alert",
                ".alert--error",
                "[data-error]"
            ]
            
            for selector in error_selectors:
                element = await page.query_selector(selector)
                if element:
                    error_text = await element.text_content()
                    if error_text:
                        self.logger.warning(f"Error message found: {error_text}")
            
            if "login" in current_url or "challenge" in current_url:
                self.logger.debug(f"Still on login/challenge page: {current_url}")
                # Try to get page content to see what's happening
                try:
                    body_text = await page.text_content("body")
                    if body_text:
                        self.logger.debug(f"Page content preview: {body_text[:200]}")
                except Exception:
                    pass
                return False
            
            # Look for elements that indicate successful login
            success_indicators = [
                "nav.global-nav",
                ".global-nav__me",
                "[data-test-id='nav-top-profile']",
                ".global-nav__primary-link--me"
            ]
            
            for selector in success_indicators:
                try:
                    await page.wait_for_selector(selector, timeout=self.settings.scraping.timeout * 1000)
                    self.logger.debug(f"Found success indicator: {selector}")
                    return True
                except Exception:
                    continue
            
            # If we're on feed or profile page, consider it success
            if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
                self.logger.debug(f"On feed/profile page, considering login successful")
                return True
            
            self.logger.warning(f"Could not verify login success. URL: {current_url}")
            return False
            
        except Exception as e:
            self.logger.error("Login verification error", error=str(e))
            return False
    
    async def logout(self, page: Page) -> None:
        """Logout from LinkedIn."""
        try:
            # Navigate to logout URL
            await page.goto("https://www.linkedin.com/m/logout/", timeout=self.settings.scraping.timeout * 1000)
            await page.wait_for_load_state("networkidle")
            
            self.logger.info("Logged out from LinkedIn")
            
        except Exception as e:
            self.logger.warning("Logout failed", error=str(e))
            # Don't raise exception for logout failures