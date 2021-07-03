echo "[INFO] ***Pull from Github***"
git pull

echo "[INFO] ***Start scraping***"
python3 lib_py/scraping.py

echo "[INFO] ***Update DWH***"
python3 lib_py/dwh.py

echo "[INFO] ***Commit to Github***"
git add data-lake
git commit -a -m "Run daily scraper"
git push