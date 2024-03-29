from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
import requests
from dotenv import load_dotenv
import os


class LinkRecipeResource(Resource):
    def post(self):
        try:
            # parameter json
            data = request.get_json()

            user_id = data.get('userId')
            recipe_name = data.get('recipeName')
        
            # Load environment variables from .env file
            load_dotenv()

            # Access the API key from the environment variable
            api_key = os.getenv("API_KEY_SEARCH")

            # Check if API key is available
            if not api_key:
                raise Exception("API key not found in the environment variables.")
            
            # Construct the URL using the API key
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=e21c2f9ab0e304589&q={recipe_name}"
            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            # Check the status code
            status_code = response.status_code

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
               
                search_results = []

                # Parse JSON response
                response_json = response.json()

                # 
                db = firestore.client()
                
                collection_ref = db.collection('favorite')
                # docs = collection_ref.stream()

                # Construct the query
                query = collection_ref.where('recipe_name', '==', recipe_name).where('user_id', '==', user_id)
                docs = query.stream()
                dataFav = []
                for doc in docs:
                    doc_data = doc.to_dict()
                    dataFav.append(doc_data)

                

                # Create a batch object
                batch = db.batch()

                 # Check if the 'items' field exists in the response
                if 'items' in response_json:

                    for item in response_json['items']:
                        # Access and print relevant information
                        title = item.get('title', '')

                        # Check if the title is not present in dataFav
                        if all(doc.get('title', '') != title for doc in dataFav):
                            link = item.get('link', '')
                            snippet = item.get('snippet', '')
                            
                            # Check if the link is an HTTP link before inserting
                            if link.startswith('https://'):
                                # Access the 'pagemap' dictionary within the item
                                pagemap = item.get('pagemap', {})

                                # Access the 'thumbnail' list within the pagemap
                                cse_image = pagemap.get('cse_image', [])

                                # Initialize img variable
                                img = ''

                                # Iterate through each thumbnail in the list
                                for thumbnail in cse_image:
                                    # Access the 'src' value within the thumbnail
                                    img = thumbnail.get('src', '')

                                favorite = {
                                    "status": 'N',
                                    'img': img,
                                    'recipe_name': recipe_name,
                                    'title': title,
                                    'url': link,
                                    'user_id': user_id,
                                    # Add more fields as needed
                                }

                                # Reference to the 'favorite' collection
                                collection_ref = db.collection('favorite')

                                # Create a new document reference in the batch
                                document_ref = collection_ref.document()

                                # Set data for the document in the batch
                                batch.set(document_ref, favorite)

                    # Commit the batch
                    batch.commit()

                db = firestore.client()
                collection_ref = db.collection('favorite')

                # Construct the query using filter keyword argument
                query = collection_ref.where('recipe_name', '==', recipe_name).where('user_id', '==', user_id)

                # Alternatively, you can use filter keyword argument directly
                # query = collection_ref.where(recipe_name='recipe_name', user_id='user_id')

                docs = query.stream()
                dataResult = []

                for doc in docs:
                    doc_data = doc.to_dict()
                    doc_id = doc.id  # Get the document_id
                    # Append the document_id along with the data to the 'data' list
                    dataResult.append({"document_id": doc_id, "data": doc_data})

                response = {}

                if dataResult:
                    transformed_data = []

                    for item in dataResult:
                        # print(item)
                        value = {
                            "favId": item.get("document_id"),
                            "img": item["data"].get("img"),
                            "title": item["data"].get("title"),
                            "url": item["data"].get("url"),
                            "isFavorite": item["data"].get("status"),
                            "userId": item["data"].get("user_id")
                        }
                        transformed_data.append(value)

                    response = {
                        "status": "1",
                        "message": "Data retrieved successfully",
                        "data": transformed_data
                    }
                else:
                    # If no data is present, return a response with a message
                    response = {
                        "status": "0",
                        "message": "No data available",
                        "data": []
                    }

                return response, 200


        
            else:
                
                print(f"Error: {status_code}")
                return status_code
     
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500

