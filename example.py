import json
import os
import urllib.error
import urllib.request
from urllib.parse import quote

api_key = "<Insert your API key here>"
base_api_url = "https://api.foodsteps.earth/v1"

if "API_KEY" in os.environ:
    api_key = os.environ["API_KEY"]

if "API_URL" in os.environ:
    base_api_url = os.environ["API_URL"]


def make_request(*, method, path, data=None):
    url = f"{base_api_url}{path}"
    headers = {"X-Api-Key": api_key}

    print(f"Sending {method} request to {url}")
    if data is not None:
        print("Request data:", json.dumps(data, indent=4))
        data = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(method=method, url=url, headers=headers)
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, data=data) as response:
            response_data = json.load(response)
            print("Response data:", json.dumps(response_data, indent=4))
            return response_data
    except urllib.error.HTTPError as error:
        print(error.code, error.read().decode())
        raise


print("Creating a new product")
response_data = make_request(
    method="POST",
    path="/products/",
    data={
        "products": [
            {
                "name": "Green Salad",
                "externalId": "product-1",
                "ingredients": [
                    {
                        "name": "Lettuce",
                        "externalId": "supplier-reference-1",
                        "quantity": 1.5,
                        "unit": "kg",
                    },
                ],
                "numServings": 10,
            }
        ]
    },
)


print()
print("Assigning a tag to the product")
response_data = make_request(
    method="POST",
    path="/tag-product-actions/",
    data={
        "actions": [
            {
                "productExternalId": "product-1",
                "action": "assign",
                "tag": "starters",
            },
        ],
    },
)


print()
print("Adding a second ingredient to the product")
response_data = make_request(
    method="POST",
    path="/products/",
    data={
        "products": [
            {
                "name": "Salad",
                "externalId": "product-1",
                "ingredients": [
                    {
                        "name": "Lettuce",
                        "externalId": "supplier-reference-1",
                        "quantity": 1.5,
                        "unit": "kg",
                    },
                    {
                        "name": "Cucumber",
                        "externalId": "supplier-reference-2",
                        "quantity": 20,
                        "unit": "each",
                    },
                ],
                "numServings": 10,
            }
        ]
    },
)


print()
print("Changing the product's tags")
response_data = make_request(
    method="POST",
    path="/tag-product-actions/",
    data={
        "actions": [
            {
                "productExternalId": "product-1",
                "action": "unassign",
                "tag": "starters",
            },
            {
                "productExternalId": "product-1",
                "action": "assign",
                "tag": "salads",
            },
        ]
    },
)


print()
print("Fetching all products")
products = []
page = 1
while True:
    response_data = make_request(method="GET", path=f"/products/?page={page}")

    for product in response_data["products"]:
        products.append(product)
        print()
        print(product["name"])
        for ingredient in product["ingredients"]:
            print("   ", ingredient["quantity"], ingredient["unit"], ingredient["name"])

    if response_data["hasNextPage"]:
        page = page + 1
    else:
        break


product_by_id = {product["externalId"]: product for product in products}


print()
print("Fetching impacts for the first 50 products")
ids_to_query = [product["externalId"] for product in products[:50]]
response_data = make_request(
    method="GET",
    path=(
        "/current-impacts/?"
        + "&".join(f"productExternalIds={quote(id)}" for id in ids_to_query)
    ),
)

print()
for impact in response_data["impacts"]:
    product_id = impact["productExternalId"]
    product_name = product_by_id[product_id]["name"]
    status = impact["status"]

    output_line = f"{product_name} - {status}"
    if status == "complete":
        ghg_per_kg = impact["impactGhgPerKg"]
        output_line = output_line + f" - {ghg_per_kg:.2f} kg CO2e/kg"

    print(output_line)
