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
            self.logger.debug(f"Navigating to login page with timeout: {self.settings.scraping.timeout * 1000}ms")
            await page.goto("https://www.linkedin.com/login", timeout=self.settings.scraping.timeout * 1000)
            self.logger.debug("Waiting for networkidle...")
            await page.wait_for_load_state("networkidle")
            self.logger.debug("Login page loaded")
            
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
            # Log what we're trying to enter (partially masked for security)
            masked_email = self.credentials.email[:3] + "***" + self.credentials.email[-3:] if len(self.credentials.email) > 6 else "***"
            self.logger.debug(f"Attempting to enter email: {masked_email}")
            
            if not self.credentials.email:
                raise AuthenticationError("Email is empty - credentials not loaded")
            
            # Take a screenshot for debugging if enabled
            if self.settings.debug:
                try:
                    await page.screenshot(path="login_form.png")
                    self.logger.debug("Screenshot saved to login_form.png")
                except Exception as e:
                    self.logger.debug(f"Could not take screenshot: {e}")
            
            # Try multiple selectors for email field (LinkedIn may use different ones)
            email_selectors = ["#username", "input[name='session_key']", "input[id='username']"]
            
            email_entered = False
            for selector in email_selectors:
                try:
                    self.logger.debug(f"Trying email selector: {selector}")
                    element = await page.wait_for_selector(selector, timeout=15000, state="visible")
                    if element:
                        # Click to focus
                        await element.click()
                        await asyncio.sleep(0.2)
                        
                        # Type email character by character (more reliable than fill())
                        await element.type(self.credentials.email, delay=50)
                        self.logger.info(f"✅ Email entered using selector: {selector}")
                        email_entered = True
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not email_entered:
                # Log page HTML for debugging
                page_content = await page.content()
                self.logger.debug(f"Page HTML sample: {page_content[:500]}")
                raise AuthenticationError("Could not find email input field with any selector")
            
            # Try multiple selectors for password field
            password_selectors = ["#password", "input[name='session_password']", "input[id='password']"]
            
            password_entered = False
            for selector in password_selectors:
                try:
                    self.logger.debug(f"Trying password selector: {selector}")
                    element = await page.wait_for_selector(selector, timeout=15000, state="visible")
                    if element:
                        # Click to focus
                        await element.click()
                        await asyncio.sleep(0.2)
                        
                        # Type password character by character
                        await element.type(self.credentials.password, delay=50)
                        self.logger.info(f"✅ Password entered using selector: {selector}")
                        password_entered = True
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not password_entered:
                raise AuthenticationError("Could not find password input field")
            
            # Wait a bit before clicking submit
            await asyncio.sleep(1)
            
            # Try multiple selectors for login button
            login_selectors = [
                "[type='submit']",
                "button[data-litms-control-urn='login-submit']",
                "button.sign-in-form__submit-button",
                "button[aria-label='Sign in']",
                "button.sign-in-form__submit-btn",
                "input[type='submit']"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    self.logger.debug(f"Trying login button selector: {selector}")
                    element = await page.wait_for_selector(selector, timeout=15000, state="visible")
                    if element:
                        await element.click()
                        self.logger.info(f"✅ Login button clicked using selector: {selector}")
                        login_clicked = True
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
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
        """Check if 2FA verification or challenge is required."""
        try:
            await asyncio.sleep(3)  # Wait for potential redirect or challenge
            
            current_url = page.url
            self.logger.debug(f"Checking for 2FA. Current URL: {current_url}")
            
            # Check URL for challenge indicators
            if "challenge" in current_url or "verify" in current_url:
                self.logger.info("Challenge detected in URL")
                return True
            
            # Check for device recognition checkbox (trust this device)
            device_checkbox = await page.query_selector("input[name='recognizedDevice'][type='checkbox']")
            if device_checkbox:
                self.logger.info("Device recognition challenge detected")
                return True
            
            # Look for 2FA code input elements
            pin_input = await page.query_selector("input[name='pin'], input[id='input__phone_verification_pin']")
            if pin_input:
                self.logger.info("2FA code input detected")
                return True
            
            # Check for generic challenge indicators
            challenge_indicators = [
                "[data-validation-id='challenge-form']",
                "span:has-text('Enter code')",
                "div:has-text('verification code')"
            ]
            
            for selector in challenge_indicators:
                element = await page.query_selector(selector)
                if element:
                    self.logger.info("Challenge prompt detected")
                    return True
            
            self.logger.debug("No challenge detected")
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking 2FA: {e}")
            return False
    
    async def _handle_2fa(self, page: Page) -> None:
        """Handle 2FA verification or device recognition."""
        try:
            # Take screenshot for debugging
            if self.settings.debug:
                await page.screenshot(path="challenge_page.png")
                self.logger.debug("Screenshot saved to challenge_page.png")
            
            # Log the current URL and page title
            current_url = page.url
            page_title = await page.title()
            self.logger.info(f"Handling challenge on: {current_url}")
            self.logger.info(f"Page title: {page_title}")
            
            # Wait for the page to fully load
            await asyncio.sleep(2)
            
            # Try clicking "try-another-way" link if present (switch to TOTP verification)
            try_another_way = await page.query_selector("#try-another-way")
            if try_another_way:
                self.logger.info("Clicking 'try-another-way' to switch to TOTP verification")
                await try_another_way.click()
                await asyncio.sleep(2)
            
            # Check if this is a device recognition challenge (checkbox)
            device_checkbox = await page.query_selector("input[name='recognizedDevice'][type='checkbox']")
            if device_checkbox:
                is_checked = await device_checkbox.is_checked()
                if not is_checked:
                    self.logger.info("Clicking 'recognizedDevice' checkbox to trust this device")
                    # Try clicking the label first (as per Selenium recording)
                    device_label = await page.query_selector(".recognized__device .form__label")
                    if device_label:
                        await device_label.click()
                    else:
                        await device_checkbox.click()
                    await asyncio.sleep(1)
                else:
                    self.logger.info("Device already recognized")
                
                # Find and click continue/submit button
                submit_buttons = [
                    "#two-step-submit-button",
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:has-text('Continue')",
                    "button:has-text('Verify')",
                    "[data-test-id='challenge-form-submit-btn']"
                ]
                
                for selector in submit_buttons:
                    try:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            await element.click()
                            self.logger.info(f"✅ Clicked submit button: {selector}")
                            await asyncio.sleep(2)
                            return
                    except Exception as e:
                        self.logger.debug(f"Could not click {selector}: {e}")
                        continue
                
                raise TwoFactorAuthError("Could not find submit button after checking device")
            
            # This is a 2FA code challenge - generate and enter TOTP code
            if not self.credentials.totp_secret:
                raise TwoFactorAuthError("No TOTP secret provided")
            
            totp = pyotp.TOTP(self.credentials.totp_secret)
            code = totp.now()
            self.logger.info(f"Generated TOTP code: {code}")
            
            # Try clicking the recognized device checkbox label if present (from Selenium recording)
            device_label = await page.query_selector(".recognized__device .form__label")
            if device_label:
                self.logger.info("Clicking recognized device checkbox label")
                await device_label.click()
                await asyncio.sleep(0.5)
            
            # Try multiple selectors for the 2FA input field
            pin_selectors = [
                "#input__phone_verification_pin",
                "input[name='pin']",
                "input[id='pin']",
                "input[placeholder*='verification']",
                "input[placeholder*='verification code']",
                "input[placeholder*='code']",
                "input[placeholder*='PIN']",
                "input[type='text']",
                "input[aria-label*='verification']",
                "input[aria-label*='code']",
                "#verificationCode",
                "#verification_code"
            ]
            
            code_entered = False
            for selector in pin_selectors:
                try:
                    self.logger.debug(f"Trying TOTP input selector: {selector}")
                    element = await page.query_selector(selector)
                    if element:
                        # Check if element is visible
                        is_visible = await element.is_visible()
                        if not is_visible:
                            self.logger.debug(f"Element {selector} found but not visible")
                            continue
                        
                        # Click to focus
                        await element.click()
                        await asyncio.sleep(0.3)
                        
                        # Type the code
                        await element.type(code, delay=100)
                        self.logger.info(f"✅ TOTP code entered using selector: {selector}")
                        code_entered = True
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not code_entered:
                # Log page content for debugging
                try:
                    page_content = await page.content()
                    self.logger.debug(f"Page HTML sample: {page_content[:1000]}")
                except Exception:
                    pass
                
                # Get all visible input fields
                all_inputs = await page.query_selector_all("input")
                self.logger.warning(f"Found {len(all_inputs)} input fields on page")
                for i, inp in enumerate(all_inputs[:20]):  # Limit to first 20
                    try:
                        inp_type = await inp.get_attribute("type")
                        inp_name = await inp.get_attribute("name")
                        inp_id = await inp.get_attribute("id")
                        inp_placeholder = await inp.get_attribute("placeholder")
                        inp_aria_label = await inp.get_attribute("aria-label")
                        inp_class = await inp.get_attribute("class")
                        self.logger.warning(f"Input {i}: type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder}, aria-label={inp_aria_label}, class={inp_class}")
                    except Exception as e:
                        self.logger.debug(f"Could not get input {i} attributes: {e}")
                
                raise TwoFactorAuthError("Could not find 2FA input field with any selector")
            
            # Wait a bit before submitting
            await asyncio.sleep(1)
            
            # Submit the form
            submit_selectors = [
                "#two-step-submit-button",
                "button[type='submit']",
                "[data-test-id='challenge-form-submit-btn']",
                ".challenge-form button[type='submit']",
                "button.sign-in-form__submit-button",
                "input[type='submit']",
                "button:has-text('Verify')",
                "button:has-text('Continue')",
                "button:has-text('Submit')"
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    self.logger.debug(f"Trying submit button selector: {selector}")
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if not is_visible:
                            continue
                        
                        await element.click()
                        self.logger.info(f"✅ Submit button clicked using selector: {selector}")
                        submit_clicked = True
                        break
                except Exception as e:
                    self.logger.debug(f"Submit selector {selector} failed: {e}")
                    continue
            
            if not submit_clicked:
                self.logger.warning("Could not find submit button, but code was entered")
            
            # Wait for verification
            self.logger.debug("Waiting for 2FA verification to complete...")
            await page.wait_for_load_state("networkidle", timeout=self.settings.scraping.timeout * 1000)
            
            self.logger.info("✅ 2FA code submitted and verification completed")
            
        except Exception as e:
            self.logger.error(f"2FA verification failed: {e}")
            raise TwoFactorAuthError(f"2FA verification failed: {e}")
    
    async def _verify_login_success(self, page: Page) -> bool:
        """Verify that login was successful."""
        try:
            # Wait longer for redirects and page loads
            self.logger.debug("Waiting for login to complete...")
            await asyncio.sleep(5)  # Increased wait time
            
            # Try waiting for network to be idle
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                self.logger.debug("Page did not reach networkidle")
            
            # Check current URL and log it for debugging
            current_url = page.url
            self.logger.info(f"Current URL after login attempt: {current_url}")
            
            # Check for specific error messages
            error_selectors = [
                "div[role='alert']",
                ".alert",
                ".alert--error",
                "[data-error]",
                ".error-for-password",
                "#error-for-password"
            ]
            
            for selector in error_selectors:
                element = await page.query_selector(selector)
                if element:
                    error_text = await element.text_content()
                    if error_text and error_text.strip():
                        self.logger.warning(f"Error message found: {error_text}")
            
            # Check if we need to handle a challenge
            if "login" in current_url:
                # Check if there's a challenge form visible
                challenge_check = await self._is_2fa_required(page)
                if challenge_check:
                    self.logger.info("Challenge detected, returning True to let 2FA handler deal with it")
                    return True  # Let the 2FA handler deal with it
                else:
                    self.logger.warning(f"Still on login page after 5 seconds: {current_url}")
                    return False
            
            if "challenge" in current_url or "verify" in current_url:
                self.logger.info(f"On challenge page: {current_url}")
                # This is actually OK, it means we need 2FA
                return True
            
            # Look for elements that indicate successful login
            success_indicators = [
                "nav.global-nav",
                ".global-nav__me",
                "[data-test-id='nav-top-profile']",
                ".global-nav__primary-link--me"
            ]
            
            for selector in success_indicators:
                try:
                    await page.wait_for_selector(selector, timeout=10000)
                    self.logger.info(f"✅ Login verified successfully with selector: {selector}")
                    return True
                except Exception:
                    continue
            
            # If we're on feed or profile page, consider it success
            if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
                self.logger.info(f"✅ On feed/profile page, login successful")
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