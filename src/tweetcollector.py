import os
import sys
import logging
from pathlib import Path
from utils import *
from extractors.twitter import TweetMetadataCollector
from extractors.arxiv import download_pdfs_from_arxiv
from extractors.docintelligence import DocumentExtractor
from extractors.github import extract_github_readme

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tweet_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def tweets_meta_collector(recent_k=50):
    """
    Main execution method for tweet metadata collection
    """
    # Create data and output directories if they don't exist
    Path('data').mkdir(exist_ok=True)
    Path('tweet_collection').mkdir(exist_ok=True)

    # Find the most recent Twitter Bookmarks CSV
    try:
        csv_files = list(Path('data').glob('twitter-Bookmarks-*.csv'))
        
        if not csv_files:
            logger.error("No Twitter Bookmarks CSV files found in 'data/' directory.")
            print("Error: Please place your Twitter Bookmarks CSV in the 'data/' directory.")
            print("Filename should start with 'twitter-Bookmarks-'")
            sys.exit(1)
        
        # Select the most recent CSV file
        csv_path = max(csv_files, key=os.path.getctime)
        logger.info(f"Processing CSV file: {csv_path}")

    except Exception as e:
        logger.error(f"Error finding CSV file: {e}")
        sys.exit(1)

    try:
        # Read tweet data
        tweets_df = read_tweet_data(csv_path,recent_k)
        
        # Initialize metadata collector
        collector = TweetMetadataCollector()
        
        # Process tweets
        processed_tweets = collector.process_tweet_collection(tweets_df)
        
        # Print summary
        print(f"Processed {len(processed_tweets)} tweets")
        print(f"Metadata saved to {collector.dirs['metadata'] / 'processed_tweets.json'}")
        print(f"Detailed logs in tweet_collector.log")
    
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def read_tweet_metadata(tweet_id):
    file_path="tweet_collection/metadata/comprehensive_metadata.json"
    df=pd.read_json(file_path)

if __name__ == "__main__":
    extractor = DocumentExtractor()
    
    # Process all supported document types
    
    tweets_meta_collector(recent_k=40)
    download_pdfs_from_arxiv()
    extract_github_readme()

    extractor.process_documents()
