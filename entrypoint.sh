#!/bin/bash

function die {
  echo $1
  if [ ! -z $2 ]; then
    cat $2
  fi
  exit 1
}

/usr/bin/supervisord --configuration /etc/supervisord.conf

for i in `seq 1 60`; do
  if [ -e /var/lib/mysql/mysql.sock ]; then
    echo "mysqld started"
    break
  fi
  sleep 1
done

if ! mysql -e "show databases;" > /dev/null 2>&1; then
  echo "failed to query mysql - did it start?"
  exit 1
fi

# create Slurm database
mysql -e "CREATE DATABASE slurm_acct_db;" || die "failed to create database"
mysql -e "create user 'slurm'@'localhost' identified by 'password';" || die "failed to create slurm mysql user"
mysql -e "grant all on slurm_acct_db.* TO 'slurm'@'localhost';" || die "failed to grant privs to slurm mysql user"

# create munge key
create-munge-key
supervisorctl start munged

supervisorctl start slurmdbd || die "slurmdbd failed to start" /var/log/slurm/slurmdbd.log
supervisorctl start slurmctld || die "slurmctld failed to start" /var/log/slurm/slurmctld.log
supervisorctl start slurmd || die "slurmd failed to start" /var/log/slurm/slurmd.log

sinfo

exec $@
