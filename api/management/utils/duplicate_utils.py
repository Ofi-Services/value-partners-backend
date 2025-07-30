from django.core.management.base import BaseCommand
import time 
import csv
import os
from django.conf import settings
from rapidfuzz import fuzz
from rapidfuzz.distance import DamerauLevenshtein, JaroWinkler
import csv
from api.models import Invoice, Case
from django.utils.dateparse import parse_datetime
from django.conf import settings
import os
from decimal import Decimal
import random
from datetime import datetime, timedelta
from ..constants import PATTERN_CHOICES


def normalize( s: str) -> str:
    return s.replace(' ', '').replace('-', '').replace('/', '').replace('.', '').lower()

# Calculates the Damerau Levenshtein distance between two strings. Useful for common typos in long strings.
def dl_distance( s1: str, s2: str) -> float:
    return DamerauLevenshtein.normalized_similarity(normalize(s1), normalize(s2))

# Calculates the Jaro Winkler distance between two strings. Useful for common typos in short strings.
def jaro_winkler_distance( s1: str, s2: str):
    return JaroWinkler.normalized_similarity(normalize(s1), normalize(s2))

def jaccard_similarity( s1: str, s2:str):
    s1 = set(normalize(s1))
    s2 = set(normalize(s2))
    return len(s1.intersection(s2)) / len(s1.union(s2))

def indel_distance( s1: str, s2: str):
    return fuzz.ratio(normalize(s1), normalize(s2))/100

def compare_metrics( s1: str, s2: str):
    start_time = time.time()
    print(indel_distance(s1,s2), 'indel distance took ', time.time()-start_time, ' seconds')

    start_time = time.time()
    print(dl_distance(s1, s2), 'Damerau Levenshtein distance took ', time.time()-start_time, ' seconds')

    start_time = time.time()
    print(jaro_winkler_distance(s1, s2), 'Jaro Winkler distance took ', time.time()-start_time, ' seconds')

    start_time = time.time()
    print(jaccard_similarity(s1, s2), 'Jaccard similarity took ', time.time()-start_time, ' seconds')

def stringify( dict):
    return ' '.join([normalize(str(dict[key])) for key in dict])

def similarity( similarity: int) -> str:

    if similarity == 1:
        return 'EXACT'
    elif similarity > 0.95:
        return 'HIGH'
    elif similarity > 0.9:
        return 'MEDIUM'
    elif similarity > 0.8:
        return 'LOW'
    else:
        return 'NONE'

def find_accuracies( d1, d2):
    accuracy_dict = {}
    for key in d1: 
        accuracy_dl = dl_distance(d1[key], d2[key])
        accuracy_jw = jaro_winkler_distance(d1[key], d2[key])
        accuracy_dict[key] = max(accuracy_dl, accuracy_jw)
    return accuracy_dict

def find_patterns( dic):
    patterns = []
    for key in dic:
        if dic[key] > 0.9 and dic[key] < 1:
            patterns.append('similar ' + key)
    return patterns

def test_invoices( invoice1, invoice2):
    
    


    str1 = stringify(invoice1)
    str2 = stringify(invoice2)

    similarity = indel_distance(str1, str2)
    print('similarity: ', similarity,' ', similarity(similarity))

    accuracies = find_accuracies(invoice1, invoice2)
    print(accuracies)
    patterns = find_patterns(accuracies)
    print(patterns)


def get_data(self):
            # Path to the input CSV file
    input_csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'OutputData.csv')
    
    

    # Read data from the input CSV file
    with open(input_csv_file_path, newline='', encoding='utf-8-sig') as input_csvfile:
        reader = csv.DictReader(input_csvfile)
        data = [row for row in reader]
    return data

def get_invoice( row):
    return {
        "reference": row['reference'],
        "date": row['Date'],
        "value": row['value'],
        "vendor": row['Vendor'],
        "region": row['Region'],
        "description": row['Description'],
        "payment_method": row['Payment Method'],
        "special_instructions": row['Special Intructions']
    }

def find_most_similar( invoice):
    data = get_data()
    similarities = []
    for row in data:
        invoice1 = get_invoice(row)
        str1 = stringify(invoice)
        str2 = stringify(invoice1)
        similarity = indel_distance(str1, str2)
        similarities.append((similarity, row))
    similarities.sort(key=lambda x: x[0], reverse=True)
    return similarities[0]

def find_most_similar_data( invoice):
    most_similar = get_invoice(find_most_similar(invoice)[1])
    print('Most similar invoice: ', most_similar['reference'])
    test_invoices(invoice, most_similar)

def similar_text( text):
    """
    Return a similar text based on the input text.
    """
    case = random.choice([0, 1, 2])
    if case == 0:
        return delete_random_char(text)
    elif case == 1:
        return duplicate_random_char(text)
    else:
        return replace_random_char(text)

def introduce_spelling_mistake( name):
        mistake_functions = [
            switch_random_chars,
            add_random_char,
            remove_random_char,
            change_random_char,
            duplicate_random_char
        ]
        for i in range(random.randint(0, 2)): 
            name = random.choice(mistake_functions)(name)
        return name

def switch_random_chars( name):
    if len(name) > 1:
        index = random.randint(0, len(name) - 2)
        return name[:index] + name[index + 1] + name[index] + name[index + 2:]
    return name

def add_random_char( name):
    index = random.randint(0, len(name))
    return name[:index] + random.choice("abcdefghijklmnopqrstuvwxyz") + name[index:]

def remove_random_char(name):
    if len(name) > 1:
        index = random.randint(0, len(name) - 1)
        return name[:index] + name[index + 1:]

def change_random_char( name):
    if len(name) > 1:
        index = random.randint(0, len(name) - 1)
        return name[:index] + random.choice("abcdefghijklmnopqrstuvwxyz") + name[index + 1:]

def duplicate_random_char( name):
    if len(name) > 1:
        index = random.randint(0, len(name) - 1)
        return name[:index] + name[index] + name[index] + name[index + 1:]
        
def get_accuracy( confidence, pattern):
    """
    Get the accuracy based on the confidence level.
    """
    if pattern == 'Exact Match':
        return 100
    elif confidence == 'High':
        return random.randint(95, 99)
    elif confidence == 'Medium':
        return random.randint(90, 94)
    elif confidence == 'Low':
        return random.randint(80, 89)
    else:
        return random.randint(0, 49)
    

def create_invoice( date: datetime, case: Case, quantity: int, unit_price: float):
    """
    Handle the command to add data to the database from the CSV file.
    """
    item_quantity = quantity
    value = unit_price * item_quantity

    accuracy = random.randint(80, 100)
    confidence = 'High' if accuracy >= 95 else 'Medium' if accuracy >= 90 else 'Low'
    pattern = random.choice(PATTERN_CHOICES)
    invoice = Invoice(
        date=date,
        unit_price=unit_price,
        quantity=item_quantity,
        value=value,
        case=case,
        pattern=pattern,
        open=random.choice([True, False]),
        group_id=str(random.randint(1, 100)),
        confidence=confidence,
        description='No description',
        payment_method=random.choice(['Credit Card', 'Bank Transfer', 'Cash']),
        pay_date=datetime.now(),
        special_instructions=random.choice(['No special instructions', 'Handle with care', 'Urgent delivery', 'Payment due in 30 days']),
        accuracy=accuracy,
    )
    invoice.save()

    
    print("Invoice,  ", invoice.id," created successfully.")
    

