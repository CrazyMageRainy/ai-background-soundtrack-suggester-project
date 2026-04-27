import csv
import time
from ddgs import DDGS

input_file = "data/removed_music_list.csv"
output_file = "data/fixed_music_list.csv"

def fix_soundcloud_urls(infile, outfile):
    with open(infile, 'r', encoding='utf-8') as f_in, \
         open(outfile, 'w', newline='', encoding='utf-8') as f_out:

        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
        writer.writeheader()

        with DDGS() as ddgs:
            for row in reader:
                artist = row['artist']
                title = row['title']
                query = f'soundcloud {artist} {title}'
                print(f"Searching: {artist} - {title}...")

                try:
                    results = list(ddgs.text(query, max_results=5))
                    sc_results = [r for r in results if "soundcloud.com" in r['href']]

                    if sc_results:
                        row['song_url'] = sc_results[0]['href']
                        print(f"  -> Found: {sc_results[0]['href']}")
                    else:
                        row['song_url'] = "NOT FOUND"
                        print("  -> Not found on SoundCloud.")
                except Exception as e:
                    print(f"  -> Error: {e}")
                    row['song_url'] = "ERROR"

                writer.writerow(row)
                time.sleep(2)

if __name__ == "__main__":
    fix_soundcloud_urls(input_file, output_file)
    print("Done! Results saved to", output_file)
