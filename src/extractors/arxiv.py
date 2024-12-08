import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
import urllib3
import urllib

def download_pdfs_from_arxiv():
    input_folder = 'tweet_collection/arxiv'
    output_folder = 'tweet_collection/arxiv/pdfs'

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'r') as file:
                soup = BeautifulSoup(file, 'html.parser')
                pdf_links = soup.find_all('a', href=True)

                for link in pdf_links:
                    if 'pdf' in link['href']:
                        pdf_url = link['href']
                        pdf_name = os.path.basename(pdf_url)
                        pdf_path = os.path.join(output_folder, filename.replace(".html",".pdf"))

                        # Download the PDF
                        response = requests.get(urllib.parse.urljoin("https://arxiv.org/",pdf_url))
                        with open(pdf_path, 'wb') as pdf_file:
                            pdf_file.write(response.content)
                            print(f'Downloaded: {pdf_name}')

# Call the function to execute the download
download_pdfs_from_arxiv()

