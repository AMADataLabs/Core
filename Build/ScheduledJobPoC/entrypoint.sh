#!/bin/sh
# Override user ID lookup to cope with being randomly assigned IDs using
# the -u option to 'docker run'.
USER_ID=$(id -u)
if [ x"$USER_ID" != x"0" -a x"$USER_ID" != x"1001" ]; then
    NSS_WRAPPER_PASSWD=/tmp/passwd.nss_wrapper
    NSS_WRAPPER_GROUP=/etc/group
    cat /etc/passwd | sed -e 's/^mockuser:/builder:/' > $NSS_WRAPPER_PASSWD
    echo "mockuser:x:$USER_ID:0:MockUser,,,:/ScheduledJobPoC:/bin/bash" >> $NSS_WRAPPER_PASSWD
    export NSS_WRAPPER_PASSWD
    export NSS_WRAPPER_GROUP
    LD_PRELOAD=/usr/local/lib64/libnss_wrapper.so
    export LD_PRELOAD

    mkdir /ScheduledJobPoC/.ssh
    touch /ScheduledJobPoC/.ssh/known_hosts
    chmod -Rf go-rwx /ScheduledJobPoC/.ssh
fi
exec tini -- "$@"
