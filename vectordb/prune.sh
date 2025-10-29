for c in $(curl -s http://localhost:6333/collections | jq -r '.result.collections[].name'); do
  echo "Deleting collection: $c"
  curl -X DELETE "http://localhost:6333/collections/$c"
done

for c in $(curl -s http://localhost:6444/v1/schema | jq -r '.classes[].class'); do
  echo "Deleting class: $c"
  curl -X DELETE "http://localhost:6444/v1/schema/$c"
done