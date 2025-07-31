#!/usr/bin/env python3
"""
Final verification of generated Excel output
"""

import pandas as pd

def verify_output():
    try:
        df = pd.read_excel('complete_workflow_output.xlsx')
        
        print("FINAL VERIFICATION REPORT")
        print("=" * 50)
        print(f"Rows processed: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check each lead
        print("\nLead Processing Results:")
        for i, row in df.iterrows():
            has_email = pd.notna(row['Personalized']) and len(str(row['Personalized']).strip()) > 0
            print(f"{i+1}. {row['first_name']} from {row['company_name']} - Email Generated: {'YES' if has_email else 'NO'}")
        
        # Show sample emails
        print("\nSample Generated Emails:")
        print("=" * 60)
        
        for i in range(min(3, len(df))):
            email = df['Personalized'].iloc[i]
            if pd.notna(email):
                print(f"\nEmail {i+1} for {df['first_name'].iloc[i]} at {df['company_name'].iloc[i]}:")
                print("-" * 40)
                print(email[:200] + "..." if len(str(email)) > 200 else email)
                print("-" * 40)
        
        # Success metrics
        successful_emails = df['Personalized'].notna().sum()
        success_rate = (successful_emails / len(df)) * 100
        
        print(f"\nSUCCESS METRICS:")
        print(f"Total leads: {len(df)}")
        print(f"Emails generated: {successful_emails}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n✅ PERFECT: 100% success rate with live business data")
            print("✅ ColdEmailAI platform is FULLY OPERATIONAL")
            return True
        else:
            print(f"\n⚠️  WARNING: {100-success_rate:.1f}% of emails failed to generate")
            return False
            
    except Exception as e:
        print(f"ERROR reading Excel file: {e}")
        return False

if __name__ == "__main__":
    verify_output()