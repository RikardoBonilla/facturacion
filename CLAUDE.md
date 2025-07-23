# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Colombian electronic invoicing system database schema designed for PostgreSQL. The system implements DIAN (Dirección de Impuestos y Aduanas Nacionales) compliance for electronic invoicing in Colombia.

## Database Architecture

The system is built around a multi-tenant PostgreSQL database with the following core modules:

### Security & User Management
- **empresas**: Multi-tenant company management with DIAN configuration
- **usuarios**: User management with role-based permissions
- **roles/permisos**: RBAC system with granular permissions
- **sesiones**: Session management for authentication

### Invoicing Core
- **facturas**: Main invoice table with DIAN compliance fields (CUFE, XML, QR codes)
- **factura_detalle**: Invoice line items
- **factura_impuestos**: Tax calculations per invoice
- **clientes**: Colombian customer data with proper document types
- **productos**: Product/service catalog with UNSPSC codes

### Colombian Tax Compliance
- **impuestos**: Colombian tax definitions (IVA, INC, ICA)
- Built-in support for Colombian fiscal responsibilities
- DIAN electronic invoicing workflow integration

## Key Features

- **Multi-tenant architecture**: Single database serving multiple companies
- **Colombian compliance**: Full DIAN integration for electronic invoicing
- **Audit trail**: Complete transaction auditing with triggers
- **Automatic numbering**: Consecutive invoice numbering per company
- **Tax calculations**: Automated Colombian tax computations

## Database Setup

```sql
-- Run the main schema file
psql -U postgres -d your_database < facturacion.sql
```

## Key Views

- `v_facturas_completas`: Complete invoice information with customer data
- `v_usuario_permisos`: User permissions flattened view

## Important Functions

- `generar_numero_factura()`: Generates consecutive invoice numbers
- `fn_auditoria()`: Automatic audit trail trigger
- `update_updated_at()`: Timestamp update trigger

## Colombian Specific Features

- Document types: NIT, CC, CE, PASAPORTE
- Tax types: IVA (0%, 5%, 19%), INC, ICA
- DIAN states: BORRADOR, EMITIDA, ACEPTADA, RECHAZADA, ANULADA
- Fiscal regimes: SIMPLIFICADO, COMÚN
- Person types: NATURAL, JURÍDICA

## Multi-tenant Considerations

All operations should be scoped by `empresa_id` to ensure proper data isolation between companies.