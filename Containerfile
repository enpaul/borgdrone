# ======================================================
# Stage 1: Build BorgBackup wheel
FROM docker.io/library/python:3.11 AS build-borg

# Install borg build dependencies
RUN apt-get update --yes
RUN apt-get install --yes --no-install-recommends \
  libacl1-dev \
  libacl1 \
  libssl-dev \
  liblz4-dev \
  libzstd-dev \
  libxxhash-dev \
  build-essential \
  pkg-config \
  python3-pkgconfig \
  libfuse3-dev
RUN python -m pip install \
  Cython==3.0.3 \
  pkgconfig==1.5.5 \
  --disable-pip-version-check \
  --upgrade \
  --no-cache-dir

# Build borg dist wheel
COPY . /source
WORKDIR /source/borgbackup
RUN python -m pip wheel .[pyfuse3] \
  --wheel-dir /wheels \
  --prefer-binary \
  --disable-pip-version-check \
  --no-cache-dir


# ======================================================
# Stage 2: Build local repo resources
FROM docker.io/library/python:3.11 as build-drone

ENV POETRY_HOME /poetry
RUN curl -o /install-poetry.py -sSL https://install.python-poetry.org
RUN python /install-poetry.py --yes

COPY . /source
WORKDIR /source
RUN ${POETRY_HOME}/bin/poetry export \
  --format requirements.txt \
  --output /requirements.txt \
  --without-hashes
RUN python -m pip wheel \
  --wheel-dir /wheels \
  --requirement /requirements.txt \
  --disable-pip-version-check \
  --no-cache-dir


# ======================================================
# Stage 3: Final distribution image
FROM docker.io/library/python:3.11-slim AS publish

RUN apt-get update --yes && \
  apt-get install openssh-client --yes --no-install-recommends && \
  apt-get clean all && \
  rm --recursive --force /var/lib/apt/lists/* && \
  mkdir /repo /data /keys && \
  useradd borg --uid 1000 --home-dir /home/borg --create-home && \
  chown --recursive borg:borg /repo && \
  chown --recursive borg:borg /keys && \
  chmod --recursive 0600 /keys

COPY --from=build-borg /wheels /wheels/borg
COPY --from=build-drone /wheels /wheels/drone
COPY --from=build-drone /requirements.txt /wheels/drone.txt
# hadolint ignore=DL3013
RUN python -m pip install borgbackup[pyfuse3] \
  --upgrade \
  --pre \
  --no-index \
  --no-cache-dir \
  --find-links /wheels/borg \
  --disable-pip-version-check && \
  python -m pip install \
  --requirement /wheels/drone.txt \
  --upgrade \
  --pre \
  --no-index \
  --no-cache-dir \
  --find-links /wheels/drone \
  --disable-pip-version-check && \
  rm -rf /wheels/

WORKDIR /repo

VOLUME ["/repo", "/data", "/keys"]

USER 1000:1000

ENTRYPOINT ["/bin/bash"]
