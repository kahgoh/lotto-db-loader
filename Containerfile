# Generate requirements.txt from the Pipenv
FROM python:3.12.4-alpine3.20 AS builder

ENV PATH=/root/.local/bin:$PATH

WORKDIR /usr/src/

ENV PATH="${PATH}:/root/.local/bin"
COPY src/Pipfile src/Pipfile.lock ./ 
RUN pip install --user pipenv \
  && pipenv requirements > requirements.txt

# Build the app container image
FROM python:3.12.4-alpine3.20

COPY src/ /usr/src/
WORKDIR /usr/src

COPY --from=builder /usr/src/requirements.txt ./
# Pipfile is not needed in the final image
RUN rm -f /usr/src/Pipfile /usr/src/Pipfile.lock \
  && pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python", "download.py"]