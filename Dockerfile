FROM --platform=linux/amd64 python:3.10

# install python-venv reqs
RUN apt-get update --no-install-recommends \
    && apt-get install python3-venv --no-install-recommends -y

# set username & uid inside docker
ARG UNAME=user1
ARG UID=1000
ENV WORKDIR="/home/$UNAME/music_analysis"

# add user UNAME as a member of the sudoers group
RUN useradd -rm --home-dir "/home/$UNAME" --shell /bin/bash -g root -G sudo -u "$UID" "$UNAME"

# set workdir
WORKDIR ${WORKDIR}

# setup python env vars & virtual env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

ENV VIRTUAL_ENV="/home/$UNAME/venv"
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies
RUN pip install pip==24.2
COPY requirements.txt  "$WORKDIR/requirements.txt"
RUN pip install --no-cache-dir --default-timeout=100 -r "$WORKDIR/requirements.txt"

# remove cache
RUN pip cache purge \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

# copy all files to src & exclude those in dockerignore
COPY . "$WORKDIR"

# change file ownership to docker user
RUN chown -R "$UNAME" "$WORKDIR"

USER "$UNAME"
CMD ["python", "app/server.py", "--port", "8080"]