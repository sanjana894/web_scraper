import scrapy
import re
from datetime import datetime

class BankrateLoanSpider(scrapy.Spider):
    name = "bankrate_loans"
    allowed_domains = ["bankrate.com"]
    start_urls = ['https://www.bankrate.com/mortgages/mortgage-rates/']

    def parse(self, response):
        # Extract and format update date
        raw_date = response.css('p.mb-0::text').re_first(r'Rates as of (.+)')
        updated_date = ''
        if raw_date:
            try:
                dt = datetime.strptime(raw_date.strip(), '%A, %B %d, %Y at %I:%M %p')
                updated_date = dt.strftime('%Y-%m-%d')
            except Exception:
                updated_date = raw_date.strip()

        # Focus only on the "Purchase" tab content
        purchase_section = response.css('div[aria-labelledby="purchase-0"]')
        rows = purchase_section.css('table tbody tr')

        for row in rows:
            product_full = row.css('th a::text').get(default='').strip()
            interest_rate = row.css('td:nth-of-type(1)::text').get(default='').strip()
            apr = row.css('td:nth-of-type(2)::text').get(default='').strip()

            if not product_full or not apr:
                continue

            # Extract numeric loan term from product name
            loan_term = ""
            match = re.search(r'(\d+)[- ]?Year', product_full)
            if match:
                loan_term = match.group(1)

            yield {
                "loan_product": product_full,
                "interest_rate": interest_rate,
                "apr_percent": apr,
                "loan_term_years": loan_term,
                # "monthly_payment": "",        # Placeholder, not on this page
                "lender_name": "Bankrate",    # Placeholder
                "updated_date": updated_date
            }
