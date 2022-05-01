FROM rockylinux:8

LABEL org.opencontainers.image.source="https://github.com/neilmunday/docker-rocky8-linux" \
      org.opencontainers.image.description="A Rocky 8 Slurm container intended for testing Slurm" \
      org.opencontainers.image.title="rocky8-slurm" \
      maintainer="Neil Munday"

ARG SLURM_VER=21.08.7

# download, build, install and clean-up
RUN dnf install -y dnf-plugins-core && \
    dnf update -y && \
    dnf install -y epel-release && \
    dnf config-manager --set-enabled powertools && \
    dnf install -y \
    gcc \
    mailx \
    mariadb-devel \
    mariadb-server \
    munge-devel \
    pam-devel \
    perl \
    python3 \
    readline-devel \
    rpm-build \
    supervisor \
    tini \
    wget && \
    wget https://download.schedmd.com/slurm/slurm-${SLURM_VER}.tar.bz2 && \
    rpmbuild -tb slurm-${SLURM_VER}.tar.bz2 && \
    dnf localinstall -y /root/rpmbuild/RPMS/x86_64/slurm-${SLURM_VER}-1.el8.x86_64.rpm \
    /root/rpmbuild/RPMS/x86_64/slurm-slurmctld-${SLURM_VER}-1.el8.x86_64.rpm \
    /root/rpmbuild/RPMS/x86_64/slurm-slurmd-${SLURM_VER}-1.el8.x86_64.rpm \
    /root/rpmbuild/RPMS/x86_64/slurm-slurmdbd-${SLURM_VER}-1.el8.x86_64.rpm && \
    dnf -y erase gcc mariab-devel make munge-devel pam-devel readline-devel rpm-build wget && \
    dnf clean all && \
    rm -rf /root/rpmbuild /root/slurm*.tar.bz2

# add users
RUN groupadd -r slurm && \
    useradd -r -g slurm -d /var/empty/slurm -m -s /bin/bash slurm && \
    groupadd test && \
    useradd -g test -d /home/test -m test

RUN install -d -o slurm -g slurm /etc/slurm /var/spool/slurm /var/log/slurm

COPY supervisord.conf /etc/
COPY --chown=slurm slurm.conf /etc/slurm/
COPY --chown=slurm slurmdbd.conf /etc/slurm/
COPY --chown=root entrypoint.sh /usr/local/sbin/

RUN /usr/bin/mysql_install_db --user=mysql

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/sbin/entrypoint.sh"]
CMD ["tail -f /dev/null"]