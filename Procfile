// web: gunicorn app:server
// worker: python data_app.py

web: python app.py && data_app.py & wait -n 