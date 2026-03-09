"""Entry point – run with: python run.py"""
from app import app

if __name__ == '__main__':
    print("🌶️  StreetByte is starting up...")
    print("📍 Open your browser at: http://localhost:5000")
    # Pre-load data so the first request is instant
    from ml.recommender import get_dataframe
    get_dataframe()
    print("✅ Dataset loaded and scored successfully!")
    app.run(debug=False, host='0.0.0.0', port=5000)
