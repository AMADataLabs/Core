import json

data = None
values = {}

with open('ssm_parameter_values_ivl.json') as file:
    data = json.loads(file.read())

for parameter in data["Parameters"]:
    values[parameter["Name"].replace('/OneView/dev/', '')] = dict(
        Type=parameter["Type"],
        Value=parameter["Value"]
    )

for name in sorted(values.keys()):
    parameter = values[name]

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
