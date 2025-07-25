import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.skin_zone_agents import skin_zone_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'skin-zone-journal-secret-key-2024'

# Enable CORS for all routes
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Import all models to ensure they're registered
from src.models.ingredient import Ingredient, Formulation, FormulationIngredient, SafetyAssessment, ClinicalStudy
from src.models.agents import Agent, AgentAction
from src.models.seven_agents import SevenAgentSystem, WorkflowTask

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(skin_zone_bp, url_prefix='/api/skin-zone')

# Import and register the seven agents blueprint
from src.routes.seven_agents_api import seven_agents_bp
app.register_blueprint(seven_agents_bp)

with app.app_context():
    db.create_all()
    
    # Initialize sample data if database is empty
    try:
        if Agent.query.count() == 0:
            from src.routes.skin_zone_agents import get_or_create_agents
            get_or_create_agents()
    except Exception as e:
        print(f"Warning: Could not initialize sample data: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
