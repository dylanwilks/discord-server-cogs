FROM python:3

# Defaults
ARG UID=999
ARG GID=999
ARG USER=bot
ARG HOME=/usr/src/app
ARG ADMIN=/usr/local/bin/admin
ENV PATH="$HOME/venv/bin:$HOME/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV BOT_PREFIX=!
ENV BOT_WATCHER_SECONDS=3.0
ENV BOT_NAME_MINUTES=10.0
ENV BOT_DB=$HOME/db/bot.db
ENV BOT_CONSTANTS=$HOME/config/constants.json
ENV BOT_CONFIG=$HOME/config/config.json
ENV BOT_COGS=$HOME/config/cogs.json

# Packages and tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        wakeonlan \
        keychain \
        iputils-ping \
        netcat-openbsd \
        net-tools \
        ffmpeg \
        quickjs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN echo '#!/bin/sh' > $ADMIN
RUN echo 'python /usr/src/app/admin.py $1' >> $ADMIN
RUN chmod 755 $ADMIN

# Setup bot environment
RUN groupadd -g $GID -o $USER
RUN useradd -r -M -d $HOME -u $UID -g $GID $USER
WORKDIR $HOME
RUN chown $UID:$UID $HOME
RUN chmod 700 $HOME

# Switch user and download python files
COPY --chown=$USER:$USER requirements.txt ./
USER $USER
RUN python -m venv $HOME/venv
RUN pip install --no-cache-dir -r requirements.txt
USER root
COPY --chown=$USER:$USER . .
RUN chmod +x start-bot.sh

# Run container as user
USER $USER
ENTRYPOINT ["./start-bot.sh"]
