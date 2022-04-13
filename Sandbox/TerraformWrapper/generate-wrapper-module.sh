#!/bin/bash


VARIABLES=


main() {
    extract_variables

    generate_main

    generate_variables

    generate_outputs
}


extract_variables() {
    VARIABLES=(`cat terraform-aws-lambda/variables.tf | grep 'variable "' | sed -e 's/variable "//' -e 's/" {//'`)
}


generate_main() {
    echo 'module "this" {' > main.tf
    echo "  source = \"app.terraform.io/AMA/cloudwatch-group/aws\"" >> main.tf
    echo "  version = \"3.1.0\"" >> main.tf

    for variable in "${VARIABLES[@]}" ; do
        if [[ "$variable" != "tags" ]]; then
            echo "  ${variable} = var.${variable}" >> main.tf
        fi
    done

    echo "  tags = local.tags" >> main.tf

    echo '}' >> main.tf

    terraform fmt main.tf
}


generate_variables() {
    cat terraform-aws-lambda/variables.tf tags.txt > variables.tf

    terraform fmt variables.tf
}


generate_outputs() {
    awk -f generate_outputs.awk terraform-aws-lambda/outputs.tf > outputs.tf

    terraform fmt outputs.tf
}


main "$@"
