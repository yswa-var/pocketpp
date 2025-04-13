#!/usr/bin/env python3
"""
Script to download required NLTK resources.
"""
import nltk
import sys

def download_nltk_resources():
    """Download required NLTK resources."""
    print("Downloading NLTK resources...")
    
    # Download punkt (regular tokenizer)
    nltk.download('punkt')
    
    # Try to download punkt_tab
    try:
        nltk.download('punkt_tab')
        print("Successfully downloaded punkt_tab")
    except Exception as e:
        print(f"Error downloading punkt_tab: {e}")
        
    # Additional resources that might be needed
    nltk.download('stopwords')
    
    print("NLTK resource download completed.")

if __name__ == "__main__":
    download_nltk_resources()

