FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
ENV WATCHTOWER_HOME=/data
VOLUME ["/data"]
ENTRYPOINT ["watchtower"]
CMD ["run"]
