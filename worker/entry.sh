#!/bin/bash

set -e

DB_PATH="/human_viral_db"

DB_DOWNLOAD="https://zenodo.org/records/18881223/files/human_viral_db.tar.gz?download=1"

if [ -f "$DB_PATH/hash.k2d" ]; then
    echo "Kraken2 db already installed.."
else
    echo "Downloading Human/Viral db..."
    # wget quiet met progress bar out naar tmp dir
    wget -q --show-progress -O /tmp/human_viral_db.tar.gz "$DB_DOWNLOAD"

    echo "Extracting database..."
    # tar extract met copy naar db path
    tar -xzf /tmp/human_viral_db.tar.gz -C $DB_PATH

    echo "Removing archive..."
    rm /tmp/human_viral_db.tar.gz

    echo "Human/Viral db installed successfully."
fi

echo "Starting watcher process..."


# in dockerfile staat: ENTRYPOINT ["bash", "entry.sh"] en daarna CMD ["python", "tasks.py"]
# docker maakt hier bash entry.sh python tasks.py van
# dus dan is "python tasks.py" de args voor entry.sh
# en met exec "$@" worden die args geexecute

exec "$@"