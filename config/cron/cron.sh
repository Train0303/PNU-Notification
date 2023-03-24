#!/bin/bash

log_dir=/app/logs/cron_logs/$(date +'%Y%m%d')
mkdir -p "$log_dir" || { echo "Can't create log directory '$log_dir'"; exit 1; }

#
# we write to the same log each time
# this can be enhanced as per needs: one log per execution, one log per job per execution etc.
#
log_file=$log_dir/noti.log

#
# hitherto, both stdout and stderr end up in the log file
#
exec 2>&1 1>>"$log_file"

#
# Run the environment setup that is shared across all jobs.
# This can set up things like PATH etc.
#
# Note: it is not a good practice to source in .profile or .bashrc here
#
# source /path/to/setup_env.sh
export PATH=$(/usr/bin/getconf PATH):/usr/local/bin
export DJANGO_DEBUG=False
export DJANGO_SETTINGS_MODULE=pnuNoti.settings.prod

# cd /app
# echo "pring all files in app"
# ls -al
#
# run the job
#
# echo "$(date): starting cron, command=[$*]"
# "$@"
# echo "$(date): cron ended, exit code is $?"

echo "$(date): starting cron"
python /app/manage.py crontab_mail >> $log_file 2>&1
python /app/manage.py crontab_mail_hakjisi >> $log_file 2>&1
echo "$(date): cron ended, exit code is $?"
