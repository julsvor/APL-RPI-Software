FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install .

# CMD ["python", "your_project_entry_point.py"]
