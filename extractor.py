from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime

def find_element_by_partial_class(container, element_type, partial_class):
    """
    Helper function to find elements with class names starting with the given prefix
    """
    elements = container.find_all(element_type, class_=lambda x: x and x.startswith(partial_class))
    return elements[0] if elements else None

def parse_reviews_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    reviews_data = []
    
    # Find all review containers - looking for classes starting with 'reviewContent'
    reviews = soup.find_all(lambda tag: tag.get('class') and 
                          any(cls.startswith('reviewContent') for cls in tag.get('class')))
    
    for review in reviews:
        # Get the parent container that holds all review information
        review_container = review.parent
        
        # Extract review title - finding class starting with 'reviewTitle'
        title = find_element_by_partial_class(review_container, 'div', 'reviewTitle')
        title_text = title.get_text(strip=True) if title else ''
        
        # Extract reviewer info - finding class starting with 'reviewerInfo'
        reviewer_info = find_element_by_partial_class(review_container, 'div', 'reviewerInfo')
        if reviewer_info:
            # Find author - class starting with 'author'
            author = find_element_by_partial_class(reviewer_info, 'span', 'author')
            author_name = author.find_all('span')[-1].get_text(strip=True) if author else ''
            
            # Find date - class starting with 'locationAndTime'
            date_span = find_element_by_partial_class(reviewer_info, 'span', 'locationAndTime')
            date_str = date_span.get('data-date') if date_span else ''
            formatted_date = datetime.fromisoformat(date_str).strftime('%Y-%m-%d') if date_str else ''
        else:
            author_name = ''
            formatted_date = ''
        
        # Extract review content
        review_text = review.get_text(strip=True)
        
        # Extract syndication source - class starting with 'syndicationSource'
        syndication = find_element_by_partial_class(review_container, 'p', 'syndicationSource')
        source = syndication.get_text(strip=True) if syndication else ''
        
        # Check if it's a promotional review
        is_promotional = '[This review was collected as part of a promotion.]' in review_text
        clean_review = review_text.replace('[This review was collected as part of a promotion.]', '').strip()
        
        reviews_data.append({
            'title': title_text,
            'author': author_name,
            'date': formatted_date,
            'review_text': clean_review,
            'is_promotional': is_promotional,
            'source': source
        })
    
    return reviews_data

def save_to_csv(reviews_data, output_file='reviews.csv'):
    if not reviews_data:
        print("No reviews found!")
        return
        
    fieldnames = ['title', 'author', 'date', 'review_text', 'is_promotional', 'source']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews_data)
        print(f"Successfully saved {len(reviews_data)} reviews to {output_file}")

# Example usage
html_file = "/home/sravanth/Documents/axion_ray/bestbuy_reviews.html"
with open(html_file, 'r', encoding='utf-8') as file:
    html_content = file.read()

reviews_data = parse_reviews_html(html_content)
print(f"Found {len(reviews_data)} reviews")
save_to_csv(reviews_data)