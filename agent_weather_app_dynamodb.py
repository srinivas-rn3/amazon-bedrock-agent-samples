import json
import requests
import boto3
import time

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('WeatherCache')

def lambda_handler(event, context):
    # ✅ Get city from structured Bedrock Agent input
    city = event.get('parameters', {}).get('city', '').lower().strip()

    if not city:
        return {"error": "City parameter is missing."}

    today = time.strftime('%Y-%m-%d')
    cache_key = f"{city}_{today}"

    try:
        # ✅ Check cache
        response = table.get_item(Key={'location_date': cache_key})
        if 'Item' in response:
            print("✅ Cache hit")
            cached = response['Item']
            body = {
                'city': city,
                'temperature_celsius': cached['temperature'],
                'feels_like_celsius': cached['feels_like'],
                'description': cached['description']
            }
        else:
            print("⏳ Cache miss, calling API")
            # ✅ Fetch from API
            weather_response = requests.get(f'https://wttr.in/{city}?format=j1')
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            current = weather_data['current_condition'][0]

            temp_c = current['temp_C']
            feels_like_c = current['FeelsLikeC']
            description = current['weatherDesc'][0]['value']

            # ✅ Save to cache
            ttl = int(time.time()) + 1800  # 30 minutes
            table.put_item(Item={
                'location_date': cache_key,
                'temperature': temp_c,
                'feels_like': feels_like_c,
                'description': description,
                'ttl': ttl
            })

            body = {
                'city': city,
                'temperature_celsius': temp_c,
                'feels_like_celsius': feels_like_c,
                'description': description
            }

    except Exception as e:
        print(f"❌ Error with cache/API: {str(e)}")
        return {"error": f"Could not fetch weather for {city}. Error: {str(e)}"}

    # ✅ Format response for Bedrock Agent
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup'),
            'apiPath': f"/weather/{city}",
            'httpMethod': event.get('httpMethod', 'GET'),
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(body)
                }
            }
        }
    }
