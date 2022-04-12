BEGIN {
    name="";
}

/output "/ {
    print;
    sub(/output "/, "");
    sub(/"/, "");
    name=$1;
}

/  description = / {
    print;
}

/  value/ {
    print "  value = module.this." name;
}

/^}$/ { print; }
