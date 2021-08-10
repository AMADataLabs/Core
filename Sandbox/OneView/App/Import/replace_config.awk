BEGIN {
    output_on = 1
}

/^    [a-z]/ {
    output_on = 1
}

/^    user_id = event['id']/

/^$/ {
    output_on = 1
}

/^    db_host = / {
    output_on = 0
    print "    db_host = os.environ.get(\"DATABASE_HOST\")"
}


/^    user_id = [^e]/ {
    output_on = 0
    print "    user_id = os.environ.get(\"DATABASE_USERNAME\")"
}

/^    password =/ {
    output_on = 0
    print "    password = os.environ.get(\"DATABASE_PASSWORD\")"
}

/^    dbname =/ {
    output_on = 0
    print "    dbname = os.environ.get(\"DATABASE_NAME\")"
}

output_on == 1
