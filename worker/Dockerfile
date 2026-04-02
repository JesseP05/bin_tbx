# syntax=docker/dockerfile:1

# vrijwel zelfde commands als manual install uit readme v1

FROM python:3.11.15-slim AS builder

# dependencies voor compileren van fastp en kraken2
RUN apt-get update && apt-get install -y --no-install-recommends \
    zlib1g-dev \
    wget \
    tar \
    make \
    build-essential \
    curl \
    perl && \
    rm -rf /var/lib/apt/lists/*

RUN wget http://opengene.org/fastp/fastp -O /usr/local/bin/fastp && \
    chmod +x /usr/local/bin/fastp

# downlaod en compileer kraken2
RUN wget https://github.com/DerrickWood/kraken2/archive/refs/tags/v2.17.1.tar.gz && \
    tar -xf v2.17.1.tar.gz && \
    cd kraken2-2.17.1 && \
    ./install_kraken2.sh /opt/kraken2 && \
    cd .. && \
    rm -rf v2.17.1.tar.gz kraken2-2.17.1

# runtime image
FROM python:3.11.15-slim

# weer dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libdeflate0 \
    libisal2 \
    zlib1g \
    perl \
    git \
    wget \
    bash \
    curl \
    make \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# copy compiled binaary
COPY --from=builder /usr/local/bin/fastp /usr/local/bin/fastp
COPY --from=builder /opt/kraken2 /opt/kraken2

ENV PATH="/opt/kraken2/bin:/opt/kraken2:$PATH"

# Krona install met optimize
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    git clone --depth 1 https://github.com/marbl/Krona.git /opt/Krona && \
    cd /opt/Krona/KronaTools && \
    ./install.pl && \
    mkdir taxonomy && \
    ./updateTaxonomy.sh taxonomy && \
    rm -rf /opt/Krona/.git && \
    apt-get remove -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shared/ ./shared/
COPY worker/*.py ./
COPY worker/entry.sh ./

# convert line endings
RUN apt-get update && apt-get install -y --no-install-recommends dos2unix && \
    dos2unix entry.sh && \
    chmod +x entry.sh && \
    rm -rf /var/lib/apt/lists/*

# database download
ENTRYPOINT ["bash", "entry.sh"]

ENV IN_DOCKER=1

CMD ["python", "-u", "watcher.py"]
