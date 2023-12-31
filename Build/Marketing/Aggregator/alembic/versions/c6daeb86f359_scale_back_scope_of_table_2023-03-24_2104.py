"""Scale back scope of table.

Revision ID: c6daeb86f359
Revises: edb7fe8072ab
Create Date: 2023-03-24 21:04:05.008492+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c6daeb86f359'
down_revision = 'edb7fe8072ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contact', 'original_order_dollars_group', schema='marketing')
    op.drop_column('contact', 'last_order_dollars', schema='marketing')
    op.drop_column('contact', 'most_frequent_audience', schema='marketing')
    op.drop_column('contact', 'email_match_or_append', schema='marketing')
    op.drop_column('contact', 'last_order_date', schema='marketing')
    op.drop_column('contact', 'impairment_marketing_driver', schema='marketing')
    op.drop_column('contact', 'total_email_opens', schema='marketing')
    op.drop_column('contact', 'last_data_file_format', schema='marketing')
    op.drop_column('contact', 'zipcode', schema='marketing')
    op.drop_column('contact', 'original_email_open', schema='marketing')
    op.drop_column('contact', 'is_professional_reseller', schema='marketing')
    op.drop_column('contact', 'city', schema='marketing')
    op.drop_column('contact', 'most_frequent_discount', schema='marketing')
    op.drop_column('contact', 'all_products_2', schema='marketing')
    op.drop_column('contact', 'original_channel', schema='marketing')
    op.drop_column('contact', 'last_driving_tactic', schema='marketing')
    op.drop_column('contact', 'suppress_telemarketing', schema='marketing')
    op.drop_column('contact', 'title_description', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_recency', schema='marketing')
    op.drop_column('contact', 'is_member', schema='marketing')
    op.drop_column('contact', 'generic_score', schema='marketing')
    op.drop_column('contact', 'documentation_marketing_driver', schema='marketing')
    op.drop_column('contact', 'promotion_frequency', schema='marketing')
    op.drop_column('contact', 'subscription_frequency', schema='marketing')
    op.drop_column('contact', 'last_subscription_start', schema='marketing')
    op.drop_column('contact', 'delivery_point_check_digit', schema='marketing')
    op.drop_column('contact', 'list_keys', schema='marketing')
    op.drop_column('contact', 'suppress_email', schema='marketing')
    op.drop_column('contact', 'original_order_dollars', schema='marketing')
    op.drop_column('contact', 'coding_marketing_driver', schema='marketing')
    op.drop_column('contact', 'original_product_2', schema='marketing')
    op.drop_column('contact', 'original_recency', schema='marketing')
    op.drop_column('contact', 'evening_phone', schema='marketing')
    op.drop_column('contact', 'business_title', schema='marketing')
    op.drop_column('contact', 'gender', schema='marketing')
    op.drop_column('contact', 'business_name', schema='marketing')
    op.drop_column('contact', 'do_not_call', schema='marketing')
    op.drop_column('contact', 'most_frequent_sku', schema='marketing')
    op.drop_column('contact', 'average_dollars', schema='marketing')
    op.drop_column('contact', 'record_sequence', schema='marketing')
    op.drop_column('contact', 'day_phone', schema='marketing')
    op.drop_column('contact', 'industry_description', schema='marketing')
    op.drop_column('contact', 'secondary_specialty', schema='marketing')
    op.drop_column('contact', 'telesales_score', schema='marketing')
    op.drop_column('contact', 'record_origin', schema='marketing')
    op.drop_column('contact', 'last_pricing_model', schema='marketing')
    op.drop_column('contact', 'name', schema='marketing')
    op.drop_column('contact', 'last_opened_email_product_1', schema='marketing')
    op.drop_column('contact', 'do_not_email', schema='marketing')
    op.drop_column('contact', 'email_open_rate', schema='marketing')
    op.drop_column('contact', 'address_3', schema='marketing')
    op.drop_column('contact', 'recency_group', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_last_term', schema='marketing')
    op.drop_column('contact', 'buyer_type', schema='marketing')
    op.drop_column('contact', 'total_email_bounces', schema='marketing')
    op.drop_column('contact', 'last_sku', schema='marketing')
    op.drop_column('contact', 'total_dollars', schema='marketing')
    op.drop_column('contact', 'subscription_recency', schema='marketing')
    op.drop_column('contact', 'dmachoice_pander_match', schema='marketing')
    op.drop_column('contact', 'responded_to_fax', schema='marketing')
    op.drop_column('contact', 'is_salesforce_sales_lead', schema='marketing')
    op.drop_column('contact', 'most_frequent_product_1', schema='marketing')
    op.drop_column('contact', 'subscription_total_dollars', schema='marketing')
    op.drop_column('contact', 'most_frequent_pricing_model', schema='marketing')
    op.drop_column('contact', 'email', schema='marketing')
    op.drop_column('contact', 'responded_to_telesale', schema='marketing')
    op.drop_column('contact', 'last_print_format', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_total_dollars', schema='marketing')
    op.drop_column('contact', 'telesales_average_order', schema='marketing')
    op.drop_column('contact', 'most_opened_email_product_1', schema='marketing')
    op.drop_column('contact', 'all_products_1', schema='marketing')
    op.drop_column('contact', 'suppress_direct_mail', schema='marketing')
    op.drop_column('contact', 'subscription_auto_renew', schema='marketing')
    op.drop_column('contact', 'telesales_max_order', schema='marketing')
    op.drop_column('contact', 'total_email_sends', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_end', schema='marketing')
    op.drop_column('contact', 'print_format_count', schema='marketing')
    op.drop_column('contact', 'print_digital_format_count', schema='marketing')
    op.drop_column('contact', 'carrier_route', schema='marketing')
    op.drop_column('contact', 'responded_to_catalogue', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_last_sku', schema='marketing')
    op.drop_column('contact', 'last_opened_email_product_2', schema='marketing')
    op.drop_column('contact', 'largest_dollar_amount', schema='marketing')
    op.drop_column('contact', 'responded_to_sales_channel', schema='marketing')
    op.drop_column('contact', 'generic_decile', schema='marketing')
    op.drop_column('contact', 'recency_months', schema='marketing')
    op.drop_column('contact', 'responded_to_usc', schema='marketing')
    op.drop_column('contact', 'original_product_1', schema='marketing')
    op.drop_column('contact', 'country', schema='marketing')
    op.drop_column('contact', 'last_email_open', schema='marketing')
    op.drop_column('contact', 'original_order_date', schema='marketing')
    op.drop_column('contact', 'bundles_format_count', schema='marketing')
    op.drop_column('contact', 'digital_format_count', schema='marketing')
    op.drop_column('contact', 'responded_to_direct_mail', schema='marketing')
    op.drop_column('contact', 'most_frequent_driving_tactic', schema='marketing')
    op.drop_column('contact', 'last_print_digital_format', schema='marketing')
    op.drop_column('contact', 'do_not_rent', schema='marketing')
    op.drop_column('contact', 'last_driver_channel', schema='marketing')
    op.drop_column('contact', 'last_order_dollars_group', schema='marketing')
    op.drop_column('contact', 'billing_marketing_driver', schema='marketing')
    op.drop_column('contact', 'responded_to_web', schema='marketing')
    op.drop_column('contact', 'is_academic_reseller', schema='marketing')
    op.drop_column('contact', 'most_frequent_product_2', schema='marketing')
    op.drop_column('contact', 'telesales_total_amount', schema='marketing')
    op.drop_column('contact', 'last_subscription_count', schema='marketing')
    op.drop_column('contact', 'telesales_frequency', schema='marketing')
    op.drop_column('contact', 'responded_to_email', schema='marketing')
    op.drop_column('contact', 'original_sku', schema='marketing')
    op.drop_column('contact', 'last_subscription_format', schema='marketing')
    op.drop_column('contact', 'prefix_description', schema='marketing')
    op.drop_column('contact', 'total_dollars_group', schema='marketing')
    op.drop_column('contact', 'frequency_group', schema='marketing')
    op.drop_column('contact', 'is_physician', schema='marketing')
    op.drop_column('contact', 'original_recency_group', schema='marketing')
    op.drop_column('contact', 'practice_marketing_driver', schema='marketing')
    op.drop_column('contact', 'primary_specialty', schema='marketing')
    op.drop_column('contact', 'last_digital_format', schema='marketing')
    op.drop_column('contact', 'delivery_point', schema='marketing')
    op.drop_column('contact', 'fax', schema='marketing')
    op.drop_column('contact', 'telesales_recency', schema='marketing')
    op.drop_column('contact', 'subscription_average_dollars', schema='marketing')
    op.drop_column('contact', 'last_bundle_format', schema='marketing')
    op.drop_column('contact', 'email_click_rate', schema='marketing')
    op.drop_column('contact', 'most_frequent_subscription_format', schema='marketing')
    op.drop_column('contact', 'state', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_max_order', schema='marketing')
    op.drop_column('contact', 'channel_type', schema='marketing')
    op.drop_column('contact', 'last_subscription_end', schema='marketing')
    op.drop_column('contact', 'data_file_format_count', schema='marketing')
    op.drop_column('contact', 'last_product_2', schema='marketing')
    op.drop_column('contact', 'do_not_mail', schema='marketing')
    op.drop_column('contact', 'direct_marketing_region', schema='marketing')
    op.drop_column('contact', 'total_email_unsubscribes', schema='marketing')
    op.drop_column('contact', 'most_opened_email_product_2', schema='marketing')
    op.drop_column('contact', 'last_channel', schema='marketing')
    op.drop_column('contact', 'frequency', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_average_dollars', schema='marketing')
    op.drop_column('contact', 'telesales_decile', schema='marketing')
    op.drop_column('contact', 'last_discount', schema='marketing')
    op.drop_column('contact', 'business_id', schema='marketing')
    op.drop_column('contact', 'cpt_assistance_frequency', schema='marketing')
    op.drop_column('contact', 'is_event_sales_lead', schema='marketing')
    op.drop_column('contact', 'last_audience', schema='marketing')
    op.drop_column('contact', 'address_2', schema='marketing')
    op.drop_column('contact', 'subscription_format_count', schema='marketing')
    op.drop_column('contact', 'total_email_clicks', schema='marketing')
    op.drop_column('contact', 'last_product_1', schema='marketing')
    op.drop_column('contact', 'responded_to_live_event', schema='marketing')
    op.drop_column('contact', 'most_frequent_driver_channel', schema='marketing')
    op.drop_column('contact', 'average_dollars_group', schema='marketing')
    op.drop_column('contact', 'address_1', schema='marketing')
    op.drop_column('contact', 'telesales_segment', schema='marketing')
    op.drop_column('contact', 'last_display_name', schema='marketing')
    op.drop_column('contact', 'training_marketing_driver', schema='marketing')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contact', sa.Column('training_marketing_driver', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_display_name', sa.VARCHAR(length=254), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_segment', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('address_1', sa.VARCHAR(length=255), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('average_dollars_group', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_driver_channel', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_live_event', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_product_1', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_email_clicks', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('subscription_format_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('address_2', sa.VARCHAR(length=255), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_audience', sa.VARCHAR(length=3), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('is_event_sales_lead', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_frequency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('business_id', sa.VARCHAR(length=10), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_discount', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_decile', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_average_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('frequency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_channel', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_opened_email_product_2', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_email_unsubscribes', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('direct_marketing_region', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('do_not_mail', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_product_2', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('data_file_format_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_subscription_end', postgresql.TIMESTAMP(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('channel_type', sa.VARCHAR(length=12), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_max_order', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('state', sa.VARCHAR(length=60), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_subscription_format', sa.VARCHAR(length=20), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('email_click_rate', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_bundle_format', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('subscription_average_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_recency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('fax', sa.VARCHAR(length=10), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('delivery_point', sa.VARCHAR(length=2), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_digital_format', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('primary_specialty', sa.VARCHAR(length=3), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('practice_marketing_driver', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_recency_group', sa.VARCHAR(length=5), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('is_physician', sa.BOOLEAN(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('frequency_group', sa.VARCHAR(length=3), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_dollars_group', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('prefix_description', sa.VARCHAR(length=8), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_subscription_format', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_sku', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_email', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_frequency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_subscription_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_total_amount', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_product_2', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('is_academic_reseller', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_web', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('billing_marketing_driver', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_order_dollars_group', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_driver_channel', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('do_not_rent', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_print_digital_format', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_driving_tactic', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_direct_mail', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('digital_format_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('bundles_format_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_order_date', sa.DATE(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_email_open', postgresql.TIMESTAMP(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('country', sa.VARCHAR(length=60), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_product_1', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_usc', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('recency_months', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('generic_decile', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_sales_channel', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('largest_dollar_amount', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_opened_email_product_2', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_last_sku', sa.VARCHAR(length=75), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_catalogue', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('carrier_route', sa.VARCHAR(length=4), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('print_digital_format_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('print_format_count', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_end', postgresql.TIMESTAMP(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_email_sends', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_max_order', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('subscription_auto_renew', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('suppress_direct_mail', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('all_products_1', sa.VARCHAR(length=250), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_opened_email_product_1', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_average_order', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_total_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_print_format', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_telesale', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('email', sa.VARCHAR(length=254), autoincrement=False, nullable=False), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_pricing_model', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('subscription_total_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_product_1', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('is_salesforce_sales_lead', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('responded_to_fax', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('dmachoice_pander_match', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('subscription_recency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_sku', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_email_bounces', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('buyer_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_last_term', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('recency_group', sa.VARCHAR(length=5), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('address_3', sa.VARCHAR(length=255), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('email_open_rate', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('do_not_email', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_opened_email_product_1', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('name', sa.VARCHAR(length=70), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_pricing_model', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('record_origin', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('telesales_score', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('secondary_specialty', sa.VARCHAR(length=3), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('industry_description', sa.VARCHAR(length=75), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('day_phone', sa.VARCHAR(length=11), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('record_sequence', sa.VARCHAR(length=10), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('average_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_sku', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('do_not_call', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('business_name', sa.VARCHAR(length=250), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('gender', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('business_title', sa.VARCHAR(length=70), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('evening_phone', sa.VARCHAR(length=11), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_recency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_product_2', sa.VARCHAR(length=40), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('coding_marketing_driver', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_order_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('suppress_email', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('list_keys', sa.VARCHAR(length=255), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('delivery_point_check_digit', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_subscription_start', postgresql.TIMESTAMP(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('subscription_frequency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('promotion_frequency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('documentation_marketing_driver', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('generic_score', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('is_member', sa.BOOLEAN(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('cpt_assistance_recency', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('title_description', sa.VARCHAR(length=75), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('suppress_telemarketing', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_driving_tactic', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_channel', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('all_products_2', sa.VARCHAR(length=250), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_discount', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('city', sa.VARCHAR(length=60), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('is_professional_reseller', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_email_open', postgresql.TIMESTAMP(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('zipcode', sa.VARCHAR(length=10), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_data_file_format', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('total_email_opens', sa.INTEGER(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('impairment_marketing_driver', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_order_date', sa.DATE(), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('email_match_or_append', sa.VARCHAR(length=1), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('most_frequent_audience', sa.VARCHAR(length=3), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('last_order_dollars', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True), schema='marketing')
    op.add_column('contact', sa.Column('original_order_dollars_group', sa.VARCHAR(length=7), autoincrement=False, nullable=True), schema='marketing')
    # ### end Alembic commands ###
