# Systemd inside a Docker container
FROM ubuntu:18.04

RUN apt-get update --yes

RUN apt-get install --yes systemd curl git sudo

# Kill all the things we don't need
RUN find /etc/systemd/system \
    /lib/systemd/system \
    -path '*.wants/*' \
    -not -name '*journald*' \
    -not -name '*systemd-tmpfiles*' \
    -not -name '*systemd-user-sessions*' \
    -exec rm \{} \;

RUN mkdir -p /etc/sudoers.d

RUN systemctl set-default multi-user.target

STOPSIGNAL SIGRTMIN+3

# Uncomment these lines for a development install
ENV JHUB_INITIALIZE_DEV=yes
ENV JHUB_INITIALIZE_PIP_SPEC=/srv/src
ENV JHUB=/opt/jhub/hub/bin:${PATH}

CMD ["/bin/bash", "-c", "exec /sbin/init --log-target=journal 3>&1"]