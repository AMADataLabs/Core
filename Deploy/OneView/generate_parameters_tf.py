import json

data = None

with open('parameter_values.json') as file:
    data = json.loads(file.read())

for parameter in data["Parameters"]:
    name = parameter["Name"].replace('/OneView/dev/', '')

    print(\
f'''
resource "aws_ssm_parameter" "{name}" {{
    name  = "/${{var.project}}/${{local.environment}}/{name}"
    type  = "{parameter["Type"]}"
    value = "{parameter["Value"]}"

    tags = local.tags
}}
'''
)
