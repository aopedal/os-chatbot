echo
echo Qdrant collections:
curl -s http://localhost:6333/collections | jq '.result.collections[].name'
echo
echo Weaviate classes:
curl -s http://localhost:6444/v1/schema | jq '.classes[].class'
echo