#!/usr/bin/env python3
"""
Create a larger test CSV file to validate chunked processing and memory management
"""
import pandas as pd
import random

def create_large_test_file():
    """Create a larger CSV file for testing chunked processing"""
    
    # Sample data for generation
    first_names = ["John", "Sarah", "David", "Jessica", "Marcus", "Amanda", "Michael", "Emily", "Robert", "Lisa", 
                   "James", "Jennifer", "William", "Ashley", "Richard", "Michelle", "Thomas", "Stephanie", "Christopher", "Angela"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    titles = ["CEO", "CTO", "Marketing Director", "Sales Manager", "Operations Manager", "VP Sales", "Founder", 
              "COO", "Head of Marketing", "Product Manager", "Business Development Manager", "Account Executive"]
    
    companies = ["TechFlow Solutions", "Green Valley Farms", "BrightStar Consulting", "AutoParts Direct", 
                  "Wellness Hub", "DataDrive Analytics", "CloudSync Systems", "NextGen Industries", 
                  "Precision Manufacturing", "Digital Marketing Pro", "HealthTech Innovations", "SmartHome Solutions"]
    
    industries = ["Software", "Agriculture", "Business Services", "Automotive", "Healthcare", "Technology",
                  "Manufacturing", "Marketing", "Real Estate", "Finance", "Education", "Consulting"]
    
    cities = ["Austin", "Sacramento", "Miami", "Detroit", "Portland", "Seattle", "Denver", "Atlanta", 
              "Boston", "Phoenix", "San Diego", "Chicago", "Dallas", "Los Angeles", "New York"]
    
    states = ["TX", "CA", "FL", "MI", "OR", "WA", "CO", "GA", "MA", "AZ", "IL", "NY"]
    
    # Generate larger dataset (2000 rows)
    num_rows = 2000
    data = []
    
    print(f"Generating {num_rows} rows of test data...")
    
    for i in range(num_rows):
        row = {
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names), 
            'title': random.choice(titles),
            'company_name': random.choice(companies) + f" #{i//50 + 1}",  # Add variety
            'industry': random.choice(industries),
            'city': random.choice(cities),
            'state': random.choice(states),
            'country': 'United States',
            'organization_short_description': f"A leading company in {random.choice(industries).lower()} sector",
            'founded_year': random.randint(2000, 2023),
            'company_size': random.choice([5, 10, 15, 25, 50, 75, 100, 250, 500])
        }
        data.append(row)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    filename = "large_test.csv"
    df.to_csv(filename, index=False)
    
    print(f"Created {filename} with {len(df)} rows and {len(df.columns)} columns")
    print(f"File size: {round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)} MB in memory")
    
    return filename

if __name__ == "__main__":
    create_large_test_file()