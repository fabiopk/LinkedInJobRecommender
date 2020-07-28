import pandas as pd
import re
from datetime import datetime, timedelta
import json

all_columns_dict = {
    'Seniority level': [
        'Associate',
        'Director',
        'Entry level',
        'Executive',
        'Internship',
        'Mid-Senior level',
        'Not Applicable'],
    'Employment type': ['Contract',
                        'Full-time',
                        'Internship',
                        'Other',
                        'Part-time',
                        'Temporary'],
    'Job function': ['Engineering', 'Analyst', 'Product Management',
                     'Information Technology', 'Strategy/Planning', 'Other',
                     'Consulting', 'Marketing', 'Business Development', 'Management',
                     'Education', 'Project Management', 'Research', 'Legal', 'Design',
                     'Finance', 'Administrative', 'Science', 'Quality Assurance',
                     'Accounting/Auditing', 'Human Resources', 'Sales',
                     'Production', 'Health Care Provider', 'Supply Chain',
                     'General Business', 'Customer Service', 'Distribution'],
    'Industries': ['Information Technology', 'Internet', 'Science',
                   'Information Technology and Services', 'Real Estate',
                   'Financial Services', 'Marketing and Advertising', 'Engineering',
                   'Supply Chain', 'Information Services',
                   'Health, Wellness and Fitness', 'Computer Software',
                   'Education Management', 'Chemicals', 'Sales', 'Strategy/Planning',
                   'Analyst', 'Training', 'Product Management',
                   'Management Consulting', 'Staffing and Recruiting', 'Advertising',
                   'Paper & Forest Products', 'Market Research',
                   'Transportation/Trucking/Railroad', 'Art/Creative',
                   'Telecommunications', 'Pharmaceuticals', 'Higher Education',
                   'Research', 'Consulting', 'Writing/Editing',
                   'Hospital & Health Care', 'Manufacturing', 'General Business',
                   'Banking', 'Electrical/Electronic Manufacturing',
                   'Food & Beverages', 'Retail', 'Marketing', 'Public Relations',
                   'Apparel & Fashion', 'Computer Hardware', 'Design',
                   'Medical Devices', 'Finance', 'Logistics and Supply Chain',
                   'Business Development', 'Customer Service', 'Accounting',
                   'Construction', 'Distribution', 'Food Production', 'Automotive',
                   'Leisure, Travel & Tourism', 'Management', 'Quality Assurance',
                   'Health Care Provider', 'Environmental Services',
                   'Human Resources', 'Mechanical or Industrial Engineering',
                   'Biotechnology', 'Consumer Electronics', 'Accounting/Auditing',
                   'Oil & Energy', 'Insurance', 'Administrative', 'Online Media',
                   'Farming', 'Cosmetics', 'Hospitality', 'Restaurants',
                   'Consumer Goods', 'Other', 'Utilities', 'Photography',
                   'Nonprofit Organization Management', 'Renewables & Environment',
                   'Supermarkets', 'Project Management', 'Entertainment', 'Music',
                   'Government Administration', 'Packaging and Containers',
                   'Civil Engineering', 'Media Production']}


def convert_datetime(datetime_ago):
    matches = re.search(
        r"(\d+ weeks?,? )?(\d+ days?,? )?(\d+ months?,? )?(\d+ hours?,? )?(\d+ mins?,? )?(\d+ secs? )?ago", datetime_ago)

    if not matches:
        return 0

    date_pieces = {'month': 0, 'week': 0,
                   'day': 0, 'hour': 0, 'min': 0, 'sec': 0}

    for i in range(1, len(date_pieces) + 1):
        if matches.group(i):
            value_unit = matches.group(i).rstrip(', ')
            if len(value_unit.split()) == 2:
                value, unit = value_unit.split()
                date_pieces[unit.rstrip('s')] = int(value)

    date_pieces['week'] += 4 * date_pieces['month']

    return timedelta(
        weeks=date_pieces['week'],
        days=date_pieces['day'],
        hours=date_pieces['hour'],
        minutes=date_pieces['min'],
        seconds=date_pieces['sec']
    )


def get_portuguese_stop_words():
    with open('../portuguese_stop_words.json') as stop_words:
        return json.load(stop_words)


def get_ohe_features(df, feature):

    ohe_features = pd.get_dummies(df[feature])

    # Get missing columns in the training test
    missing_cols = set(all_columns_dict[feature]) - set(ohe_features.columns)

    # Add a missing column in test set with default value equal to 0
    for c in missing_cols:
        ohe_features[c] = 0

    # Ensure the order of column in the test set is in the same order than in train set
    ohe_features = ohe_features[all_columns_dict[feature]]

    return ohe_features
