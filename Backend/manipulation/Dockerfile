FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . /app/manipulation

# Expose API and Streamlit ports
EXPOSE 8000
EXPOSE 8501

# Default command runs the API
CMD ["uvicorn", "manipulation.main:app", "--host", "0.0.0.0", "--port", "8000"]
