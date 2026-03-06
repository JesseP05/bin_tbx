# syntax=docker/dockerfile:1

# vrijwel zelfde commands als manual install uit readme v1

FROM python:3.11-slim as builder

# dependencies voor compileren van fastp en kraken2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libdeflate-dev \
    libisal-dev \
    isal \
    build-essential \
    zlib1g-dev

# download en compileer fastp
RUN wget https://github.com/OpenGene/fastp/archive/refs/tags/v1.1.0.tar.gz && \
    tar -xf v1.1.0.tar.gz && \
    cd fastp-1.1.0/ && \
    make -j && make install

# downlaod en compileer kraken2
RUN wget https://github.com/DerrickWood/kraken2/archive/refs/tags/v2.17.1.tar.gz && \
    tar -xf v2.17.1.tar.gz && \
    cd kraken2-2.17.1 && \
    ./install_kraken2.sh /usr/local/bin

# runtime image
FROM python:3.11-slim

# dependencies weer nodig
RUN apt-get update && apt-get install -y \
    libdeflate0 \
    libisal2 \
    zlib1g \
    perl \
    git \
    wget \
    bash

# copy builder files
COPY --from=builder /usr/local/bin/fastp /usr/local/bin/fastp
COPY --from=builder /usr/local/bin/kraken2* /usr/local/bin/

# Krona install
RUN git clone https://github.com/marbl/Krona.git /opt/Krona && \
    cd /opt/Krona/KronaTools && \
    ./install.pl && \
    mkdir taxonomy && ./updateTaxonomy.sh taxonomy

# python dependencies for watcher
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["bash", "entry.sh"]

CMD ["python", "watcher.py"]