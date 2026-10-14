# Native ARM build for Hikaru's Mac; the pinned base contains PostgreSQL 18.6.
FROM postgres@sha256:06cad38a5d9f5d24b4d83d86def30795d5e4b757fedbf5281172b576dedcd941
ARG CITUS_VERSION=14.1.0
ARG CITUS_SHA256=e174ed00efba74aaf5a9da87f770f6a7e11274066cce8449d804bc6b17df6ff8
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates flex bison pkg-config \
    postgresql-server-dev-18 libcurl4-openssl-dev liblz4-dev libzstd-dev \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends libicu-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fL --retry 3 "https://github.com/citusdata/citus/archive/refs/tags/v${CITUS_VERSION}.tar.gz" -o /tmp/citus.tar.gz \
    && echo "${CITUS_SHA256}  /tmp/citus.tar.gz" | sha256sum -c - \
    && tar -xf /tmp/citus.tar.gz -C /tmp \
    && cd "/tmp/citus-${CITUS_VERSION}" \
    && ./configure \
    && make -j4 \
    && make install-all \
    && rm -rf /tmp/citus*
LABEL org.cs5424.citus.version="14.1.0" org.cs5424.purpose="isolated local validation"
