import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def handle_privacy_notice(driver, max_wait=10):
    """
    Handle the privacy notice popup by finding and clicking the close button
    Returns True if successfully closed, False otherwise
    """
    try:
        # Wait for privacy notice to appear and become clickable
        wait = WebDriverWait(driver, max_wait)
        close_button = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-close-btn-container"))
        )
        
        # Try different click methods
        try:
            close_button.click()
        except:
            try:
                ActionChains(driver).move_to_element(close_button).click().perform()
            except:
                driver.execute_script("arguments[0].click();", close_button)
        
        # Wait for popup to disappear
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error handling privacy notice: {e}")
        return False

def fetch_and_save_html(url, output_file="bestbuy_reviews.html", max_attempts=20):
    """
    Use Selenium to load the page, handle privacy notice, click 'Show More', and save the final HTML
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Enable headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    action = ActionChains(driver)
    
    try:
        print(f"Opening URL: {url}")
        driver.get(url)
        time.sleep(3)  # Initial load wait
        
        # Handle privacy notice
        if not handle_privacy_notice(driver):
            print("Warning: Could not handle privacy notice")
        
        attempts = 0
        while attempts < max_attempts:
            try:
                # Wait for Show More button to be present and visible
                wait = WebDriverWait(driver, 10)
                show_more = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[data-automation='load-more-button'] a.loadMoreLink_2cY6X")
                    )
                )
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more)
                time.sleep(1)
                
                # Click using different methods until one works
                try:
                    show_more.click()
                except:
                    try:
                        action.move_to_element(show_more).click().perform()
                    except:
                        driver.execute_script("arguments[0].click();", show_more)
                
                print(f"Clicked Show More button (attempt {attempts + 1})")
                time.sleep(2)  # Wait for new content to load
                attempts += 1
                
            except NoSuchElementException:
                print("No more Show More button found")
                break
            except Exception as e:
                print(f"Error clicking button: {e}")
                break
        
        # Wait longer before saving HTML to ensure all content is loaded
        print("Waiting for final content to load completely...")
        time.sleep(10)
        
        # Save the final HTML
        print("Saving final HTML...")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        
        print(f"HTML saved to {output_file}")
        
    finally:
        driver.quit()

def main():
    url = "https://www.bestbuy.ca/en-ca/product/google-pixel-9-pro-256gb-hazel-unlocked/18165489/review"
    
    try:
        fetch_and_save_html(url)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()