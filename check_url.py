import pandas as pd
import requests
import concurrent.futures

# Load the CSV
df = pd.read_csv('data/full_music_list.csv')

def check_url(index_url_tuple):
    idx, url = index_url_tuple
    if pd.isna(url) or not str(url).startswith('http'):
        return idx, False
    
    try:
        response = requests.get(
            'https://soundcloud.com/oembed',
            params={'url': url, 'format': 'json'},
            timeout=10
        )
        return idx, response.status_code == 200
    except requests.RequestException:
        return idx, False

# Check URLs in parallel to speed up the process
invalid_indices = []
print("Checking URLs, please wait...")

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Pass the index and URL to the checker
    results = executor.map(check_url, df['song_url'].items())
    
    for idx, is_valid in results:
        if not is_valid:
            invalid_indices.append(idx)

# Filter the dataframe to only show invalid entries
invalid_entries = df.loc[invalid_indices]

print(f"\nFound {len(invalid_entries)} invalid or missing URLs:")
print(invalid_entries[['id', 'title', 'artist', 'song_url']].to_string(index=False))

ids_to_remove = invalid_entries['id']
df_cleaned = df[~df['id'].isin(ids_to_remove)]
df_cleaned.to_csv('data/cleaned_music_list_final_finally.csv', index=False)
print(f"Removed {len(df) - len(df_cleaned)} rows. Cleaned CSV saved!")

invalid_entries.to_csv('data/cleaned_music_list.csv', index=False)