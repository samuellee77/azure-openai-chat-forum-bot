#!/bin/sh

echo ""
echo "Loading azd .env file from current environment"
echo ""

while IFS='=' read -r key value; do
    value=$(echo "$value" | sed 's/^"//' | sed 's/"$//')
    export "$key=$value"
done <<EOF
$(azd env get-values)
EOF

echo 'Running "prepdocs.py"'
python ./scripts/prepdocs.py './data/*.md' --storageaccount "$AZURE_STORAGE_ACCOUNT" --container "$AZURE_STORAGE_CONTAINER" --storagekey "$AZURE_STORAGE_KEY" --searchservice "$AZURE_SEARCH_SERVICE" --openaiservice "$AZURE_OPENAI_SERVICE" --index "$AZURE_SEARCH_INDEX" --tenantid "$AZURE_TENANT_ID" --remove_image --remove_href -v