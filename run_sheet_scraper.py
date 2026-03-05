import pandas as pd
from email_scraper import scrape_website

SHEET_URL = r"C:\Users\joell\email-scraper\Copy of Ballonvaart NL - Sheet1.csv"


print("Downloading sheet...")

df = pd.read_csv(SHEET_URL)

emails_found = []

for index, row in df.iterrows():

    website = row["Website"]

    print(f"\nScraping: {website}")

    try:

        emails = scrape_website(website)

        if emails:
            email = list(emails)[0]
        else:
            email = None

    except Exception as e:

        print("Error:", e)
        email = None

    emails_found.append(email)


df["Email"] = emails_found

df.to_csv("output.csv", index=False)

print("\nFinished. Saved to output.csv")