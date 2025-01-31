import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
import urllib3
import urllib
# from util import extract_pdf_to_markdown
from docling import DocumentConverter

def download_pdfs_from_arxiv():
    input_folder = 'tweet_collection/arxiv'
    output_folder = 'tweet_collection/arxiv'

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        print(f"Downloading pdfs from arxiv {filename}")
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

def process_from_arxiv_pdf(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = soup.find_all('a', href=True)

    for link in pdf_links:
        if 'pdf' in link['href']:
            pdf_url = link['href']
            pdf_name = os.path.basename(pdf_url)

            # Download the PDF content
            pdf_response = requests.get(urllib.parse.urljoin("https://arxiv.org/", pdf_url))
            pdf_content = pdf_response.content

            # Convert PDF to markdown using DocumentConverter from docling
            converter = DocumentConverter()
            markdown_content = converter.convert(pdf_content).document.export_to_markdown()

            # Save the markdown content to a file
            markdown_path = os.path.join('tweet_collection/arxiv', pdf_name.replace('.pdf', '.md'))
            with open(markdown_path, 'w') as md_file:
                md_file.write(markdown_content)
                print(f'Converted to Markdown: {markdown_path}')
# Call the function to execute the download
# download_pdfs_from_arxiv()

