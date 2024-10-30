FROM python:3.10
RUN pip install fastapi boto3 uvicorn pyjwt requests cryptography
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]