FROM docker.io/library/python:3.11 AS build

RUN apt update --yes
RUN apt install --yes \
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
  --upgrade

# remember to add borg user to fuse group in final container

COPY . /source

RUN cd /source/borgbackup && python -m pip wheel .[pyfuse3] \
  --wheel-dir /wheels \
  --prefer-binary \
  --disable-pip-version-check


FROM docker.io/library/python:3.11-slim AS final

COPY --from=build /wheels /wheels

RUN python -m pip install borgbackup[pyfuse3] \
  --upgrade \
  --pre \
  --no-index \
  --no-cache-dir \
  --find-links /wheels \
  --disable-pip-version-check && \
  rm -rf /install/

ENTRYPOINT ["/bin/bash"]
