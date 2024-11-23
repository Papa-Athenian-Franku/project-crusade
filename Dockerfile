FROM python:3.12-slim

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Work directory
WORKDIR /src

CMD ["python", "bot.py"]
