#!/bin/bash


VARIABLES=
OUTPUTS=


main() {
    extract_variables

    extract_outputs

    generate_main

    generate_variables

    generate_outputs
}


extract_variables() {
    VARIABLES=(`cat terraform-aws-lambda/variables.tf | grep 'variable "' | sed -e 's/variable "//' -e 's/" {//'`)
}


extract_outputs() {
    OUTPUTS=(`cat terraform-aws-lambda/outputs.tf | grep 'output "' | sed -e 's/output "//' -e 's/" {//'`)
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
