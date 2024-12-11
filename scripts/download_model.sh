#!/bin/sh

mkdir -p chrome5

REPO_URL="https://raw.githubusercontent.com/yohhaan/topics_classifier/main"

download_file() {
    echo "Downloading $1..."
    output=$(curl -L "$REPO_URL/$1" --create-dirs -o "$1" 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully downloaded $1"
        return 0
    else
        echo "✗ Error downloading $1"
        echo "Curl output:"
        echo "$output"
        return 1
    fi
}

for file in \
    "chrome5/config.json" \
    "chrome5/model-info.pb" \
    "chrome5/model.tflite" \
    "chrome5/override_list.pb.gz" \
    "chrome5/override_list.tsv" \
    "chrome5/taxonomy.tsv" \
    "chrome5/utility_buckets.tsv"
do
    download_file "$file" || exit 1
done

for file in \
    "chrome5/config.json" \
    "chrome5/model.tflite" \
    "chrome5/taxonomy.tsv" \
    "chrome5/override_list.tsv"
do
    if [ ! -f "$file" ]; then
        echo "Error: Essential file $file is missing!"
        exit 1
    fi
done

echo "✓ All files downloaded successfully!" 