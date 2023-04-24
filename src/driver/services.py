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

BROWSER_OPTIONS = Options()
BROWSER_OPTIONS.binary_location = sa_settings.google_chrome_bin
BROWSER_OPTIONS.add_argument("--headless")
BROWSER_OPTIONS.add_argument("--no-sandbox")
BROWSER_OPTIONS.add_argument("--disable-dev-shm-usage")
BROWSER_OPTIONS.add_argument("--disable-gpu")
DRIVER_PATH = sa_settings.chromedriver_path
THYNKBROWSER: Optional[WebDriver] = None
wait = WebDriverWait(THYNKBROWSER, 1)


async def launch_browser():
    global THYNKBROWSER
    service = Service(executable_path=DRIVER_PATH)
    THYNKBROWSER = webdriver.Chrome(service=service, options=BROWSER_OPTIONS)


async def new_tab():
    global THYNKBROWSER
    if THYNKBROWSER:
        await asyncio.to_thread(THYNKBROWSER.execute_script, "window.open('about:blank', '_blank');")
        await asyncio.to_thread(THYNKBROWSER.switch_to.window, THYNKBROWSER.window_handles[-1])


async def close_browser():
    global THYNKBROWSER
    if THYNKBROWSER:
        await asyncio.to_thread(THYNKBROWSER.quit)
        THYNKBROWSER = None


async def close_tab():
    global THYNKBROWSER
    if THYNKBROWSER:
        await asyncio.to_thread(THYNKBROWSER.execute_script, "window.close();")
        await asyncio.to_thread(THYNKBROWSER.switch_to.window, THYNKBROWSER.window_handles[-1])


async def go_to_url(url: str):
    global THYNKBROWSER
    if THYNKBROWSER:
        await asyncio.to_thread(THYNKBROWSER.get, url)


async def login_to_selleramp():
    try:
        if not THYNKBROWSER:
            await launch_browser()
        await new_tab()
        if THYNKBROWSER.current_url != "https://sas.selleramp.com/site/login":
            await go_to_url("https://sas.selleramp.com/site/login")
        email = THYNKBROWSER.find_element(By.XPATH, "//*[@id='loginform-email']")
        email.send_keys(sa_settings.sas_email)
        password = THYNKBROWSER.find_element(By.XPATH, "//*[@id='loginform-password']")
        password.send_keys(sa_settings.sas_pass)
        login = THYNKBROWSER.find_element(By.XPATH, "//*[@id='login-form']/div[5]/button")
        login.click()
    except Exception as e:
        print(f"Error logging in to SellerAMP: {e}")
        raise HTTPException(status_code=500, detail="Error logging in to SellerAMP")


async def search_ean_on_selleramp(ean: str):
    try:
        if "https://sas.selleramp.com/" not in THYNKBROWSER.current_url:
            url = "https://sas.selleramp.com/"
            await go_to_url(url)
        search_field = THYNKBROWSER.find_element(By.XPATH, "//*[@id='saslookup-search_term']")
        search_field.clear()
        search_field.send_keys(ean)
        try:
            search_button = THYNKBROWSER.find_element(By.XPATH,
                                                 "/html/body/div[2]/div/div/div[2]/form/div/div/div/div/div/div[2]/button")
        except NoSuchElementException:
            try:
                search_button = THYNKBROWSER.find_element(By.XPATH,
                                                 "/html/body/div[2]/div/div/form/div[2]/div/div/div/div/div/div/div/div[2]/button")
            except NoSuchElementException:
                search_button = THYNKBROWSER.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/form/h1/div/div/div[1]/div[2]/button[1]")
        search_button.click()

        # Check if product loaded
        if "https://sas.selleramp.com/sas/lookup/" not in THYNKBROWSER.current_url:
            try:
                # Wait for the search results to load
                search_results = THYNKBROWSER.find_elements(By.XPATH, "//div[@id='search-results']/ul/li")
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
        ean = THYNKBROWSER.find_element(By.XPATH, "//*[@id='pdb-ean-input']").text
        price = THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi_sale_price']").text
        # Enter the price in the cost field
        cost = THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi_cost']")
        cost.clear()
        cost.send_keys(cost_input)
        product = THYNKBROWSER.find_element(By.XPATH, "//div[@class='pdb-title product-title']")
        asin = THYNKBROWSER.find_element(By.XPATH, "//*[@id='pdb-asin-input']")
        alerts = THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi-alerts']/ul")
        bsr = THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi-bsr']")
        est = THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi-estimated-sales']/span")
        profit = float(THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi-profit']")
                       .text.replace('£', ''))
        roi = THYNKBROWSER.find_element(By.XPATH, "//*[@id='qi-roi']")
        reviewCount = THYNKBROWSER.find_element(By.XPATH, "//*[@id='product-details-box']/div[3]/div[2]/span[2]")
        # Find the rating element and its children (the stars)
        rating_element = THYNKBROWSER.find_element(By.XPATH, "//*[@id='product-details-box']/div[3]/div[2]/span[1]")
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
        fbaSellers = THYNKBROWSER.find_element(By.XPATH, "//*[@id='keepa_csv_type_10']")
        fbmSellers = THYNKBROWSER.find_element(By.XPATH, "//*[@id='keepa_csv_type_7']")
        amazon = THYNKBROWSER.find_element(By.XPATH, "//*[@id='keepa_csv_type_0']")
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
