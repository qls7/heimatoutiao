from flask import Blueprint
from flask_restful import Api, Resource

from utils.output import output_json

search_bp = Blueprint('search', __name__)

search_api = Api(search_bp)

search_api.representation('application/json')(output_json)