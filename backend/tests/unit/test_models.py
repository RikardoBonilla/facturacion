"""
Unit tests for SQLAlchemy models
"""

import pytest
from decimal import Decimal
from datetime import date

from app.models import Empresa, Cliente, Producto, Factura, FacturaDetalle, Usuario


class TestEmpresaModel:
    """Test cases for Empresa model"""

    @pytest.mark.unit
    def test_empresa_creation(self):
        """Test creating an Empresa instance"""
        empresa = Empresa(
            nit="900123456-1",
            razon_social="Test Company S.A.S.",
            direccion="Test Address 123",
            ciudad="Bogotá",
            departamento="Cundinamarca",
            email="test@company.com",
            tipo_contribuyente="PERSONA_JURIDICA",
            regimen_fiscal="COMUN"
        )
        
        assert empresa.nit == "900123456-1"
        assert empresa.razon_social == "Test Company S.A.S."
        assert empresa.tipo_contribuyente == "PERSONA_JURIDICA"
        assert empresa.regimen_fiscal == "COMUN"
        assert empresa.activo is True  # Default value

    @pytest.mark.unit
    def test_empresa_repr(self):
        """Test Empresa string representation"""
        empresa = Empresa(
            id=1,
            nit="900123456-1",
            razon_social="Test Company S.A.S.",
            direccion="Test Address",
            ciudad="Bogotá",
            departamento="Cundinamarca",
            email="test@company.com",
            tipo_contribuyente="PERSONA_JURIDICA",
            regimen_fiscal="COMUN"
        )
        
        expected = "<Empresa(id=1, nit='900123456-1', razon_social='Test Company S.A.S.')>"
        assert repr(empresa) == expected

    @pytest.mark.unit
    def test_empresa_defaults(self):
        """Test Empresa default values"""
        empresa = Empresa(
            nit="900123456-1",
            razon_social="Test Company",
            direccion="Address",
            ciudad="City",
            departamento="Department",
            email="test@email.com",
            tipo_contribuyente="PERSONA_JURIDICA",
            regimen_fiscal="COMUN"
        )
        
        assert empresa.activo is True
        assert empresa.ambiente_dian == "PRUEBAS"


class TestClienteModel:
    """Test cases for Cliente model"""

    @pytest.mark.unit
    def test_cliente_creation_natural(self):
        """Test creating a natural person client"""
        cliente = Cliente(
            empresa_id=1,
            tipo_persona="NATURAL",
            tipo_documento="CC",
            numero_documento="12345678",
            primer_nombre="Juan",
            primer_apellido="Pérez",
            direccion="Calle 123",
            ciudad="Bogotá",
            departamento="Cundinamarca"
        )
        
        assert cliente.tipo_persona == "NATURAL"
        assert cliente.tipo_documento == "CC"
        assert cliente.primer_nombre == "Juan"
        assert cliente.activo is True

    @pytest.mark.unit
    def test_cliente_creation_juridica(self):
        """Test creating a juridical person client"""
        cliente = Cliente(
            empresa_id=1,
            tipo_persona="JURIDICA",
            tipo_documento="NIT",
            numero_documento="900123456-1",
            razon_social="Cliente Corp S.A.S.",
            direccion="Carrera 50",
            ciudad="Medellín",
            departamento="Antioquia"
        )
        
        assert cliente.tipo_persona == "JURIDICA"
        assert cliente.razon_social == "Cliente Corp S.A.S."
        assert cliente.primer_nombre is None

    @pytest.mark.unit
    def test_cliente_get_nombre_completo_natural(self):
        """Test getting full name for natural person"""
        cliente = Cliente(
            empresa_id=1,
            tipo_persona="NATURAL",
            tipo_documento="CC",
            numero_documento="12345678",
            primer_nombre="Juan",
            segundo_nombre="Carlos",
            primer_apellido="Pérez",
            segundo_apellido="García",
            direccion="Address",
            ciudad="City",
            departamento="Department"
        )
        
        nombre_completo = cliente.get_nombre_completo()
        assert nombre_completo == "Juan Carlos Pérez García"

    @pytest.mark.unit
    def test_cliente_get_nombre_completo_juridica(self):
        """Test getting full name for juridical person"""
        cliente = Cliente(
            empresa_id=1,
            tipo_persona="JURIDICA",
            tipo_documento="NIT",
            numero_documento="900123456-1",
            razon_social="Mi Empresa S.A.S.",
            nombre_comercial="Mi Empresa",
            direccion="Address",
            ciudad="City",
            departamento="Department"
        )
        
        nombre_completo = cliente.get_nombre_completo()
        assert nombre_completo == "Mi Empresa S.A.S."

    @pytest.mark.unit
    def test_cliente_get_nombre_completo_partial(self):
        """Test getting full name with partial data"""
        cliente = Cliente(
            empresa_id=1,
            tipo_persona="NATURAL",
            tipo_documento="CC",
            numero_documento="12345678",
            primer_nombre="Juan",
            primer_apellido="Pérez",
            direccion="Address",
            ciudad="City",
            departamento="Department"
        )
        
        nombre_completo = cliente.get_nombre_completo()
        assert nombre_completo == "Juan Pérez"

    @pytest.mark.unit
    def test_cliente_repr(self):
        """Test Cliente string representation"""
        cliente = Cliente(
            id=1,
            empresa_id=1,
            tipo_persona="NATURAL",
            tipo_documento="CC",
            numero_documento="12345678",
            primer_nombre="Juan",
            primer_apellido="Pérez",
            direccion="Address",
            ciudad="City",
            departamento="Department"
        )
        
        expected = "<Cliente(id=1, documento='12345678', nombre='Juan Pérez')>"
        assert repr(cliente) == expected


class TestProductoModel:
    """Test cases for Producto model"""

    @pytest.mark.unit
    def test_producto_creation(self):
        """Test creating a Producto instance"""
        producto = Producto(
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI"
        )
        
        assert producto.codigo == "PROD001"
        assert producto.precio_unitario == Decimal("100.00")
        assert producto.incluye_iva is True  # Default
        assert producto.porcentaje_iva == Decimal("19.00")  # Default

    @pytest.mark.unit
    def test_producto_get_precio_con_impuestos_solo_iva(self):
        """Test price calculation with only IVA"""
        producto = Producto(
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI",
            incluye_iva=True,
            porcentaje_iva=Decimal("19.00"),
            incluye_inc=False,
            incluye_ica=False
        )
        
        precio_con_impuestos = producto.get_precio_con_impuestos()
        expected = 100.00 * 1.19  # 119.00
        assert precio_con_impuestos == expected

    @pytest.mark.unit
    def test_producto_get_precio_con_impuestos_todos(self):
        """Test price calculation with all taxes"""
        producto = Producto(
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI",
            incluye_iva=True,
            porcentaje_iva=Decimal("19.00"),
            incluye_inc=True,
            porcentaje_inc=Decimal("8.00"),
            incluye_ica=True,
            porcentaje_ica=Decimal("1.00")
        )
        
        precio_con_impuestos = producto.get_precio_con_impuestos()
        # 100 * 1.19 * 1.08 * 1.01 = 129.73
        expected = round(100.00 * 1.19 * 1.08 * 1.01, 2)
        assert precio_con_impuestos == expected

    @pytest.mark.unit
    def test_producto_get_precio_sin_impuestos(self):
        """Test price calculation without taxes"""
        producto = Producto(
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI",
            incluye_iva=False,
            incluye_inc=False,
            incluye_ica=False
        )
        
        precio_con_impuestos = producto.get_precio_con_impuestos()
        assert precio_con_impuestos == 100.00

    @pytest.mark.unit
    def test_producto_defaults(self):
        """Test Producto default values"""
        producto = Producto(
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI"
        )
        
        assert producto.activo is True
        assert producto.incluye_iva is True
        assert producto.porcentaje_iva == Decimal("19.00")
        assert producto.incluye_inc is False
        assert producto.porcentaje_inc == Decimal("0.00")
        assert producto.maneja_inventario is False
        assert producto.stock_actual == 0

    @pytest.mark.unit
    def test_producto_repr(self):
        """Test Producto string representation"""
        producto = Producto(
            id=1,
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI"
        )
        
        expected = "<Producto(id=1, codigo='PROD001', nombre='Test Product')>"
        assert repr(producto) == expected


class TestFacturaModel:
    """Test cases for Factura model"""

    @pytest.mark.unit
    def test_factura_creation(self):
        """Test creating a Factura instance"""
        factura = Factura(
            empresa_id=1,
            cliente_id=1,
            numero=1,
            numero_completo="FT001",
            fecha_emision=date(2024, 1, 15)
        )
        
        assert factura.numero == 1
        assert factura.numero_completo == "FT001"
        assert factura.estado_dian == "BORRADOR"  # Default
        assert factura.activo is True

    @pytest.mark.unit
    def test_factura_totales_defaults(self):
        """Test Factura default totals"""
        factura = Factura(
            empresa_id=1,
            cliente_id=1,
            numero=1,
            numero_completo="FT001",
            fecha_emision=date(2024, 1, 15)
        )
        
        assert factura.subtotal == Decimal("0.00")
        assert factura.total_descuentos == Decimal("0.00")
        assert factura.total_iva == Decimal("0.00")
        assert factura.total_inc == Decimal("0.00")
        assert factura.total_ica == Decimal("0.00")
        assert factura.total_impuestos == Decimal("0.00")
        assert factura.total_factura == Decimal("0.00")

    @pytest.mark.unit
    def test_factura_repr(self):
        """Test Factura string representation"""
        factura = Factura(
            id=1,
            empresa_id=1,
            cliente_id=1,
            numero=1,
            numero_completo="FT001",
            fecha_emision=date(2024, 1, 15),
            total_factura=Decimal("119.00")
        )
        
        expected = "<Factura(id=1, numero='FT001', total=119.00)>"
        assert repr(factura) == expected


class TestFacturaDetalleModel:
    """Test cases for FacturaDetalle model"""

    @pytest.mark.unit
    def test_factura_detalle_creation(self):
        """Test creating a FacturaDetalle instance"""
        detalle = FacturaDetalle(
            factura_id=1,
            producto_id=1,
            codigo_producto="PROD001",
            nombre_producto="Test Product",
            cantidad=Decimal("2.000"),
            precio_unitario=Decimal("100.00"),
            subtotal_linea=Decimal("200.00"),
            total_descuentos_linea=Decimal("0.00"),
            total_impuestos_linea=Decimal("38.00"),
            total_linea=Decimal("238.00")
        )
        
        assert detalle.cantidad == Decimal("2.000")
        assert detalle.precio_unitario == Decimal("100.00")
        assert detalle.subtotal_linea == Decimal("200.00")
        assert detalle.descuento_porcentaje == Decimal("0.00")  # Default

    @pytest.mark.unit
    def test_factura_detalle_repr(self):
        """Test FacturaDetalle string representation"""
        detalle = FacturaDetalle(
            id=1,
            factura_id=1,
            producto_id=1,
            codigo_producto="PROD001",
            nombre_producto="Test Product",
            cantidad=Decimal("2.000"),
            precio_unitario=Decimal("100.00"),
            subtotal_linea=Decimal("200.00"),
            total_descuentos_linea=Decimal("0.00"),
            total_impuestos_linea=Decimal("38.00"),
            total_linea=Decimal("238.00")
        )
        
        expected = "<FacturaDetalle(id=1, producto='Test Product', cantidad=2.000)>"
        assert repr(detalle) == expected


class TestUsuarioModel:
    """Test cases for Usuario model"""

    @pytest.mark.unit
    def test_usuario_creation(self):
        """Test creating a Usuario instance"""
        usuario = Usuario(
            empresa_id=1,
            email="test@empresa.com",
            password_hash="hashed_password",
            nombre="Test",
            apellido="User",
            tipo_documento="CC",
            numero_documento="12345678",
            rol_id=1
        )
        
        assert usuario.email == "test@empresa.com"
        assert usuario.nombre == "Test"
        assert usuario.apellido == "User"
        assert usuario.activo is True  # Default

    @pytest.mark.unit
    def test_usuario_repr(self):
        """Test Usuario string representation"""
        usuario = Usuario(
            id=1,
            empresa_id=1,
            email="test@empresa.com",
            password_hash="hashed_password",
            nombre="Test",
            apellido="User",
            tipo_documento="CC",
            numero_documento="12345678",
            rol_id=1
        )
        
        expected = "<Usuario(id=1, email='test@empresa.com', nombre='Test')>"
        assert repr(usuario) == expected


class TestModelRelationships:
    """Test model relationships and foreign keys"""

    @pytest.mark.unit
    def test_cliente_empresa_relationship(self):
        """Test Cliente-Empresa relationship attributes"""
        cliente = Cliente(
            empresa_id=1,
            tipo_persona="NATURAL",
            tipo_documento="CC",
            numero_documento="12345678",
            direccion="Address",
            ciudad="City",
            departamento="Department"
        )
        
        # Test that foreign key is set
        assert cliente.empresa_id == 1
        
        # Test that relationship attribute exists
        assert hasattr(cliente, 'empresa')
        assert hasattr(cliente, 'facturas')

    @pytest.mark.unit
    def test_producto_empresa_relationship(self):
        """Test Producto-Empresa relationship attributes"""
        producto = Producto(
            empresa_id=1,
            codigo="PROD001",
            nombre="Test Product",
            tipo="PRODUCTO",
            precio_unitario=Decimal("100.00"),
            unidad_medida="UNI"
        )
        
        assert producto.empresa_id == 1
        assert hasattr(producto, 'empresa')
        assert hasattr(producto, 'detalles_factura')

    @pytest.mark.unit
    def test_factura_relationships(self):
        """Test Factura relationship attributes"""
        factura = Factura(
            empresa_id=1,
            cliente_id=1,
            numero=1,
            numero_completo="FT001",
            fecha_emision=date(2024, 1, 15)
        )
        
        assert factura.empresa_id == 1
        assert factura.cliente_id == 1
        assert hasattr(factura, 'empresa')
        assert hasattr(factura, 'cliente')
        assert hasattr(factura, 'detalles')
        assert hasattr(factura, 'impuestos')