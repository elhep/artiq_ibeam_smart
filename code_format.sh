#!/bin/sh

echo "Python code formatting..."
find -type f -name "*.py" | xargs black -q
find -type f -name "*.py" | xargs isort
echo "Done"
