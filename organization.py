"""
This module defines the Organization class, which models the essential
information about companies, including their name, funding details, and operational status.
It also includes functionality to create Organization instances from CSV data.
"""
# pylint: disable=too-many-instance-attributes
class Organization:
    def __init__(self, 
                 organization_name, 
                 organization_name_url, 
                 semrush_monthly_visits, 
                 number_of_contacts, 
                 operating_status, 
                 company_type, 
                 last_funding_date, 
                 full_description, 
                 last_funding_type, 
                 founded_date, 
                 founded_date_precision, 
                 industries, 
                 headquarters_location, 
                 description, 
                 cb_rank_company, 
                 last_funding_amount, 
                 last_funding_amount_currency, 
                 last_funding_amount_currency_in_usd, 
                 total_funding_amount, 
                 total_funding_amount_currency, 
                 total_funding_amount_currency_in_usd, 
                 number_of_investors, top_5_investors, 
                 number_of_lead_investors, 
                 website, 
                 headquarters_regions, 
                 estimated_revenue_range, 
                 twitter, 
                 facebook, 
                 linkedin, 
                 number_of_investments, 
                 number_of_lead_investments, 
                 accelerator_program_type, 
                 accelerator_application_deadline, 
                 accelerator_duration_in_weeks, 
                 number_of_founders, 
                 number_of_employees, 
                 founders,
                 _id = None,
                 website_context = None,
                 website_content = None,
                 website_content_tags = None,
                 batch=3):
        self.organization_name = organization_name
        self.organization_name_url = organization_name_url
        self.semrush_monthly_visits = semrush_monthly_visits
        self.number_of_contacts = number_of_contacts
        self.operating_status = operating_status
        self.company_type = company_type
        self.last_funding_date = last_funding_date
        self.full_description = full_description
        self.last_funding_type = last_funding_type
        self.founded_date = founded_date
        self.founded_date_precision = founded_date_precision
        self.industries = industries
        self.headquarters_location = headquarters_location
        self.description = description
        self.cb_rank_company = cb_rank_company
        self.last_funding_amount = last_funding_amount
        self.last_funding_amount_currency = last_funding_amount_currency
        self.last_funding_amount_currency_in_usd = last_funding_amount_currency_in_usd
        self.total_funding_amount = total_funding_amount
        self.total_funding_amount_currency = total_funding_amount_currency
        self.total_funding_amount_currency_in_usd = total_funding_amount_currency_in_usd
        self.number_of_investors = number_of_investors
        self.top_5_investors = top_5_investors
        self.number_of_lead_investors = number_of_lead_investors
        self.website = website
        self.headquarters_regions = headquarters_regions
        self.estimated_revenue_range = estimated_revenue_range
        self.twitter = twitter
        self.facebook = facebook
        self.linkedin = linkedin
        self.number_of_investments = number_of_investments
        self.number_of_lead_investments = number_of_lead_investments
        self.accelerator_program_type = accelerator_program_type
        self.accelerator_application_deadline = accelerator_application_deadline
        self.accelerator_duration_in_weeks = accelerator_duration_in_weeks
        self.number_of_founders = number_of_founders
        self.number_of_employees = number_of_employees
        self.founders = founders
        self._id = _id,
        self.website_context = website_context
        self.website_content = website_content
        self.website_content_tags = website_content_tags
        self.batch = batch

    @classmethod
    def from_doc(cls, doc): 
        return cls(**doc)

    @classmethod
    def from_csv_row(cls, row):
        # Explicit mapping of CSV columns to class constructor arguments
        return cls(
            organization_name=row.get("Organization Name"),
            organization_name_url=row.get("Organization Name URL"),
            semrush_monthly_visits=row.get("SEMrush - Monthly Visits"),
            number_of_contacts=row.get("Number of Contacts"),
            operating_status=row.get("Operating Status"),
            company_type=row.get("Company Type"),
            last_funding_date=row.get("Last Funding Date"),
            full_description=row.get("Full Description"),
            last_funding_type=row.get("Last Funding Type"),
            founded_date=row.get("Founded Date"),
            founded_date_precision=row.get("Founded Date Precision"),
            industries=row.get("Industries"),
            headquarters_location=row.get("Headquarters Location"),
            description=row.get("Description"),
            cb_rank_company=row.get("CB Rank (Company)"),
            last_funding_amount=row.get("Last Funding Amount"),
            last_funding_amount_currency=row.get("Last Funding Amount Currency"),
            last_funding_amount_currency_in_usd=row.get("Last Funding Amount Currency (in USD)"),
            total_funding_amount=row.get("Total Funding Amount"),
            total_funding_amount_currency=row.get("Total Funding Amount Currency"),
            total_funding_amount_currency_in_usd=row.get("Total Funding Amount Currency (in USD)"),
            number_of_investors=row.get("Number of Investors"),
            top_5_investors=row.get("Top 5 Investors"),
            number_of_lead_investors=row.get("Number of Lead Investors"),
            website=row.get("Website"),
            headquarters_regions=row.get("Headquarters Regions"),
            estimated_revenue_range=row.get("Estimated Revenue Range"),
            twitter=row.get("Twitter"),
            facebook=row.get("Facebook"),
            linkedin=row.get("LinkedIn"),
            number_of_investments=row.get("Number of Investments"),
            number_of_lead_investments=row.get("Number of Lead Investments"),
            accelerator_program_type=row.get("Accelerator Program Type"),
            accelerator_application_deadline=row.get("Accelerator Application Deadline"),
            accelerator_duration_in_weeks=row.get("Accelerator Duration (in weeks)"),
            number_of_founders=row.get("Number of Founders"),
            number_of_employees=row.get("Number of Employees"),
            founders=row.get("Founders")
        )

    def to_dict(self):
        return self.__dict__
    # Add more methods here as needed
