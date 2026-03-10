import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from email_scraper import scrape_website

SHEET_URL = r"C:\Users\joell\email-scraper\Copy of Ballonvaart NL - Sheet1.csv"
MAX_WORKERS = 10

print("Downloading sheet...")

df = pd.read_csv(SHEET_URL)


def scrape_row(index, website):
    print(f"\nScraping: {website}")
    try:
        emails = scrape_website(website)
        return index, list(emails)[0] if emails else None
    except Exception as e:
        print(f"Error scraping {website}: {e}")
        return index, None


emails_found = [None] * len(df)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(scrape_row, idx, row["Website"]): idx
        for idx, row in df.iterrows()
    }

    for future in as_completed(futures):
        index, email = future.result()
        emails_found[index] = email

df["Email"] = emails_found

df.to_csv("output.csv", index=False)

print("\nFinished. Saved to output.csv")
