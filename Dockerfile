FROM python:3.11-alpine

ARG USER=coolio
ARG GROUP=coolio
ARG UID=1234
ARG GID=4321

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN apk add --no-cache tzdata \
    && pip install --no-cache-dir --upgrade pip pipenv \
    && pipenv sync --system \
    && addgroup --gid $GID $GROUP \
    && adduser -D -H --gecos "" \
                     --ingroup "$GROUP" \
                     --uid "$UID" \
                     "$USER" \
    && rm -rf /tmp/* /var/{cache,log}/* /var/lib/apt/lists/*

USER $USER

ENTRYPOINT ["python", "-m", "octopus_api_consumer"]
CMD ["--help"]
