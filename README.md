# Email Scraper Tool 📧

A Python-based tool that scrapes websites to collect email addresses. Given a starting URL, this tool will recursively follow links found on the page and extract email addresses from all visited pages.

Built with:
<br>
<br>
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
<br>
<br>

## Features ✨
- **Recursive scraping**: Follows links on the web pages to visit multiple pages for a thorough search.
- **Email extraction**: Uses regular expressions to find and collect email addresses.
- **Easy to use**: Just enter a URL, and the tool will start scraping.

## Requirements 🛠️
- `python 3.x`
- `requests` – For making HTTP requests.
- `beautifulsoup4` – For parsing and navigating HTML.
- `lxml` – An XML/HTML parser for BeautifulSoup.

## Installation Guide 📝

### 1. Clone the repository:
```bash
git clone https://github.com/AdrianTomin/email-scraper.git
cd email-scraper
```

### 2. Set up a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  
```
> On Windows: venv\Scripts\activate

### 3. Install dependencies:
The required libraries are listed in requirements.txt. You can install them using pip:
```bash
pip install -r requirements.txt
```
If you don't have the requirements.txt file yet, you can generate it as follows:
```bash
pip freeze > requirements.txt
```

### 4. Run the tool:
After installing the dependencies, you can run the tool by executing the following command:

```bash
python email_scraper.py
```

## Example Output 🖥️
```
[+] Enter url to scan: https://example.com
[1] Processing https://example.com
[2] Processing https://example.com/contact
Found emails:
info@example.com
support@example.com
```

## Badges
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Authors
- [@AdrianTomin](https://www.github.com/AdrianTomin)
