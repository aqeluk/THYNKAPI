import asyncio
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from fastapi import HTTPException
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from src.driver.config import sa_settings

BROWSER_OPTIONS = webdriver.ChromeOptions()
BROWSER_OPTIONS.binary_location = sa_settings.google_chrome_bin
BROWSER_OPTIONS.add_argument("--headless")
BROWSER_OPTIONS.add_argument("--disable-dev-shm-usage")
BROWSER_OPTIONS.add_argument("--no-sandbox")
DRIVER_PATH = sa_settings.chromedriver_path
BROWSER: Optional[WebDriver] = None
wait = WebDriverWait(BROWSER, 1)


async def launch_browser():
    global BROWSER
    service = Service(executable_path=DRIVER_PATH)
    BROWSER = webdriver.Chrome(service=service, options=BROWSER_OPTIONS)


async def new_tab():
    global BROWSER
    if BROWSER:
        await asyncio.to_thread(BROWSER.execute_script, "window.open('about:blank', '_blank');")
        await asyncio.to_thread(BROWSER.switch_to.window, BROWSER.window_handles[-1])


async def close_browser():
    global BROWSER
    if BROWSER:
        await asyncio.to_thread(BROWSER.quit)
        BROWSER = None


async def close_tab():
    global BROWSER
    if BROWSER:
        await asyncio.to_thread(BROWSER.execute_script, "window.close();")
        await asyncio.to_thread(BROWSER.switch_to.window, BROWSER.window_handles[-1])


async def go_to_url(url: str):
    global BROWSER
    if BROWSER:
        await asyncio.to_thread(BROWSER.get, url)


async def login_to_selleramp():
    try:
        # Create a new tab
        await new_tab()
        # Check if already on the login page
        if BROWSER.current_url != "https://sas.selleramp.com/site/login":
            # Navigate to the login page
            await go_to_url("https://sas.selleramp.com/site/login")
        # Find the email field and enter the email
        email = BROWSER.find_element(By.XPATH, "//*[@id='loginform-email']")
        email.send_keys(sa_settings.sas_email)
        # Find the password field and enter the password
        password = BROWSER.find_element(By.XPATH, "//*[@id='loginform-password']")
        password.send_keys(sa_settings.sas_pass)
        # Click the login button
        login = BROWSER.find_element(By.XPATH, "//*[@id='login-form']/div[5]/button")
        login.click()
    except Exception as e:
        print(f"Error logging in to SellerAMP: {e}")
        raise HTTPException(status_code=500, detail="Error logging in to SellerAMP")


async def search_ean_on_selleramp(ean: str):
    try:
        # Check if the current URL matches the selleramp search URL
        if "https://sas.selleramp.com/" not in BROWSER.current_url:
            # Navigate to the login page
            url = "https://sas.selleramp.com/"
            await go_to_url(url)
        # Find the search field and enter the EAN
        search_field = BROWSER.find_element(By.XPATH, "//*[@id='saslookup-search_term']")
        search_field.clear()
        search_field.send_keys(ean)
        # Click the search button
        try:
            search_button = BROWSER.find_element(By.XPATH,
                                                 "/html/body/div[2]/div/div/div[2]/form/div/div/div/div/div/div[2]/button")
        except NoSuchElementException:
            try:
                search_button = BROWSER.find_element(By.XPATH,
                                                 "/html/body/div[2]/div/div/form/div[2]/div/div/div/div/div/div/div/div[2]/button")
            except NoSuchElementException:
                search_button = BROWSER.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/form/h1/div/div/div[1]/div[2]/button[1]")
        search_button.click()

        # Check if product loaded
        if "https://sas.selleramp.com/sas/lookup/" not in BROWSER.current_url:
            try:
                # Wait for the search results to load
                search_results = BROWSER.find_elements(By.XPATH, "//div[@id='search-results']/ul/li")
                print(search_results)
                if len(search_results) > 0:
                    # Click on the first product in the search results
                    product = search_results[0].find_element(By.XPATH, ".//a")
                    product.click()
            except (NoSuchElementException, TimeoutException) as e:
                raise HTTPException(status_code=500, detail=f"Error while searching for EAN {ean}")
    except Exception as e:
        print(f"Error searching for EAN {ean} on SellerAMP: {e}")
        raise HTTPException(status_code=500, detail=f"No result or exception for EAN {ean} on SellerAMP")


async def scrape_product_data(cost_input: float):
    try:
        scraped_data = []
        ean = BROWSER.find_element(By.XPATH, "//*[@id='pdb-ean-input']").text
        price = BROWSER.find_element(By.XPATH, "//*[@id='qi_sale_price']").text
        # Enter the price in the cost field
        cost = BROWSER.find_element(By.XPATH, "//*[@id='qi_cost']")
        cost.clear()
        cost.send_keys(cost_input)
        product = BROWSER.find_element(By.XPATH, "//div[@class='pdb-title product-title']")
        asin = BROWSER.find_element(By.XPATH, "//*[@id='pdb-asin-input']")
        alerts = BROWSER.find_element(By.XPATH, "//*[@id='qi-alerts']/ul")
        bsr = BROWSER.find_element(By.XPATH, "//*[@id='qi-bsr']")
        est = BROWSER.find_element(By.XPATH, "//*[@id='qi-estimated-sales']/span")
        profit = float(BROWSER.find_element(By.XPATH, "//*[@id='qi-profit']")
                       .text.replace('£', ''))
        roi = BROWSER.find_element(By.XPATH, "//*[@id='qi-roi']")
        reviewCount = BROWSER.find_element(By.XPATH, "//*[@id='product-details-box']/div[3]/div[2]/span[2]")
        # Find the rating element and its children (the stars)
        rating_element = BROWSER.find_element(By.XPATH, "//*[@id='product-details-box']/div[3]/div[2]/span[1]")
        stars = rating_element.find_elements(By.TAG_NAME, "i")
        # Initialize a variable to store the rating
        reviews = 0
        # Iterate through the stars and add their values to the rating
        for star in stars:
            classes = star.get_attribute("class")
            if "fa-star-half-empty" in classes:
                reviews += 0.5
            elif "fa-star-o" in classes:
                reviews += 0
            else:
                reviews += 1
        fbaSellers = BROWSER.find_element(By.XPATH, "//*[@id='keepa_csv_type_10']")
        fbmSellers = BROWSER.find_element(By.XPATH, "//*[@id='keepa_csv_type_7']")
        amazon = BROWSER.find_element(By.XPATH, "//*[@id='keepa_csv_type_0']")
        scraped_data.append({
            'asin': asin,
            'ean': ean,
            'price': price,
            'product': product.text,
            'reviews': reviews,
            'reviewCount': reviewCount.text,
            'alerts': alerts.text,
            'est': est.text,
            'bsr': bsr.text,
            'profit': profit,
            'roi': roi.text.replace('%', ''),
            'fbaSellers': fbaSellers.text,
            'fbmSellers': fbmSellers.text,
            'amazon': amazon.text
        })
        return scraped_data
    except NoSuchElementException as e:
        print(e)
    except Exception as e:
        print(e)
