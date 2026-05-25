FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt update && \
    apt install -y \
      qemu-user \
      qemu-user-binfmt

RUN chmod +x ./bin/

COPY ./bin/ /usr/local/bin/

CMD ["sleep", "infinity"]
