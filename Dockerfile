FROM python:3.13.11-slim-trixie
WORKDIR /usr/local/app

# Copy in the source code
COPY src ./src
# Install the application dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

EXPOSE 8080

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["python", "src/bot.py"]