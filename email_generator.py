import os
import logging
import random
from openai import OpenAI
import pandas as pd

class EmailGenerator:
    """Handles AI-powered personalized email generation using OpenAI GPT-4"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        self.logger = logging.getLogger(__name__)
    
    def build_prompt(self, row):
        """Build personalized prompt for each lead with flexible field mapping"""
        # Extract data with flexible field names
        first_name = (row.get('First Name') or row.get('first_name') or '').strip()
        company_name = (row.get('Company Name') or row.get('organization/name') or row.get('company_name') or '').strip()
        
        # Job title - extremely valuable for personalization
        job_title = (row.get('title') or row.get('Title') or row.get('job_title') or '').strip()
        
        # Industry with multiple fallbacks
        industry = (row.get('Industry') or row.get('organization/industries') or 
                   row.get('organization/industries/0') or 'N/A').strip()
        
        # Enhanced location data
        city = (row.get('organization/city') or row.get('City') or '').strip()
        state = (row.get('State') or row.get('organization/state') or '').strip()
        country = (row.get('Country') or row.get('organization/country') or '').strip()
        
        # Company size for scale-appropriate messaging
        company_size = str(row.get('organization/estimated_num_employees') or 
                          row.get('company_size') or '').strip()
        
        # Company age/maturity
        founded_year = str(row.get('organization/founded_year') or 
                          row.get('founded_year') or '').strip()
        
        # Organization description (already implemented but with flexible naming)
        org_description = (row.get('Organization Short Description') or 
                          row.get('organization/short_description') or 
                          row.get('organization_description') or '').strip()
        
        # Build location string with priority: city, state, country
        location_parts = [part for part in [city, state, country] if part]
        location = ', '.join(location_parts) if location_parts else 'their location'
        
        # Build comprehensive prospect information
        prospect_info = f"""
Name: {first_name}
Company: {company_name}
Industry: {industry}
Location: {location}"""

        # Add job title for role-specific messaging
        if job_title:
            prospect_info += f"""
Title: {job_title}"""

        # Add company size for scale-appropriate messaging
        if company_size:
            try:
                size_num = int(company_size)
                if size_num <= 10:
                    size_context = "small team/startup"
                elif size_num <= 50:
                    size_context = "growing company"
                elif size_num <= 200:
                    size_context = "mid-size company"
                else:
                    size_context = "large enterprise"
                prospect_info += f"""
Company Size: {company_size} employees ({size_context})"""
            except:
                prospect_info += f"""
Company Size: {company_size} employees"""

        # Add company maturity for context
        if founded_year:
            try:
                year = int(founded_year)
                current_year = 2025
                age = current_year - year
                if age <= 2:
                    maturity = "newly established"
                elif age <= 5:
                    maturity = "growing startup"
                elif age <= 15:
                    maturity = "established business"
                else:
                    maturity = "well-established company"
                prospect_info += f"""
Founded: {founded_year} ({maturity})"""
            except:
                prospect_info += f"""
Founded: {founded_year}"""

        # Add organization description for deep personalization
        if org_description:
            prospect_info += f"""
Organization Description: {org_description}"""

        # Build personalized instructions based on available data
        personalization_instructions = []
        
        if job_title:
            personalization_instructions.append(f"Address them appropriately for their role as {job_title}, focusing on challenges and benefits relevant to their position and decision-making authority.")
        
        if company_size:
            try:
                size_num = int(company_size)
                if size_num <= 50:
                    personalization_instructions.append("Focus on solutions that help small/growing companies scale efficiently without large infrastructure investments.")
                else:
                    personalization_instructions.append("Emphasize enterprise-grade solutions that can handle scale and integrate with existing systems.")
            except:
                pass
        
        if org_description:
            personalization_instructions.append("Use specific insights from the organization description to identify unique business challenges and demonstrate genuine understanding of their context.")
        
        if founded_year:
            try:
                year = int(founded_year)
                age = 2025 - year
                if age <= 5:
                    personalization_instructions.append("Reference growth-stage challenges and scalability opportunities appropriate for a newer company.")
                else:
                    personalization_instructions.append("Focus on modernization and efficiency improvements for their established operations.")
            except:
                pass
        
        # Add location-based personalization for more personal connection
        if city or state:
            location_reference = city if city else state
            location_lower = location_reference.lower()
            
            # Vegas/Las Vegas specific personalization
            if 'vegas' in location_lower or 'las vegas' in location_lower:
                vegas_jokes = [
                    "Hope you're not too tired from all that Vegas networking!",
                    "Betting you're always looking for ways to streamline operations (see what I did there?)",
                    "I know Vegas moves fast, so I'll keep this quick",
                    "Hope the desert heat isn't slowing down your business growth"
                ]
                personalization_instructions.append(f"Add a casual Vegas reference like: '{random.choice(vegas_jokes)}'")
            
            # California specific
            elif 'california' in location_lower or location_lower in ['ca', 'san francisco', 'los angeles', 'la', 'sf']:
                ca_references = [
                    "I know the California market moves fast",
                    "Hope you're staying ahead of the innovation curve out there",
                    "I imagine scaling in California comes with unique challenges",
                    "The West Coast tech scene keeps everyone on their toes"
                ]
                personalization_instructions.append(f"Add a California reference like: '{random.choice(ca_references)}'")
            
            # Texas specific
            elif 'texas' in location_lower or location_lower in ['tx', 'dallas', 'houston', 'austin']:
                texas_references = [
                    "Everything's bigger in Texas, including the opportunities",
                    "I know Texas businesses don't mess around when it comes to results",
                    "The Lone Star State is always looking for innovative solutions",
                    "Texas companies know how to scale efficiently"
                ]
                personalization_instructions.append(f"Add a Texas reference like: '{random.choice(texas_references)}'")
            
            # New York specific
            elif 'new york' in location_lower or location_lower in ['ny', 'nyc', 'manhattan']:
                ny_references = [
                    "I know New York moves at lightning speed",
                    "The Big Apple demands efficiency in everything",
                    "NYC companies are always ahead of the curve",
                    "I imagine you're juggling a million things in the city"
                ]
                personalization_instructions.append(f"Add a New York reference like: '{random.choice(ny_references)}'")
            
            # Miami/Florida specific
            elif 'miami' in location_lower or 'florida' in location_lower or location_lower in ['fl']:
                florida_references = [
                    "Hope you're staying cool down in the sunshine state",
                    "I know Florida businesses are booming right now",
                    "The Miami tech scene is really taking off",  
                    "Florida's growth market has so many opportunities"
                ]
                personalization_instructions.append(f"Add a Florida reference like: '{random.choice(florida_references)}'")
            
            # Generic location personalization for other cities/states
            else:
                generic_references = [
                    f"Hope things are going well in {location_reference}",
                    f"I know the {location_reference} market has been interesting lately",
                    f"Always enjoy connecting with businesses in {location_reference}",
                    f"The business climate in {location_reference} seems really dynamic"
                ]
                personalization_instructions.append(f"Add a location reference like: '{random.choice(generic_references)}'")


        # Build the prompt with enhanced personalization
        instruction_text = " ".join(personalization_instructions) if personalization_instructions else "Identify common pain points in their industry and explain how AI automation can address them."

        prompt = f"""
Write a natural, conversational cold email using this contact information:

{prospect_info}

Write like you're a real person reaching out - natural, authentic, non-promotional tone.

Key guidelines:
- Start casually: "Hey [name]", "Hi [name]", "[name], hope you're well"
- Mention you work with AI automation in a casual way
- Reference their specific situation when possible: {instruction_text}
- Keep it conversational and authentic
- End with if-then call CTA + "if not, all good/no worries/totally fine" with smiley
- Use proper spacing with blank lines between paragraphs for readability
- NO signatures, names, or formal closings
- 50-70 words max

Make each email sound completely different - vary greetings, structure, tone, and phrasing naturally.
""".strip()
        
        return prompt
    
    def generate_email(self, prompt, retry_count=0):
        """Generate personalized email using OpenAI GPT-4 with robust error handling"""
        max_retries = 2
        
        try:
            # Using gpt-4o-mini for better quality email generation
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Write ONE conversational cold email. Use proper spacing with blank lines between paragraphs. End with fallback phrase only - NO signatures, names, dashes, or extra text. Structure: Greeting + blank line + Main content + blank line + CTA + blank line + Fallback with smiley."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.8,
                timeout=20  # Reduced timeout to prevent hanging
            )
            
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
            else:
                self.logger.warning("Empty response from OpenAI, using fallback")
                return self.generate_fallback_email(prompt)
            
        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"OpenAI API error (attempt {retry_count + 1}): {str(e)}")
            
            # Retry logic for specific transient errors only
            if retry_count < max_retries:
                if any(term in error_msg for term in ['rate_limit', 'timeout', 'connection', 'temporary']):
                    import time
                    wait_time = min(2 ** retry_count, 10)  # Cap wait time at 10 seconds
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self.generate_email(prompt, retry_count + 1)
            
            # Fallback email for all other cases
            self.logger.info("Using fallback email due to API issues")
            return self.generate_fallback_email(prompt)
    
    def generate_fallback_email(self, prompt):
        """Generate a basic fallback email when AI fails"""
        # Extract name from prompt for basic personalization
        lines = prompt.split('\n')
        name = "there"
        for line in lines:
            if line.startswith("Name:"):
                name = line.split(":", 1)[1].strip()
                break
        
        return f"""Hey {name},

Hope you're doing well.

I'm Alex, and I help businesses automate their operations with AI tools. I think your company could benefit from AI solutions like customer chat automation, lead follow-up systems, and sales process optimization.

These tools can help you scale efficiently without major infrastructure investments.

Would you be interested in a quick 15-minute chat to explore how this might work for your business?

Let me know if you'd like to discuss further."""
    
    def process_leads(self, df):
        """Process all leads in the DataFrame and generate personalized emails"""
        total_leads = len(df)
        self.logger.info(f"Starting to process {total_leads} leads")
        
        emails = []
        successful_count = 0
        failed_count = 0
        
        for index, row in df.iterrows():
            first_name = str(row.get('first_name') or row.get('First Name') or 'Unknown')
            company_name = str(row.get('company_name') or row.get('Company Name') or 'Unknown Company')
            try:
                # Get identifying info for logging
                
                self.logger.debug(f"Processing lead {index + 1}/{total_leads}: {first_name} at {company_name}")
                
                # Build prompt for this lead
                prompt = self.build_prompt(row)
                
                # Generate email with fallback logic
                email = self.generate_email(prompt)
                emails.append(email)
                
                if "Error generating email:" not in email:
                    successful_count += 1
                else:
                    failed_count += 1
                
                # Log progress for every 50 leads for large batches
                if (index + 1) % 50 == 0:
                    self.logger.info(f"Progress: {index + 1}/{total_leads} leads processed ({successful_count} successful, {failed_count} failed)")
                
                # Add small delay for large batches to avoid overwhelming API
                if total_leads > 1000 and (index + 1) % 10 == 0:
                    import time
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Critical error processing lead {index + 1}: {str(e)}")
                # Add fallback email even for critical errors
                emails.append(self.generate_fallback_email(f"Name: {first_name}"))
                failed_count += 1
        
        # Add emails to DataFrame
        df_copy = df.copy()
        df_copy['Personalized'] = emails
        
        self.logger.info(f"Completed processing {total_leads} leads: {successful_count} successful, {failed_count} failed")
        return df_copy
    
    def process_leads_with_mapping(self, mapped_df, mapping):
        """Process leads using user-defined column mapping"""
        total_leads = len(mapped_df)
        self.logger.info(f"Starting to process {total_leads} leads with custom mapping: {mapping}")
        
        emails = []
        successful_count = 0
        failed_count = 0
        
        for index, row in mapped_df.iterrows():
            first_name = str(row.get('first_name', 'Unknown'))
            company_name = str(row.get('company_name', 'Unknown Company'))
            try:
                # Get identifying info for logging
                
                self.logger.debug(f"Processing lead {index + 1}/{total_leads}: {first_name} at {company_name}")
                
                # Build custom prompt using mapped fields
                prompt = self.build_custom_prompt(row, mapping)
                
                # Generate email with fallback logic
                email = self.generate_email(prompt)
                emails.append(email)
                
                if "Error generating email:" not in email:
                    successful_count += 1
                else:
                    failed_count += 1
                
                # Log progress for every 50 leads for large batches
                if (index + 1) % 50 == 0:
                    self.logger.info(f"Progress: {index + 1}/{total_leads} leads processed ({successful_count} successful, {failed_count} failed)")
                
                # Add small delay for large batches to avoid overwhelming API
                if total_leads > 1000 and (index + 1) % 10 == 0:
                    import time
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Critical error processing lead {index + 1}: {str(e)}")
                # Add fallback email even for critical errors
                emails.append(self.generate_fallback_email(f"Name: {first_name}"))
                failed_count += 1
        
        # Add emails to DataFrame
        result_df = mapped_df.copy()
        result_df['Personalized'] = emails
        
        self.logger.info(f"Completed processing {total_leads} leads: {successful_count} successful, {failed_count} failed")
        return result_df
    
    def build_custom_prompt(self, row, mapping):
        """Build personalized prompt using user-defined field mapping"""
        # Get mapped fields
        first_name = str(row.get('first_name', '')).strip()
        company_name = str(row.get('company_name', '')).strip()
        job_title = str(row.get('job_title', '')).strip()
        industry = str(row.get('industry', '')).strip()
        city = str(row.get('city', '')).strip()
        state = str(row.get('state', '')).strip()
        country = str(row.get('country', '')).strip()
        company_description = str(row.get('company_description', '')).strip()
        
        # Build location string
        location_parts = [part for part in [city, state, country] if part]
        location = ', '.join(location_parts) if location_parts else 'their location'
        
        # Build comprehensive prospect information
        prospect_info = f"""
Name: {first_name}
Company: {company_name}
Industry: {industry if industry else 'N/A'}
Location: {location}"""

        # Add job title for role-specific messaging
        if job_title:
            prospect_info += f"""
Title: {job_title}"""

        # Add company description for unique business insights
        if company_description:
            prospect_info += f"""
Company Description: {company_description}"""
        
        # Location-based personalization with variety
        location_reference = ""
        if city and state:
            location_lower = city.lower()
            state_lower = state.lower()
            
            # Vegas references
            if 'vegas' in location_lower or 'las vegas' in location_lower:
                vegas_refs = [
                    f"I know Vegas moves fast",
                    f"Vegas is all about growth and opportunity", 
                    f"In the Vegas market, speed matters",
                    f"Vegas businesses know how to scale quickly"
                ]
                location_reference = random.choice(vegas_refs)
            
            # California references
            elif state_lower == 'california' or 'ca' in state_lower:
                ca_refs = [
                    f"California's innovation ecosystem is incredible",
                    f"In the California market, staying ahead is everything",
                    f"California companies are always pushing boundaries",
                    f"The California business landscape moves fast"
                ]
                location_reference = random.choice(ca_refs)
            
            # Texas references
            elif state_lower == 'texas' or 'tx' in state_lower:
                tx_refs = [
                    f"Texas businesses think big",
                    f"Everything's bigger in Texas, including opportunities",
                    f"Texas companies know how to scale",
                    f"The Texas market is booming"
                ]
                location_reference = random.choice(tx_refs)
            
            # New York references
            elif state_lower == 'new york' or 'ny' in state_lower:
                ny_refs = [
                    f"New York pace demands efficient solutions",
                    f"In the NYC market, every minute counts",
                    f"New York businesses move at lightning speed",
                    f"The New York market is all about efficiency"
                ]
                location_reference = random.choice(ny_refs)
            
            # Florida references
            elif state_lower == 'florida' or 'fl' in state_lower:
                fl_refs = [
                    f"Florida's business climate is thriving",
                    f"The Florida market is growing rapidly",
                    f"Florida companies are expanding fast",
                    f"Florida's business environment is dynamic"
                ]
                location_reference = random.choice(fl_refs)
        
        # Base prompt with variations for natural diversity
        base_prompts = [
            f"Write a conversational cold email to {first_name} at {company_name}.",
            f"Create a friendly cold outreach email for {first_name} from {company_name}.",
            f"Draft a personalized cold email to {first_name} who works at {company_name}."
        ]
        
        base_prompt = random.choice(base_prompts)
        
        # Build complete prompt
        prompt = f"""{base_prompt}

Prospect Details:{prospect_info}

IMPORTANT INSTRUCTIONS:
- Write ONE complete email only
- Use EXACTLY this structure: Greeting + blank line + Main content + blank line + Call-to-action + blank line + Fallback phrase with smiley face
- NO signatures, names, dashes, or extra text after the fallback
- Keep it conversational and genuine
- Mention I help businesses automate operations with AI tools (customer chat automation, lead follow-up systems, sales process optimization)
- Include a specific call-to-action for a 15-minute chat
- End with a fallback phrase like "Let me know if you'd like to discuss further :)" or similar
"""

        # Add location reference if available
        if location_reference:
            prompt += f"""
- Include this location insight naturally: "{location_reference}"
"""

        # Add role-specific messaging if job title available
        if job_title:
            job_lower = job_title.lower()
            if any(word in job_lower for word in ['ceo', 'founder', 'president', 'owner']):
                prompt += """
- Focus on strategic benefits: scaling operations, reducing overhead, growth acceleration
"""
            elif any(word in job_lower for word in ['operations', 'ops', 'manager', 'director']):
                prompt += """
- Focus on operational efficiency: process automation, workflow optimization, team productivity
"""
            elif any(word in job_lower for word in ['sales', 'business development', 'revenue']):
                prompt += """
- Focus on sales acceleration: lead qualification, follow-up automation, pipeline efficiency
"""

        # Add company description context if available
        if company_description:
            prompt += f"""
- Reference their business context: "{company_description}"
"""

        prompt += """
Make each email sound completely different - vary greetings, structure, tone, and phrasing naturally.
""".strip()
        
        return prompt
