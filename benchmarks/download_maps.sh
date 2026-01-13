#!/bin/bash
mkdir -p benchmarks/movingai/dao

# URL for Dragon Age: Origins dataset (ZIP)
URL="https://www.movingai.com/benchmarks/dao/dao-map.zip"

echo "Downloading DAO Dataset..."
# Use curl with location following (-L) and user-agent
curl -L -A "Mozilla/5.0" -o benchmarks/movingai/dao.zip $URL

if [ -f "benchmarks/movingai/dao.zip" ]; then
    echo "Extracting..."
    unzip -o -q benchmarks/movingai/dao.zip -d benchmarks/movingai/dao
    rm benchmarks/movingai/dao.zip
    echo "Done! Maps are in benchmarks/movingai/dao/"
else
    echo "Download failed."
fi
