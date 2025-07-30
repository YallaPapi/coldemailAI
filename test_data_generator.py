"""
Test Data Generator for ColdEmailAI

Generates realistic business test data following TaskMaster research:
"realistic business test data generation CSV files company names employee data security testing malicious files 2025"

Uses real business data patterns as mandated by ZAD requirements.
"""

import csv
import random
import os
from typing import List, Dict


class BusinessTestDataGenerator:
    """Generate realistic business test data for ColdEmailAI testing"""
    
    def __init__(self):
        # Real business data from research
        self.companies = [
            "TechFlow Solutions", "Green Valley Farms", "BrightStar Consulting", 
            "AutoParts Direct", "Wellness Hub", "DataSync Corp", "CloudNet Systems",
            "InnovateLab", "SecureGuard Inc", "FastTrack Logistics", "PrimeTech Industries",
            "Horizon Manufacturing", "EliteCore Systems", "NexGen Solutions", "BlueSky Ventures",
            "Quantum Dynamics", "GlobalTrade Partners", "SteelWorks Corp", "MedTech Innovations",
            "EcoGreen Energy", "CyberShield Security", "RapidScale Technologies", "Unity Health Systems",
            "ProService Group", "Digital Frontier", "Apex Marketing", "SolarMax Energy",
            "FinanceFirst Corp", "BuildSmart Construction", "AeroTech Aerospace"
        ]
        
        self.first_names = [
            "Sarah", "David", "Jessica", "Marcus", "Amanda", "Robert", "Lisa",
            "Michael", "Jennifer", "William", "Susan", "James", "Patricia",
            "Christopher", "Karen", "Daniel", "Nancy", "Matthew", "Betty",
            "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna", "Steven",
            "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle"
        ]
        
        self.last_names = [
            "Johnson", "Chen", "Rodriguez", "Williams", "Taylor", "Brown", "Davis",
            "Miller", "Wilson", "Moore", "Anderson", "Thomas", "Jackson", "White",
            "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
            "Clark", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez",
            "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker"
        ]
        
        self.job_titles = [
            "CEO", "Chief Executive Officer", "Marketing Director", "Operations Manager", 
            "VP Sales", "Vice President Sales", "Founder", "CTO", "Chief Technology Officer",
            "Sales Manager", "Product Manager", "Director of Operations", "Vice President",
            "Regional Manager", "Business Development Manager", "Account Manager",
            "Senior Sales Representative", "Marketing Manager", "Operations Director",
            "General Manager", "President", "Senior Vice President", "Division Manager"
        ]
        
        self.industries = [
            "Software", "Technology", "Agriculture", "Business Services", "Automotive",
            "Healthcare", "Manufacturing", "Retail", "Finance", "Education",
            "Construction", "Energy", "Telecommunications", "Transportation",
            "Consulting", "Real Estate", "Insurance", "Pharmaceuticals",
            "Aerospace", "Food & Beverage", "Media", "Logistics", "Security"
        ]
        
        self.cities_states = [
            ("Austin", "TX"), ("Sacramento", "CA"), ("Miami", "FL"), ("Detroit", "MI"),
            ("Portland", "OR"), ("Denver", "CO"), ("Atlanta", "GA"), ("Phoenix", "AZ"),
            ("Seattle", "WA"), ("Boston", "MA"), ("Chicago", "IL"), ("Houston", "TX"),
            ("New York", "NY"), ("Los Angeles", "CA"), ("Philadelphia", "PA"),
            ("San Diego", "CA"), ("San Antonio", "TX"), ("Dallas", "TX"),
            ("San Jose", "CA"), ("Jacksonville", "FL"), ("Indianapolis", "IN"),
            ("Columbus", "OH"), ("Charlotte", "NC"), ("San Francisco", "CA"),
            ("Fort Worth", "TX"), ("Milwaukee", "WI"), ("El Paso", "TX"),
            ("Memphis", "TN"), ("Baltimore", "MD"), ("Nashville", "TN")
        ]
        
    def generate_small_business_leads(self, filename: str = "test_data/small_business_leads.csv"):
        """Generate 50-100 realistic small business leads"""
        leads = []
        num_leads = random.randint(75, 95)  # 75-95 leads
        
        for i in range(num_leads):
            company = f"{random.choice(self.companies)}"
            if random.random() < 0.3:  # 30% chance of numbered variant
                company += f" #{random.randint(1, 10)}"
                
            city, state = random.choice(self.cities_states)
            
            lead = {
                'first_name': random.choice(self.first_names),
                'last_name': random.choice(self.last_names),
                'company_name': company,
                'title': random.choice(self.job_titles),
                'industry': random.choice(self.industries),
                'city': city,
                'state': state,
                'country': 'United States'
            }
            leads.append(lead)
            
        self._write_csv(leads, filename)
        print(f"Generated {len(leads)} small business leads in {filename}")
        
    def generate_enterprise_leads(self, filename: str = "test_data/enterprise_leads.csv"):
        """Generate 2000+ realistic enterprise leads"""
        leads = []
        num_leads = 2100  # Slightly over 2000 as per requirements
        
        for i in range(num_leads):
            # Create more realistic company distribution
            base_company = random.choice(self.companies)
            if i < 1000:
                company = f"{base_company} #{i//50 + 1}"  # Multiple divisions
            else:
                company = f"{base_company} {random.choice(['Inc', 'Corp', 'LLC', 'Ltd'])}"
                
            city, state = random.choice(self.cities_states)
            
            lead = {
                'first_name': random.choice(self.first_names),
                'last_name': random.choice(self.last_names),
                'company_name': company,
                'title': random.choice(self.job_titles),
                'industry': random.choice(self.industries),
                'city': city,
                'state': state,
                'country': 'United States'
            }
            leads.append(lead)
            
        self._write_csv(leads, filename)
        print(f"Generated {len(leads)} enterprise leads in {filename}")
        
    def generate_messy_real_data(self, filename: str = "test_data/messy_real_data.csv"):
        """Generate messy data with real-world quality issues"""
        leads = []
        num_leads = 50
        
        # Inconsistent headers (mixed case, spaces)
        headers = ['First Name', ' Last Name ', 'COMPANY_NAME', 'Job Title', 'industry', 'City', 'State', 'Country']
        
        for i in range(num_leads):
            city, state = random.choice(self.cities_states)
            company = random.choice(self.companies)
            
            # Add various data quality issues
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            
            # 20% chance of missing data
            if random.random() < 0.2:
                first_name = ""
            if random.random() < 0.15:
                last_name = ""
                
            # Add extra spaces randomly
            if random.random() < 0.3:
                company += "  "
            if random.random() < 0.3:
                first_name = "  " + first_name
                
            # Mix case in industry
            industry = random.choice(self.industries)
            if random.random() < 0.5:
                industry = industry.lower()
                
            # Sometimes include commas in company names (CSV challenge)
            if random.random() < 0.2:
                company = f'"{company}, LLC"'
                
            lead = {
                'First Name': first_name,
                ' Last Name ': last_name,
                'COMPANY_NAME': company,
                'Job Title': random.choice(self.job_titles),
                'industry': industry,
                'City': city,
                'State': state,
                'Country': 'United States' if random.random() > 0.1 else ""  # 10% missing country
            }
            leads.append(lead)
            
        # Write with inconsistent headers
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(leads)
            
        print(f"Generated {len(leads)} messy business leads in {filename}")
        
    def generate_malicious_files(self):
        """Generate malicious files for security testing"""
        malicious_dir = "test_data/malicious_files"
        
        # 1. Fake executable disguised as CSV
        with open(os.path.join(malicious_dir, "virus.exe.csv"), 'wb') as f:
            f.write(b'MZ\x90\x00This is a fake executable file disguised as CSV')
            
        # 2. CSV injection attack
        csv_injection = """name,email,command
John Doe,john@example.com,"=cmd|'/c calc'!A1"
Jane Smith,jane@example.com,"=system('rm -rf /')"
Bob Wilson,bob@example.com,=HYPERLINK("http://malicious-site.com")"""
        with open(os.path.join(malicious_dir, "csv_injection.csv"), 'w') as f:
            f.write(csv_injection)
            
        # 3. Oversized file (20MB)
        with open(os.path.join(malicious_dir, "oversized.csv"), 'w') as f:
            f.write("data,content\n")
            for i in range(500000):  # Generate large file
                f.write(f"row_{i}," + "x" * 40 + "\n")
                
        # 4. Malformed CSV
        malformed = """name,email,company
John,john@example.com,Acme Corp
Jane,"jane@example.com,Tech Inc
Bob,bob@example.com,"Broken Quote Corp"""
        with open(os.path.join(malicious_dir, "malformed.csv"), 'w') as f:
            f.write(malformed)
            
        # 5. Empty file
        with open(os.path.join(malicious_dir, "empty.csv"), 'w') as f:
            pass
            
        # 6. Text file disguised as CSV
        with open(os.path.join(malicious_dir, "fake.txt.csv"), 'w') as f:
            f.write("This is not a CSV file at all, just plain text trying to disguise itself.")
            
        print("Generated malicious test files for security testing")
        
    def generate_edge_cases(self):
        """Generate edge case files with unicode and special characters"""
        edge_dir = "test_data/edge_cases"
        
        # Unicode names and special characters
        unicode_leads = [
            {
                'first_name': '张', 'last_name': '伟', 'company_name': 'Beijing Tech Solutions',
                'title': 'CEO', 'industry': 'Technology', 'city': 'Beijing', 'state': 'Beijing', 'country': 'China'
            },
            {
                'first_name': 'José', 'last_name': 'García', 'company_name': 'México Manufacturing',
                'title': 'Director', 'industry': 'Manufacturing', 'city': 'Mexico City', 'state': 'CDMX', 'country': 'Mexico'
            },
            {
                'first_name': 'François', 'last_name': 'Müller', 'company_name': 'Café & Bäckerei GmbH',
                'title': 'Propriétaire', 'industry': 'Food & Beverage', 'city': 'Paris', 'state': 'Île-de-France', 'country': 'France'
            },
            {
                'first_name': '🎯 John', 'last_name': 'Smith 💼', 'company_name': 'Emoji Corp 🚀',
                'title': 'Chief Fun Officer 🎉', 'industry': 'Social Media', 'city': 'San Francisco', 'state': 'CA', 'country': 'United States'
            }
        ]
        
        self._write_csv(unicode_leads, os.path.join(edge_dir, "unicode_data.csv"))
        
        # Very long field values
        long_leads = [{
            'first_name': 'VeryLongFirstNameThatExceedsNormalLengthExpectations' * 3,
            'last_name': 'EvenLongerLastNameThatCouldCauseProblemsInSomeSystemsIfNotHandledProperly' * 2,
            'company_name': 'An Extremely Long Company Name That Might Cause Issues In Some Database Systems Or User Interfaces If Not Properly Handled By The Application Logic' * 2,
            'title': 'Senior Executive Vice President of Global Operations and Strategic Business Development',
            'industry': 'Professional Services',
            'city': 'Los Angeles',
            'state': 'CA',
            'country': 'United States'
        }]
        
        self._write_csv(long_leads, os.path.join(edge_dir, "long_fields.csv"))
        
        print("Generated edge case test files")
        
    def _write_csv(self, data: List[Dict], filename: str):
        """Write data to CSV file"""
        if not data:
            return
            
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
    def generate_all_test_data(self):
        """Generate all test data files"""
        print("Generating realistic business test data following TaskMaster research...")
        self.generate_small_business_leads()
        self.generate_enterprise_leads()
        self.generate_messy_real_data()
        self.generate_malicious_files()
        self.generate_edge_cases()
        print("All test data generation completed!")


if __name__ == "__main__":
    generator = BusinessTestDataGenerator()
    generator.generate_all_test_data()