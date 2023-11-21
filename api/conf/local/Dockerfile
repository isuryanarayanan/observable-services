FROM python:3.11.6

# Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ="Asia/Kolkata"
ENV PATH="/home/user/.local/bin:$PATH"

# Setup working directory
RUN mkdir /app
COPY ./conf/local/firebase.json /firebase.json
COPY ./project /app

# Essential directories and files
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Configure tmux
RUN apt-get update && apt-get install -y tmux
RUN echo "set -g prefix C-a" > ~/.tmux.conf

# Run the app
RUN cd /app
WORKDIR /app

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

ARG USER_ID
ARG GROUP_ID

USER root
COPY ./project/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
USER user

# CMD [ "python","manage.py","runserver", "0.0.0.0:8000" ]
# ENTRYPOINT [ "/entrypoint.sh" ]
