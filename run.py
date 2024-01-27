# run.py
from flask import Flask
from flask_restful import Api
from app.core.firebase import initialize_firebase_app
from app.api.v1.routes.resources.alpha_resource import AlphaResource
from app.api.v1.routes.resources.ingredient_resource import IngredientResource, IngredientResourceWithCategory
from app.api.v1.routes.resources.favorite_resource import AddFavoriteResource, FavoriteResourceByUser
from app.api.v1.routes.resources.recipe_resource import GenerateRecipeFromIngredients
from app.api.v1.routes.resources.google_resource import SearchWithRecipe
import aws_lambda_wsgi

app = Flask(__name__)
api = Api(app)

# Use initialize_firebase_app()
initialize_firebase_app()

api.add_resource(AlphaResource, '/api/v1/alpha/<string:type>')
api.add_resource(IngredientResource, '/api/v1/ingredient/')
api.add_resource(IngredientResourceWithCategory, '/api/v1/ingredient/<string:category>')
api.add_resource(AddFavoriteResource, '/api/v1/favorite')
api.add_resource(FavoriteResourceByUser, '/api/v1/favorite/<string:user_id>')
api.add_resource(GenerateRecipeFromIngredients, '/api/v1/GenerateRecipe/')
api.add_resource(SearchWithRecipe, '/api/v1/search/<string:recipeName>')

# AWS Lambda handler
def lambda_handler(event, context):
    try:
        import aws_lambda_wsgi
        return aws_lambda_wsgi.response(app, event, context)
    except ImportError:
        pass

# Run the application locally if not running on AWS Lambda
if __name__ == '__main__':
    app.run(debug=True)