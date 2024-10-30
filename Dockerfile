FROM python:3.10
RUN pip install fastapi boto3 uvicorn
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]