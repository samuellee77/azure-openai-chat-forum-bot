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

echo 'Creating python virtual environment "scripts/.venv"'
python3 -m venv scripts/.venv

echo 'Installing dependencies from "requirements.txt" into virtual environment'
./scripts/.venv/bin/python -m pip install -r scripts/requirements.txt

echo 'Running "prepdocs.py"'
./scripts/.venv/bin/python ./scripts/prepdocs.py './data/*' --searchservice "$AZURE_SEARCH_SERVICE" --openaiservice "$AZURE_OPENAI_SERVICE" --openaideployment "$AZURE_OPENAI_EMB_DEPLOYMENT" --index "$AZURE_SEARCH_INDEX" --formrecognizerservice "$AZURE_FORMRECOGNIZER_SERVICE" --tenantid "$AZURE_TENANT_ID" -v