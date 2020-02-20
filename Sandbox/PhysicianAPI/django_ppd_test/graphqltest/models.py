# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    last_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_flag = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoTest(models.Model):
    me = models.AutoField(db_column='ME', primary_key=True, blank=True)  # Field name made lowercase.
    record_id = models.TextField(db_column='RECORD_ID', blank=True, null=True)  # Field name made lowercase.
    update_type = models.TextField(db_column='UPDATE_TYPE', blank=True, null=True)  # Field name made lowercase.
    address_type = models.TextField(db_column='ADDRESS_TYPE', blank=True, null=True)  # Field name made lowercase.
    mailing_name = models.TextField(db_column='MAILING_NAME', blank=True, null=True)  # Field name made lowercase.
    last_name = models.TextField(db_column='LAST_NAME', blank=True, null=True)  # Field name made lowercase.
    first_name = models.TextField(db_column='FIRST_NAME', blank=True, null=True)  # Field name made lowercase.
    middle_name = models.TextField(db_column='MIDDLE_NAME', blank=True, null=True)  # Field name made lowercase.
    suffix = models.TextField(db_column='SUFFIX', blank=True, null=True)  # Field name made lowercase.
    mailing_line_1 = models.TextField(db_column='MAILING_LINE_1', blank=True, null=True)  # Field name made lowercase.
    mailing_line_2 = models.TextField(db_column='MAILING_LINE_2', blank=True, null=True)  # Field name made lowercase.
    city = models.TextField(db_column='CITY', blank=True, null=True)  # Field name made lowercase.
    state = models.TextField(db_column='STATE', blank=True, null=True)  # Field name made lowercase.
    zip = models.TextField(db_column='ZIP', blank=True, null=True)  # Field name made lowercase.
    sector = models.TextField(db_column='SECTOR', blank=True, null=True)  # Field name made lowercase.
    carrier_route = models.TextField(db_column='CARRIER_ROUTE', blank=True, null=True)  # Field name made lowercase.
    address_undeliverable_flag = models.TextField(db_column='ADDRESS_UNDELIVERABLE_FLAG', blank=True, null=True)  # Field name made lowercase.
    fips_county = models.TextField(db_column='FIPS_COUNTY', blank=True, null=True)  # Field name made lowercase.
    fips_state = models.TextField(db_column='FIPS_STATE', blank=True, null=True)  # Field name made lowercase.
    printer_control_code = models.TextField(db_column='PRINTER_CONTROL_CODE', blank=True, null=True)  # Field name made lowercase.
    pc_zip = models.TextField(db_column='PC_ZIP', blank=True, null=True)  # Field name made lowercase.
    pc_sector = models.TextField(db_column='PC_SECTOR', blank=True, null=True)  # Field name made lowercase.
    delivery_point_code = models.TextField(db_column='DELIVERY_POINT_CODE', blank=True, null=True)  # Field name made lowercase.
    check_digit = models.TextField(db_column='CHECK_DIGIT', blank=True, null=True)  # Field name made lowercase.
    printer_control_code_2 = models.TextField(db_column='PRINTER_CONTROL_CODE_2', blank=True, null=True)  # Field name made lowercase.
    region = models.TextField(db_column='REGION', blank=True, null=True)  # Field name made lowercase.
    division = models.TextField(db_column='DIVISION', blank=True, null=True)  # Field name made lowercase.
    group = models.TextField(db_column='GROUP', blank=True, null=True)  # Field name made lowercase.
    tract = models.TextField(db_column='TRACT', blank=True, null=True)  # Field name made lowercase.
    suffix_census = models.TextField(db_column='SUFFIX_CENSUS', blank=True, null=True)  # Field name made lowercase.
    block_group = models.TextField(db_column='BLOCK_GROUP', blank=True, null=True)  # Field name made lowercase.
    msa_population_size = models.TextField(db_column='MSA_POPULATION_SIZE', blank=True, null=True)  # Field name made lowercase.
    micro_metro_ind = models.TextField(db_column='MICRO_METRO_IND', blank=True, null=True)  # Field name made lowercase.
    cbsa = models.TextField(db_column='CBSA', blank=True, null=True)  # Field name made lowercase.
    cbsa_div_ind = models.TextField(db_column='CBSA_DIV_IND', blank=True, null=True)  # Field name made lowercase.
    md_do_code = models.TextField(db_column='MD_DO_CODE', blank=True, null=True)  # Field name made lowercase.
    birth_year = models.TextField(db_column='BIRTH_YEAR', blank=True, null=True)  # Field name made lowercase.
    birth_city = models.TextField(db_column='BIRTH_CITY', blank=True, null=True)  # Field name made lowercase.
    birth_state = models.TextField(db_column='BIRTH_STATE', blank=True, null=True)  # Field name made lowercase.
    birth_country = models.TextField(db_column='BIRTH_COUNTRY', blank=True, null=True)  # Field name made lowercase.
    gender = models.TextField(db_column='GENDER', blank=True, null=True)  # Field name made lowercase.
    telephone_number = models.TextField(db_column='TELEPHONE_NUMBER', blank=True, null=True)  # Field name made lowercase.
    presumed_dead_flag = models.TextField(db_column='PRESUMED_DEAD_FLAG', blank=True, null=True)  # Field name made lowercase.
    fax_number = models.TextField(db_column='FAX_NUMBER', blank=True, null=True)  # Field name made lowercase.
    top_cd = models.TextField(db_column='TOP_CD', blank=True, null=True)  # Field name made lowercase.
    pe_cd = models.TextField(db_column='PE_CD', blank=True, null=True)  # Field name made lowercase.
    prim_spec_cd = models.TextField(db_column='PRIM_SPEC_CD', blank=True, null=True)  # Field name made lowercase.
    sec_spec_cd = models.TextField(db_column='SEC_SPEC_CD', blank=True, null=True)  # Field name made lowercase.
    mpa_cd = models.TextField(db_column='MPA_CD', blank=True, null=True)  # Field name made lowercase.
    pra_recipient = models.TextField(db_column='PRA_RECIPIENT', blank=True, null=True)  # Field name made lowercase.
    pra_exp_dt = models.TextField(db_column='PRA_EXP_DT', blank=True, null=True)  # Field name made lowercase.
    gme_conf_flg = models.TextField(db_column='GME_CONF_FLG', blank=True, null=True)  # Field name made lowercase.
    from_dt = models.TextField(db_column='FROM_DT', blank=True, null=True)  # Field name made lowercase.
    to_dt = models.TextField(db_column='TO_DT', blank=True, null=True)  # Field name made lowercase.
    year_in_program = models.TextField(db_column='YEAR_IN_PROGRAM', blank=True, null=True)  # Field name made lowercase.
    post_graduate_year = models.TextField(db_column='POST_GRADUATE_YEAR', blank=True, null=True)  # Field name made lowercase.
    gme_spec_1 = models.TextField(db_column='GME_SPEC_1', blank=True, null=True)  # Field name made lowercase.
    gme_spec_2 = models.TextField(db_column='GME_SPEC_2', blank=True, null=True)  # Field name made lowercase.
    training_type = models.TextField(db_column='TRAINING_TYPE', blank=True, null=True)  # Field name made lowercase.
    gme_inst_state = models.TextField(db_column='GME_INST_STATE', blank=True, null=True)  # Field name made lowercase.
    gme_inst_id = models.TextField(db_column='GME_INST_ID', blank=True, null=True)  # Field name made lowercase.
    medschool_state = models.TextField(db_column='MEDSCHOOL_STATE', blank=True, null=True)  # Field name made lowercase.
    medschool_id = models.TextField(db_column='MEDSCHOOL_ID', blank=True, null=True)  # Field name made lowercase.
    medschool_grad_year = models.TextField(db_column='MEDSCHOOL_GRAD_YEAR', blank=True, null=True)  # Field name made lowercase.
    no_contact_ind = models.TextField(db_column='NO_CONTACT_IND', blank=True, null=True)  # Field name made lowercase.
    no_web_flag = models.TextField(db_column='NO_WEB_FLAG', blank=True, null=True)  # Field name made lowercase.
    pdrp_flag = models.TextField(db_column='PDRP_FLAG', blank=True, null=True)  # Field name made lowercase.
    pdrp_start_dt = models.TextField(db_column='PDRP_START_DT', blank=True, null=True)  # Field name made lowercase.
    polo_mailing_line_1 = models.TextField(db_column='POLO_MAILING_LINE_1', blank=True, null=True)  # Field name made lowercase.
    polo_mailing_line_2 = models.TextField(db_column='POLO_MAILING_LINE_2', blank=True, null=True)  # Field name made lowercase.
    polo_city = models.TextField(db_column='POLO_CITY', blank=True, null=True)  # Field name made lowercase.
    polo_state = models.TextField(db_column='POLO_STATE', blank=True, null=True)  # Field name made lowercase.
    polo_zip = models.TextField(db_column='POLO_ZIP', blank=True, null=True)  # Field name made lowercase.
    polo_sector = models.TextField(db_column='POLO_SECTOR', blank=True, null=True)  # Field name made lowercase.
    polo_carrier_route = models.TextField(db_column='POLO_CARRIER_ROUTE', blank=True, null=True)  # Field name made lowercase.
    most_recent_former_last_name = models.TextField(db_column='MOST_RECENT_FORMER_LAST_NAME', blank=True, null=True)  # Field name made lowercase.
    most_recent_former_middle_name = models.TextField(db_column='MOST_RECENT_FORMER_MIDDLE_NAME', blank=True, null=True)  # Field name made lowercase.
    most_recent_former_first_name = models.TextField(db_column='MOST_RECENT_FORMER_FIRST_NAME', blank=True, null=True)  # Field name made lowercase.
    next_most_recent_former_last = models.TextField(db_column='NEXT_MOST_RECENT_FORMER_LAST', blank=True, null=True)  # Field name made lowercase.
    next_most_recent_former_middle = models.TextField(db_column='NEXT_MOST_RECENT_FORMER_MIDDLE', blank=True, null=True)  # Field name made lowercase.
    next_most_recent_former_first = models.TextField(db_column='NEXT_MOST_RECENT_FORMER_FIRST', blank=True, null=True)  # Field name made lowercase.
    
    def __str__(self):
        return self.me


    class Meta:
        managed = False
        db_table = 'django_test'
        ordering=('me',)
