locals {
    ### Static Constants ###

    environments                    = {
        sandbox="sbx"
        dev="dev"
        test="tst"
        prod="prd"
    }

    accounts                        = {
        sbx = "644454719059"
        dev = "191296302136"
        tst = "194221139997"
        stg = "340826698851"
        prd = "285887636563"
    }

    project                         = "DataLake"
    owner                           = "DataLabs"
    contact                         = "DataLabs@ama-assn.org"
    budget_code                     = "PBW"
    department                      = "HS"
    group                           = "DataLabs"
    region                          = "us-east-1"


    ### Dynamic Constants ###

    environment                     = regex("(?:.+/)(?P<environment>..*)", abspath(path.root)).environment
    account                         = lookup(local.accounts, local.environment)
    ecr_account                     = local.environment == "sbx" ? local.account : "394406051370"

    tags                    = {
        Environment             = local.environment
        Contact                 = local.contact
        SystemTier              = "0"
        DRTier                  = "0"
        DataClassification      = "N/A"
        BudgetCode              = local.budget_code
        Owner                   = local.owner
        ProjectName             = local.project
        Notes                   = "N/A"
        OS                      = "N/A"
        EOL                     = "N/A"
        MaintenanceWindow       = "N/A"
        Group                   = local.group
        Department              = local.department
    }

    public_subnets = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]


    ### replicate TE stacks ##
    subnets = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
}
