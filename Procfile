// web: gunicorn app:server
// worker: python data_app.py

web: trap '' SIGTERM; gunicorn app:server && python data_app.py & wait -n; kill -SIGTERM -$$; wait