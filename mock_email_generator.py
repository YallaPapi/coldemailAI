import os
import logging
import random
import pandas as pd

class MockEmailGenerator:
    """Mock email generator for testing without OpenAI API"""
    
    def __init__(self):
        """Initialize mock email generator"""
        self.logger = logging.getLogger(__name__)
        
    def build_prompt(self, row):
        """Build personalized prompt for each lead with flexible field mapping"""
        # Extract data with flexible field names (same logic as real generator)
        first_name = (row.get('First Name') or row.get('first_name') or '').strip()
        company_name = (row.get('Company Name') or row.get('organization/name') or row.get('company_name') or '').strip()
        job_title = (row.get('title') or row.get('Title') or row.get('job_title') or '').strip()
        industry = (row.get('Industry') or row.get('organization/industries') or 
                   row.get('organization/industries/0') or 'N/A').strip()
        
        return f"Generate email for {first_name} at {company_name} ({job_title}) in {industry}"
    
    def generate_email(self, row):
        """Generate a mock email for testing purposes"""
        first_name = (row.get('First Name') or row.get('first_name') or 'there').strip()
        company_name = (row.get('Company Name') or row.get('company_name') or 'your company').strip()
        job_title = (row.get('title') or row.get('Title') or 'professional').strip()
        
        # Generate a simple mock email
        templates = [
            f"Hi {first_name},\n\nI noticed {company_name} is doing great work in your industry. As {job_title}, I thought you might be interested in discussing how we can help your team achieve even better results.\n\nBest regards,\n[Your Name]",
            f"Hello {first_name},\n\nI've been following {company_name}'s progress and I'm impressed by your work as {job_title}. I'd love to connect and share some insights that could benefit your team.\n\nLooking forward to connecting,\n[Your Name]",
            f"Dear {first_name},\n\nAs {job_title} at {company_name}, you're probably always looking for ways to optimize your operations. I have some ideas that might interest you.\n\nWould you be open to a brief conversation?\n\n[Your Name]"
        ]
        
        return random.choice(templates)
    
    def generate_fallback_email(self, row):
        """Generate a simple fallback email"""
        return "Hi there,\n\nI'd love to connect and discuss how we can help your business grow.\n\nBest regards,\n[Your Name]"
    
    def process_leads_with_mapping(self, df, mapping):
        """Process leads with mapping (mock version)"""
        results = []
        
        for _, row in df.iterrows():
            try:
                # Generate mock email
                email = self.generate_email(row)
                
                # Create result row
                result_row = row.copy()
                result_row['generated_email'] = email
                result_row['generation_status'] = 'success'
                results.append(result_row)
                
            except Exception as e:
                self.logger.error(f"Error generating email for row: {str(e)}")
                fallback_email = self.generate_fallback_email(row)
                result_row = row.copy()
                result_row['generated_email'] = fallback_email
                result_row['generation_status'] = 'fallback'
                results.append(result_row)
        
        return pd.DataFrame(results)