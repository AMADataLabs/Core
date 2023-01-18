"""Remove ME foreign key

Revision ID: 6f956fe11830
Revises: 26f01d3a67b3
Create Date: 2020-11-09 08:48:59.511187+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f956fe11830'
down_revision = '26f01d3a67b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('credentialing_order ', schema='oneview')
    op.drop_table('medical_education_physician', schema='oneview')

    op.drop_constraint('fk_physician_ethnicity_medical_education_number_physician', 'physician_ethnicity',
                       schema='oneview', type_='foreignkey')
    op.drop_constraint('fk_provider_medical_education_number_physician', 'provider', schema='oneview',
                       type_='foreignkey')
    op.alter_column('physician', 'medical_education_number',
                    existing_type=sa.INTEGER(),
                    type_=sa.String(),
                    existing_server_default=sa.text(
                        "nextval('oneview.physician_medical_education_number_seq'::regclass)"),
                    schema='oneview')
    op.create_table('credentialing_order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer', sa.Integer(), nullable=False),
    sa.Column('product', sa.Integer(), nullable=False),
    sa.Column('number', sa.String(), nullable=False),
    sa.Column('medical_education_number', sa.String(), nullable=False),
    sa.Column('date', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['customer'], ['oneview.credentialing_customer.id'], name=op.f('fk_credentialing_order_customer_credentialing_customer')),
    sa.ForeignKeyConstraint(['product'], ['oneview.credentialing_product.id'], name=op.f('fk_credentialing_order_product_credentialing_product')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_credentialing_order')),
    schema='oneview'
    )
    op.create_table('residency_program_physician',
    sa.Column('personnel_member', sa.Integer(), nullable=False),
    sa.Column('medical_education_number', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['personnel_member'], ['oneview.residency_program_personnel_member.id'], name=op.f('fk_residency_program_physician_personnel_member_residency_program_personnel_member')),
    sa.PrimaryKeyConstraint('personnel_member', name=op.f('pk_residency_program_physician')),
    schema='oneview'
    )

    op.alter_column('physician_ethnicity', 'medical_education_number',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               schema='oneview')

    op.alter_column('provider', 'medical_education_number',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False,
               schema='oneview')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('fk_provider_medical_education_number_physician', 'provider', 'physician', ['medical_education_number'], ['medical_education_number'], source_schema='oneview', referent_schema='oneview')
    op.alter_column('provider', 'medical_education_number',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               schema='oneview')
    op.create_foreign_key('fk_physician_ethnicity_medical_education_number_physician', 'physician_ethnicity', 'physician', ['medical_education_number'], ['medical_education_number'], source_schema='oneview', referent_schema='oneview')
    op.alter_column('physician_ethnicity', 'medical_education_number',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               schema='oneview')
    op.alter_column('physician', 'medical_education_number',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_server_default=sa.text("nextval('oneview.physician_medical_education_number_seq'::regclass)"),
               schema='oneview')
    op.create_table('medical_education_physician',
    sa.Column('medical_education_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('personnel_member', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['medical_education_number'], ['oneview.physician.medical_education_number'], name='fk_medical_education_physician_medical_education_number_b729'),
    sa.ForeignKeyConstraint(['personnel_member'], ['oneview.residency_program_personnel_member.id'], name='fk_medical_education_physician_personnel_member_residen_462a'),
    schema='oneview'
    )
    op.create_table('credentialing_order ',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'oneview."credentialing_order _id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('number', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('medical_education_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('customer', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['customer'], ['oneview.credentialing_customer.id'], name='fk_credentialing_order _customer_credentialing_customer'),
    sa.ForeignKeyConstraint(['medical_education_number'], ['oneview.physician.medical_education_number'], name='fk_credentialing_order _medical_education_number_physician'),
    sa.ForeignKeyConstraint(['product'], ['oneview.credentialing_product.id'], name='fk_credentialing_order _product_credentialing_product'),
    sa.PrimaryKeyConstraint('id', name='pk_credentialing_order '),
    schema='oneview'
    )
    op.drop_table('residency_program_physician', schema='oneview')
    op.drop_table('credentialing_order', schema='oneview')
    # ### end Alembic commands ###