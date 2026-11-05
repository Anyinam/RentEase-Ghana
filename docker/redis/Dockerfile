FROM redis:7-alpine AS config
COPY redis.conf /tmp/redis.conf

FROM redis:7-alpine AS runtime
COPY --from=config /tmp/redis.conf /usr/local/etc/redis/redis.conf
