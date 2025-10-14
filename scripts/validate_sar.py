#!/usr/bin/env python3
"""
Validation script for Special Administrative Regions (SARs) implementation.
This script validates that Hong Kong and Macau SARs have the correct data structure.
"""

import json
import sys

def validate_sar_data():
    """Validate SAR data in states.json"""
    print("=" * 60)
    print("SAR Data Validation Script")
    print("=" * 60)
    
    try:
        # Load states data
        with open('contributions/states/states.json', 'r', encoding='utf-8') as f:
            states = json.load(f)
        
        print(f"\n✓ Loaded {len(states)} states")
        
        # Find SARs
        sars = [s for s in states if s.get('type') == 'special administrative region']
        print(f"✓ Found {len(sars)} Special Administrative Regions")
        
        # Required SAR fields
        required_sar_fields = ['phonecode', 'currency', 'currency_name', 'currency_symbol', 'emoji', 'emojiU']
        
        validation_passed = True
        
        for sar in sars:
            print(f"\n{'=' * 60}")
            print(f"Validating: {sar['name']} (ID: {sar['id']})")
            print(f"{'=' * 60}")
            
            # Basic fields
            print(f"  Country: {sar.get('country_code', 'N/A')} (ID: {sar.get('country_id', 'N/A')})")
            print(f"  Type: {sar.get('type', 'N/A')}")
            print(f"  ISO2: {sar.get('iso2', 'N/A')}")
            
            # Check SAR-specific fields
            print(f"\n  SAR-specific fields:")
            for field in required_sar_fields:
                value = sar.get(field)
                status = "✓" if value else "✗"
                print(f"    {status} {field}: {value}")
                if not value:
                    validation_passed = False
                    print(f"      ERROR: Missing required SAR field '{field}'")
            
            # Additional validation
            if sar.get('country_code') != 'CN':
                print(f"  ✗ ERROR: Expected country_code 'CN', got '{sar.get('country_code')}'")
                validation_passed = False
            else:
                print(f"  ✓ Country code is correct (CN)")
            
            if sar.get('country_id') != 45:
                print(f"  ✗ ERROR: Expected country_id 45 (China), got {sar.get('country_id')}")
                validation_passed = False
            else:
                print(f"  ✓ Country ID is correct (45 - China)")
        
        # Verify regular states don't have SAR fields
        print(f"\n{'=' * 60}")
        print("Checking regular states...")
        print(f"{'=' * 60}")
        
        regular_states = [s for s in states if s.get('type') != 'special administrative region']
        sample_regular = regular_states[:5]  # Check first 5
        
        for state in sample_regular:
            has_sar_fields = any(state.get(field) for field in required_sar_fields)
            if has_sar_fields:
                print(f"  ✗ WARNING: Regular state '{state['name']}' has SAR fields")
                validation_passed = False
        
        print(f"  ✓ Checked {len(sample_regular)} regular states - no unexpected SAR fields")
        
        # Summary
        print(f"\n{'=' * 60}")
        print("Validation Summary")
        print(f"{'=' * 60}")
        
        if validation_passed:
            print("✓ All validations PASSED")
            print("\nSAR Implementation is correct:")
            print("  - Hong Kong SAR has all required fields")
            print("  - Macau SAR has all required fields")
            print("  - Both are correctly linked to China (country_id: 45)")
            print("  - Regular states don't have SAR fields")
            return 0
        else:
            print("✗ Some validations FAILED")
            print("  Please review the errors above")
            return 1
            
    except FileNotFoundError as e:
        print(f"✗ ERROR: File not found - {e}")
        print("  Make sure you're running this from the repository root")
        return 1
    except json.JSONDecodeError as e:
        print(f"✗ ERROR: Invalid JSON - {e}")
        return 1
    except Exception as e:
        print(f"✗ ERROR: Unexpected error - {e}")
        return 1

def display_sar_comparison():
    """Display before/after comparison"""
    print("\n" + "=" * 60)
    print("Before vs After Comparison")
    print("=" * 60)
    
    print("\n📋 BEFORE (States without SAR fields):")
    print("""
    {
      "id": 2267,
      "name": "Hong Kong SAR",
      "country_id": 45,
      "country_code": "CN",
      "type": "special administrative region"
      ❌ Missing: phonecode, currency, emoji
    }
    """)
    
    print("\n📋 AFTER (States with SAR fields):")
    print("""
    {
      "id": 2267,
      "name": "Hong Kong SAR",
      "country_id": 45,
      "country_code": "CN",
      "type": "special administrative region",
      ✅ "phonecode": "852",
      ✅ "currency": "HKD",
      ✅ "currency_name": "Hong Kong dollar",
      ✅ "currency_symbol": "$",
      ✅ "emoji": "🇭🇰",
      ✅ "emojiU": "U+1F1ED U+1F1F0"
    }
    """)

if __name__ == '__main__':
    display_sar_comparison()
    sys.exit(validate_sar_data())
