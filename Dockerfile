# Use Python 3.11 image
FROM python:3.11.9-bullseye

# Set the working directory
WORKDIR /usr/app

RUN pwd

RUN python --version

# Install dependencies
COPY requirements.txt requirements.txt

RUN ls -la

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the source code
COPY . .

ENV PORT=8000

# Expose the port
EXPOSE $PORT

# Run the application
CMD ["sh", "-c", "fastapi run app/main.py --port $PORT"]
#CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
#CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
