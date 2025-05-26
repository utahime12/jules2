"""
Downloads videos from a given webpage URL.

This script fetches the content of a webpage, parses its HTML to find links 
to video files, and then downloads these videos to a specified directory.

Usage:
    python video_downloader.py <URL> [-o OUTPUT_DIR]

Arguments:
    URL             The URL of the webpage to scan for video links (required).
    -o OUTPUT_DIR, --output OUTPUT_DIR
                    The directory where downloaded videos will be saved. 
                    If not specified, videos are saved in the current working directory. (optional)

Examples:
    1. Download videos from a webpage to the current directory:
       python video_downloader.py https://www.example.com/some_video_page.html

    2. Download videos to a specific directory:
       python video_downloader.py https://www.example.com/another_video_page.html -o /path/to/your/download_folder

Dependencies:
    - requests (for making HTTP requests)
    - BeautifulSoup4 (for parsing HTML)

To install dependencies:
    pip install requests beautifulsoup4
"""
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import sys

def main():
    """
    Parses command-line arguments to get a URL, fetches its content,
    parses HTML to find video links, and downloads them to a specified path.
    """
    parser = argparse.ArgumentParser(description="Fetches content from a given URL, finds video links, and downloads them.")
    parser.add_argument("url", help="The URL of the page to scan for video links.")
    parser.add_argument('-o', '--output', help="Directory to save downloaded videos", default='.')
    args = parser.parse_args()
    print(f"The provided URL is: {args.url}")

    output_path = os.path.abspath(args.output)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path, exist_ok=True)
            print(f"Output directory '{output_path}' created.")
        except PermissionError:
            print(f"Error: Permission denied. Could not create output directory '{output_path}'. Please check permissions.")
            sys.exit(1)
        except OSError as e:
            print(f"Error: Could not create output directory '{output_path}': {e}")
            sys.exit(1)
    elif not os.path.isdir(output_path):
        print(f"Error: Output path '{output_path}' exists but is not a directory.")
        sys.exit(1)
    
    print(f"Videos will be saved to: {output_path}")

    try:
        page_response = requests.get(args.url)
        page_response.raise_for_status() 
        print(f"Successfully fetched URL: {args.url}")

        soup = BeautifulSoup(page_response.text, 'html.parser')
        video_urls = []
        video_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.wmv']
        base_url = args.url

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if any(href.lower().endswith(ext) for ext in video_extensions):
                try:
                    abs_url = urljoin(base_url, href)
                    video_urls.append(abs_url)
                except ValueError:
                    print(f"Warning: Could not construct absolute URL for '{href}'. Skipping.")

        for video_tag in soup.find_all('video'):
            if video_tag.has_attr('src'):
                src = video_tag['src']
                if any(src.lower().endswith(ext) for ext in video_extensions) or not os.path.splitext(urlparse(src).path)[1]:
                    try:
                        abs_url = urljoin(base_url, src)
                        video_urls.append(abs_url)
                    except ValueError:
                        print(f"Warning: Could not construct absolute URL for '{src}' in <video> tag. Skipping.")
            
            for source_tag in video_tag.find_all('source', src=True):
                src = source_tag['src']
                if any(src.lower().endswith(ext) for ext in video_extensions) or not os.path.splitext(urlparse(src).path)[1]:
                    try:
                        abs_url = urljoin(base_url, src)
                        video_urls.append(abs_url)
                    except ValueError:
                        print(f"Warning: Could not construct absolute URL for '{src}' in <source> tag. Skipping.")
        
        video_urls = sorted(list(set(video_urls)))

        if video_urls:
            print(f"\nFound {len(video_urls)} potential video link(s).")
            downloaded_count = 0
            generic_file_counter = 1
            for video_url in video_urls:
                base_filename = "" 
                filepath = ""
                try:
                    print(f"Attempting to download: {video_url}")
                    parsed_url = urlparse(video_url)
                    base_filename = os.path.basename(parsed_url.path)
                    
                    if not base_filename or base_filename.endswith('/'):
                        file_ext = '.mp4' 
                        for ext in video_extensions:
                            if video_url.lower().endswith(ext):
                                file_ext = ext
                                break
                        base_filename = f"video_{generic_file_counter}{file_ext}"
                        generic_file_counter += 1
                    else:
                        _ , ext_from_url = os.path.splitext(base_filename)
                        if not ext_from_url or not any(ext_from_url.lower().endswith(vid_ext) for vid_ext in video_extensions) :
                                 base_filename += ".mp4"
                    
                    filepath = os.path.join(output_path, base_filename)

                    video_response = requests.get(video_url, stream=True)
                    video_response.raise_for_status()

                    with open(filepath, 'wb') as f:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Successfully downloaded to {filepath}")
                    downloaded_count += 1
                
                except PermissionError:
                    print(f"Error: Permission denied. Cannot write to '{filepath}'. Please check permissions or try a different download location.")
                except requests.exceptions.HTTPError as e:
                    print(f"Failed to download {video_url}. Status code: {e.response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {video_url}: {e}")
                except IOError as e: 
                    print(f"File error for '{filepath}': {e}")

            if downloaded_count > 0:
                print(f"\nSuccessfully downloaded {downloaded_count} video(s) to '{output_path}'.")
            elif not video_urls: 
                 print("No videos were downloaded.")
            else: 
                 print(f"\nNo videos were successfully downloaded to '{output_path}'.")
        else:
            print("No video URLs found on the page.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch page {args.url}: {e}")
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
