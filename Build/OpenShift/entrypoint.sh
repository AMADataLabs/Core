#!/bin/sh
# Override user ID lookup to cope with being randomly assigned IDs using
# the -u option to 'docker run'.
USER_ID=$(id -u)
if [ x"$USER_ID" != x"0" -a x"$USER_ID" != x"1001" ]; then
    NSS_WRAPPER_PASSWD=/tmp/passwd.nss_wrapper
    NSS_WRAPPER_GROUP=/etc/group
    cat /etc/passwd | sed -e 's/^mockuser:/builder:/' > $NSS_WRAPPER_PASSWD
    echo "mockuser:x:$USER_ID:0:MockUser,,,:/OpenShift:/bin/bash" >> $NSS_WRAPPER_PASSWD
    export NSS_WRAPPER_PASSWD
    export NSS_WRAPPER_GROUP
    LD_PRELOAD=/usr/local/lib64/libnss_wrapper.so
    export LD_PRELOAD

    mkdir /OpenShift/.ssh
    echo "|1|73cHl1zspROg3smLvYE3liBdIyI=|wOijRpt1JN3EWSwO5jejNKyA68o= ssh-rsa AAAAB3NzaC1yc2EAAAABEQAAAQEAqQX4RaqXGy0/QjCSPrDVrmY8jMKwXXVEvD0iB8Q2q8DE/X5wqTuFR2Dg6KZygUo7IERLMMUVYTzsnDwHF/3kXNFtBtB0oOuV81LNSXe7afKBUzmOwHwAWhM99MXrb6R7bQ9XgefXYxGtFlpaPoBGrOs0+YUFiSYAVsl5EBe5QVpY4myfX9aBpjzHcwFXviviC9ytJNunhVxi2WL3ebk3fCkf0XcKPc+pbWfhUzERPuWhHnjDyYI5/GStMdIaGs5i5OYboMQJC60DDhECeHnjuo5MvNxq7P4W+pEUZUuj85z7Kf3SseFy7j1q34sTEn1UsVKimv1BP32f+6vv08m6tw==" > /OpenShift/.ssh/known_hosts
    chmod -Rf go-rwx /OpenShift/.ssh
fi
exec tini -s -- "$@"
