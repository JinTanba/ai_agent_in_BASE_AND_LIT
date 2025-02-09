#!/bin/bash

# Start main.py (port 8001)
python main.py &

# Start main2.py (port 8000)
python main2.py &

# Start midjarny server (port 3000)
cd midjarny && npm run dev &

# Keep script running
wait