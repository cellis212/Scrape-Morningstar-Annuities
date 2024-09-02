 # nolint start: line_length_linter, trailing_whitespace_linter.
import csv
import re
import unittest
import json

def is_annuity_data_empty(text):
    """
    Check if the annuity data is empty based on the provided examples.
    
    Args:
    text (str): The text content of the annuity data.
    
    Returns:
    bool: True if the data is considered empty, False otherwise.
    """
    # Split the text into lines
    lines = text.strip().splitlines()
    
    # Check for specific patterns that indicate non-empty data
    non_empty_patterns = [
        "Contract Information",
        "Share Class",
        "Prospectus Date",
        "Inception Date",
        "Expenses and Fees",
        "Mortality and Expense Risk (M&E)",
        "Summary of Available and Historic Benefits"
    ]
    
    # Count how many non_empty_patterns are found in the text
    pattern_count = sum(1 for pattern in non_empty_patterns if any(pattern in line for line in lines))
    
    # If at least 3 of the non_empty_patterns are found, consider the data non-empty
    return pattern_count < 3

def parse_contract_info(lines):
    contract_info_data = {}
    keys = [
        "Share Class", "Prospectus Date", "Supplement Date", 
        "Date of Last Update", "Inception Date", "Closed Date", 
        "AM Best Rating", "Website", "Phone Number", "State Availability"
    ]
    
    for i, line in enumerate(lines):
        line = line.strip()
        for key in keys:
            if key.lower() in line.lower():
                value = line.split(':', 1)[-1].strip() if ':' in line else lines[i+1].strip()
                contract_info_data[key] = value
                break  # Move to the next line after finding a match
    
    return contract_info_data

def parse_surrender_schedule(lines):
    surrender_schedule_data = {}
    keys = [
        "Duration (Years)", "Surrender Charge Schedule (%)", "Free Withdrawals", "Special Conditions"
    ]
    
    in_surrender_schedule_section = False
    for i, line in enumerate(lines):
        if "Surrender Schedule" in line:
            in_surrender_schedule_section = True
            continue
        
        if not in_surrender_schedule_section:
            continue
        
        if line.strip() == "":
            in_surrender_schedule_section = False
            break
        
        for key in keys:
            if key in line:
                value = line.split(':', 1)[-1].strip() if ':' in line else lines[i+1].strip()
                surrender_schedule_data[key] = value
                break
    
    return surrender_schedule_data

def parse_expenses_fees(lines):
    expenses_fees_data = {}
    keys = [
        "Mortality and Expense Risk (M&E)", "Administrative Charge", "Distribution Charge", 
        "Total Annual Expense", "Annual Contract Fee", "Anniversary Contract Fee Waived at", 
        "M&E Fee", "Admin Fee", "Annual Policy Fee", "Premium Based Sales Charges"
    ]
    
    for i, line in enumerate(lines):
        if any(key in line for key in keys):
            key, value = line.split(':', 1) if ':' in line else (line, lines[i+1].strip())
            expenses_fees_data[key.strip()] = value.strip()
    
    return expenses_fees_data

def parse_benefits_continuation(lines):
    benefits_continuation_data = {}
    keys = [
        "Can either spouse trigger the Guaranteed Death Benefit?", 
        "If spousally continued is death benefit credited?", 
        "If spousally continued is CDSC waived?", 
        "Special Note"
    ]
    
    in_benefits_section = False
    for i, line in enumerate(lines):
        if "Spousal Benefits and Continuation" in line:
            in_benefits_section = True
            continue
        
        if not in_benefits_section:
            continue
        
        if line.strip() == "":
            in_benefits_section = False
            break
        
        for key in keys:
            if key in line:
                value = line.split(':', 1)[-1].strip() if ':' in line else lines[i+1].strip()
                benefits_continuation_data[key] = value
                break
    
    if "Sample Titling for Obtaining Spousal Benefits on a Non-Qualified Contract" in ' '.join(lines):
        benefits_continuation_data["Sample Titling for Obtaining Spousal Benefits on a Non-Qualified Contract"] = {
            "Owner": "Husband",
            "Joint Owner": "Wife",
            "Annuitant": "Husband",
            "Joint Annuitant": "Wife",
            "Primary Beneficiary": "Anybody",
            "Secondary Beneficiary": "Anybody"
        }
    
    return benefits_continuation_data

def parse_issue_ages_contributions(lines):
    issue_ages_contributions_data = {
        "Plan Type": {}
    }
    plan_types = ["Qualified", "Non-Qualified"]
    current_plan_type = None
    in_issue_ages_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if "Issue Ages and Contributions" in line:
            in_issue_ages_section = True
            continue
        
        if not in_issue_ages_section:
            continue
        
        if line in plan_types:
            current_plan_type = line
            issue_ages_contributions_data["Plan Type"][current_plan_type] = {}
        elif current_plan_type and line:
            if "Min-Max Age" not in issue_ages_contributions_data["Plan Type"][current_plan_type]:
                issue_ages_contributions_data["Plan Type"][current_plan_type]["Min-Max Age"] = line
            elif "Life(ives)" not in issue_ages_contributions_data["Plan Type"][current_plan_type]:
                issue_ages_contributions_data["Plan Type"][current_plan_type]["Life(ives)"] = line
            elif "Initial" not in issue_ages_contributions_data["Plan Type"][current_plan_type]:
                issue_ages_contributions_data["Plan Type"][current_plan_type]["Initial"] = line
            elif "Subsequent" not in issue_ages_contributions_data["Plan Type"][current_plan_type]:
                issue_ages_contributions_data["Plan Type"][current_plan_type]["Subsequent"] = line
        
        # Handle Maximum Annuitization Age parsing
        if "Maximum Annuitization Age" in line:
            max_age = line.split(':')[-1].strip().rstrip(';')
            issue_ages_contributions_data["Maximum Annuitization Age"] = max_age
        
        # Stop parsing at Subaccount Information
        if line.startswith("Subaccount Information"):
            break
    
    return issue_ages_contributions_data
def parse_subaccount_information(lines):
    result = {}
    in_section = False
    data_lines = []
    for line in lines:
        if "Subaccount Information" in line:
            in_section = True
            continue
        if in_section:
            if line.strip() == "" and len(data_lines) > 8:
                break
            data_lines.append(line.strip())
    
    # Find the index where the actual data starts
    data_start = next((i for i, line in enumerate(data_lines) if line.isdigit()), -1)
    
    if data_start != -1 and len(data_lines) >= data_start + 4:
        result["Number of Subaccounts"] = data_lines[data_start]
        result["Subaccount Fee Range"] = data_lines[data_start + 1]
        result["Free Transfers Per Year"] = data_lines[data_start + 2]
        result["Transfer Fee"] = data_lines[data_start + 3]
    
    return result


def parse_plan_availability(lines):
    plan_availability_data = {
        "Plan Availability": "",
        "Surrender Charge Waivers": ""
    }
    
    for i, line in enumerate(lines):
        if "Plan Availability" in line:
            if ":" in line:
                plan_availability_data["Plan Availability"] = line.split(':', 1)[-1].strip()
            else:
                plan_availability_data["Plan Availability"] = lines[i+1].strip()
        elif "Surrender Charge Waivers" in line:
            if ":" in line:
                plan_availability_data["Surrender Charge Waivers"] = line.split(':', 1)[-1].strip()
            else:
                plan_availability_data["Surrender Charge Waivers"] = lines[i+1].strip()
    
    return plan_availability_data

def parse_benefits(lines):
    benefits = []
    in_benefits_section = False
    current_benefit = {}
    benefit_keys = ["Benefit Name", "Inception Date", "Close Date", "Benefit Type", "Impact of Withdrawals"]
    key_index = 0
    
    for line in lines:
        line = line.strip()
        
        if "Summary of Available and Historic Benefits" in line:
            in_benefits_section = True
            continue
        
        if not in_benefits_section:
            continue
        
        if line == "Select sort field:":
            break
        
        if line and line not in benefit_keys:
            current_benefit[benefit_keys[key_index]] = line
            key_index += 1
            
            if key_index == len(benefit_keys):
                benefits.append(current_benefit)
                current_benefit = {}
                key_index = 0
    
    return benefits

def parse_annuity_data(file_path):
    parsed_data = []
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        
        for row in reader:
            annuity_number = row[0]
            text = row[1]
            
            # Check if the annuity data is empty
            if is_annuity_data_empty(text):
                print(f"Skipping empty annuity data for Annuity {annuity_number}")
                continue
            
            lines = text.splitlines()
            
            parsed_entry = {"Annuity Number": annuity_number}
            
            parsing_functions = {
                "Contract Information": parse_contract_info,
                "Surrender Schedule": parse_surrender_schedule,
                "Expenses and Fees": parse_expenses_fees,
                "Benefits and Continuation": parse_benefits_continuation,
                "Issue Ages and Contributions": parse_issue_ages_contributions,
                "Subaccount Information": parse_subaccount_information,
                "Plan Availability": parse_plan_availability,
                "Summary of Available and Historic Benefits": parse_benefits
            }
            
            for key, func in parsing_functions.items():
                try:
                    result = func(lines)
                    if result:  # Only add non-empty results
                        parsed_entry[key] = result
                except Exception as e:
                    print(f"Error parsing {key} for Annuity {annuity_number}: {str(e)}")
            
            parsed_data.append(parsed_entry)
    
    return parsed_data

    # Parse the annuity data
if __name__ == "__main__":
    import json
    
    # Parse the annuity data
    parsed_annuities = parse_annuity_data('annuity_data.csv')
    
    # Save the parsed data to a JSON file
    output_file = 'parsed_annuities.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_annuities, f, indent=2, ensure_ascii=False)
    
    print(f"Parsed {len(parsed_annuities)} annuities. Results saved to {output_file}")
    

# nolint end