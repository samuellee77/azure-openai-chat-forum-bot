#!/bin/sh

echo 'Running "prepdocs.py"'
python ./prepdocs.py '../data/*.md' --storageaccount "$AZURE_STORAGE_ACCOUNT" --container "$AZURE_STORAGE_CONTAINER" --storagekey "$AZURE_STORAGE_KEY" --searchservice "$AZURE_SEARCH_SERVICE" --searchkey "$AZURE_SEARCH_KEY" --index "$AZURE_SEARCH_INDEX" --remove_image --remove_href -v