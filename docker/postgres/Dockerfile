FROM postgres:15-alpine AS config
COPY postgresql.conf /tmp/postgresql.conf

FROM postgres:15-alpine AS runtime
COPY --from=config /tmp/postgresql.conf /etc/postgresql/postgresql.conf
