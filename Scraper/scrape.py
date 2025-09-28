from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from models.jobs import Job
from db import db


def scrape_actuary_jobs():
    """
    Scrape jobs from actuarylist.com and save them into the database.
    """

    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.actuarylist.com/")

        wait = WebDriverWait(driver, 10)

        print("Waiting for page to load...")
        section = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.Job_grid-section__kgIsR"))
        )
        print("Section found!")

        # Allow dynamic content to load
        time.sleep(2)

        # Find job cards using partial class matching for better reliability
        cards = driver.find_elements(By.CSS_SELECTOR, "[class*='Job_job-card'][class*='YgDAV']")
        if len(cards) == 0:
            print("Trying alternative selectors...")
            cards = driver.find_elements(By.CSS_SELECTOR, "[class*='Job_job-card']")
            print(f"Found {len(cards)} cards with alternative selector")

        print(f"Found {len(cards)} job cards to process")

        for i, card in enumerate(cards):
            try:
                # Title - using partial class matching
                title = None
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, "[class*='Job_job-card__position']")
                    title = title_elem.text.strip()
                except NoSuchElementException:
                    print(f"  No title found for card {i + 1}")

                # Company - using partial class matching
                company = None
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "[class*='Job_job-card__company']")
                    company = company_elem.text.strip()
                except NoSuchElementException:
                    print(f"  No company found for card {i + 1}")

                # Location - try multiple selectors
                location = None
                try:
                    # Try location links first
                    location_elements = card.find_elements(By.CSS_SELECTOR, "[class*='Job_job-card__location'] a")
                    if location_elements:
                        locations = [loc.text.strip() for loc in location_elements if loc.text.strip()]
                        location = ", ".join(locations) if locations else None

                    # If no links, try direct location text
                    if not location:
                        location_elem = card.find_element(By.CSS_SELECTOR, "[class*='Job_job-card__location']")
                        location = location_elem.text.strip() if location_elem.text.strip() else None

                except NoSuchElementException:
                    print(f"  No location found for card {i + 1}")

                # Tags - using partial class matching
                tags = None
                try:
                    tags_elements = card.find_elements(By.CSS_SELECTOR, "[class*='Job_job-card__tags'] a")
                    if tags_elements:
                        tag_list = [tag.text.strip() for tag in tags_elements if tag.text.strip()]
                        tags = ", ".join(tag_list) if tag_list else None
                except NoSuchElementException:
                    print(f"  No tags found for card {i + 1}")

                # Skip if essential fields are missing
                if not title or not company:
                    print(f"⚠️ Skipping card {i + 1}: Missing essential data (title: {title}, company: {company})")
                    continue

                # Build Job object with proper values
                new_job = Job(
                    title=title.strip() if title else "Unknown Position",
                    company=company.strip() if company else "Unknown Company",
                    location=location.strip() if location else "Remote/Not Specified",
                    posting_date=None,  # Set to None to avoid datetime parsing issues
                    job_type="Full-time",  # Default value since it's required
                    tags=tags if tags else "Actuary"  # Default tag if none found
                )

                # Check for duplicates before adding (optional)
                existing_job = Job.query.filter_by(
                    title=new_job.title,
                    company=new_job.company,
                    location=new_job.location
                ).first()

                if existing_job:
                    print(f"📝 Job {i + 1} already exists: {title} at {company}")
                    continue

                db.session.add(new_job)
                db.session.commit()
                print(f"✅ Saved job {i + 1}: {title} at {company}")

            except Exception as e:
                print(f" Error processing card {i + 1}: {e}")
                # Rollback the session to prevent transaction issues
                db.session.rollback()
                continue

        print(f"\n Scraping completed! Processed {len(cards)} job cards")

    except TimeoutException:
        print("⏳ Timeout: Page took too long to load")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()  # Rollback any pending transaction
    finally:
        driver.quit()
        print("Browser closed")