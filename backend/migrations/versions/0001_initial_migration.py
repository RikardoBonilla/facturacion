"""Initial migration: Create all tables for Colombian invoicing system

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )

    # Create permisos table
    op.create_table('permisos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('modulo', sa.String(length=50), nullable=False),
        sa.Column('accion', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('modulo', 'accion')
    )

    # Create rol_permisos table
    op.create_table('rol_permisos',
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('permiso_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permiso_id'], ['permisos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('rol_id', 'permiso_id')
    )

    # Create empresas table
    op.create_table('empresas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nit', sa.String(length=20), nullable=False),
        sa.Column('razon_social', sa.String(length=200), nullable=False),
        sa.Column('nombre_comercial', sa.String(length=200), nullable=True),
        sa.Column('direccion', sa.Text(), nullable=False),
        sa.Column('ciudad', sa.String(length=100), nullable=False),
        sa.Column('departamento', sa.String(length=100), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('tipo_contribuyente', sa.String(length=50), nullable=False),
        sa.Column('regimen_fiscal', sa.String(length=50), nullable=False),
        sa.Column('responsabilidades_fiscales', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('ambiente_dian', sa.String(length=20), nullable=False, default='PRUEBAS'),
        sa.Column('prefijo_factura', sa.String(length=10), nullable=True),
        sa.Column('resolucion_dian', sa.String(length=50), nullable=True),
        sa.Column('fecha_resolucion', sa.Date(), nullable=True),
        sa.Column('rango_autorizado_desde', sa.Integer(), nullable=True),
        sa.Column('rango_autorizado_hasta', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nit')
    )
    op.create_index(op.f('ix_empresas_nit'), 'empresas', ['nit'], unique=False)

    # Create usuarios table
    op.create_table('usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellido', sa.String(length=100), nullable=False),
        sa.Column('tipo_documento', sa.String(length=20), nullable=False),
        sa.Column('numero_documento', sa.String(length=20), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('ultimo_acceso', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=False)

    # Create sesiones table
    op.create_table('sesiones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('fecha_expiracion', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    # Create clientes table
    op.create_table('clientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('tipo_persona', sa.String(length=20), nullable=False),
        sa.Column('tipo_documento', sa.String(length=20), nullable=False),
        sa.Column('numero_documento', sa.String(length=20), nullable=False),
        sa.Column('razon_social', sa.String(length=200), nullable=True),
        sa.Column('nombre_comercial', sa.String(length=200), nullable=True),
        sa.Column('primer_nombre', sa.String(length=50), nullable=True),
        sa.Column('segundo_nombre', sa.String(length=50), nullable=True),
        sa.Column('primer_apellido', sa.String(length=50), nullable=True),
        sa.Column('segundo_apellido', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('direccion', sa.Text(), nullable=False),
        sa.Column('ciudad', sa.String(length=100), nullable=False),
        sa.Column('departamento', sa.String(length=100), nullable=False),
        sa.Column('codigo_postal', sa.String(length=10), nullable=True),
        sa.Column('regimen_fiscal', sa.String(length=50), nullable=True),
        sa.Column('responsabilidad_tributaria', sa.String(length=10), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clientes_numero_documento'), 'clientes', ['numero_documento'], unique=False)

    # Create productos table
    op.create_table('productos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('nombre', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('codigo_unspsc', sa.String(length=20), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('precio_compra', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('unidad_medida', sa.String(length=20), nullable=False),
        sa.Column('incluye_iva', sa.Boolean(), nullable=False, default=True),
        sa.Column('porcentaje_iva', sa.Numeric(precision=5, scale=2), nullable=False, default=19.00),
        sa.Column('incluye_inc', sa.Boolean(), nullable=False, default=False),
        sa.Column('porcentaje_inc', sa.Numeric(precision=5, scale=2), nullable=False, default=0.00),
        sa.Column('incluye_ica', sa.Boolean(), nullable=False, default=False),
        sa.Column('porcentaje_ica', sa.Numeric(precision=5, scale=2), nullable=False, default=0.00),
        sa.Column('maneja_inventario', sa.Boolean(), nullable=False, default=False),
        sa.Column('stock_actual', sa.Integer(), nullable=True, default=0),
        sa.Column('stock_minimo', sa.Integer(), nullable=True, default=0),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_productos_codigo'), 'productos', ['codigo'], unique=False)

    # Create facturas table
    op.create_table('facturas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('prefijo', sa.String(length=10), nullable=True),
        sa.Column('numero', sa.Integer(), nullable=False),
        sa.Column('numero_completo', sa.String(length=20), nullable=False),
        sa.Column('fecha_emision', sa.Date(), nullable=False),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=True),
        sa.Column('cufe', sa.String(length=96), nullable=True),
        sa.Column('qr_code', sa.Text(), nullable=True),
        sa.Column('xml_content', sa.Text(), nullable=True),
        sa.Column('estado_dian', sa.String(length=20), nullable=False, default='BORRADOR'),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_descuentos', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_iva', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_inc', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_ica', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_impuestos', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_factura', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facturas_cufe'), 'facturas', ['cufe'], unique=False)
    op.create_index(op.f('ix_facturas_numero_completo'), 'facturas', ['numero_completo'], unique=False)

    # Create factura_detalle table
    op.create_table('factura_detalle',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('factura_id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('codigo_producto', sa.String(length=50), nullable=False),
        sa.Column('nombre_producto', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('cantidad', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('descuento_porcentaje', sa.Numeric(precision=5, scale=2), nullable=False, default=0),
        sa.Column('descuento_valor', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('subtotal_linea', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_descuentos_linea', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_impuestos_linea', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_linea', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['factura_id'], ['facturas.id'], ),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create factura_impuestos table
    op.create_table('factura_impuestos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('factura_id', sa.Integer(), nullable=False),
        sa.Column('tipo_impuesto', sa.String(length=10), nullable=False),
        sa.Column('porcentaje', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('base_gravable', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('valor_impuesto', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['factura_id'], ['facturas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create triggers for updated_at timestamps
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    # Add triggers to tables with updated_at columns
    for table in ['empresas', 'usuarios', 'clientes', 'productos', 'facturas']:
        op.execute(f"""
        CREATE TRIGGER update_{table}_updated_at 
        BEFORE UPDATE ON {table} 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ['empresas', 'usuarios', 'clientes', 'productos', 'facturas']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")
    
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Drop tables in reverse order
    op.drop_table('factura_impuestos')
    op.drop_table('factura_detalle')
    op.drop_index(op.f('ix_facturas_numero_completo'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_cufe'), table_name='facturas')
    op.drop_table('facturas')
    op.drop_index(op.f('ix_productos_codigo'), table_name='productos')
    op.drop_table('productos')
    op.drop_index(op.f('ix_clientes_numero_documento'), table_name='clientes')
    op.drop_table('clientes')
    op.drop_table('sesiones')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_index(op.f('ix_empresas_nit'), table_name='empresas')
    op.drop_table('empresas')
    op.drop_table('rol_permisos')
    op.drop_table('permisos')
    op.drop_table('roles')