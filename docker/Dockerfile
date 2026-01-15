FROM n8nio/n8n:1.88.0

# Switch to root to install packages
USER root
RUN apk add --update python3 py3-pip

USER node
RUN python3 -m pip install --user --break-system-packages pipx

ENV PATH="/home/node/.local/bin:${PATH}"
