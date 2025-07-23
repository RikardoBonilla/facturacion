"""
Performance tests for the Colombian Electronic Invoicing System
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from fastapi import status
from concurrent.futures import ThreadPoolExecutor
import statistics

from app.models import Cliente, Producto, Factura, Usuario


class TestAPIPerformance:
    """Test API endpoint performance"""

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_empresa_list_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test empresa listing endpoint performance"""
        
        # Warm up
        await async_client.get("/api/v1/empresas/", headers=authenticated_headers)
        
        # Measure performance
        start_time = time.time()
        response = await async_client.get("/api/v1/empresas/", headers=authenticated_headers)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert execution_time < 1.0  # Should complete within 1 second

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_bulk_cliente_creation_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test performance of creating multiple clientes"""
        
        num_clientes = 50
        start_time = time.time()
        
        tasks = []
        for i in range(num_clientes):
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": f"1234567{i:02d}",
                "primer_nombre": f"Cliente{i}",
                "primer_apellido": "TestPerf",
                "direccion": f"Calle {i}",
                "ciudad": "Bogotá",
                "departamento": "Cundinamarca"
            }
            
            task = async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        execution_time = end_time - start_time
        successful_requests = sum(1 for r in responses if r.status_code == 201)
        
        assert successful_requests == num_clientes
        assert execution_time < 10.0  # Should complete within 10 seconds
        
        # Calculate requests per second
        rps = num_clientes / execution_time
        assert rps > 5  # At least 5 requests per second

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_bulk_producto_creation_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test performance of creating multiple productos"""
        
        num_productos = 30
        start_time = time.time()
        
        tasks = []
        for i in range(num_productos):
            producto_data = {
                "codigo": f"PERF{i:03d}",
                "nombre": f"Producto Performance {i}",
                "tipo": "PRODUCTO",
                "precio_unitario": 50000.00 + (i * 1000),
                "unidad_medida": "UNI"
            }
            
            task = async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        execution_time = end_time - start_time
        successful_requests = sum(1 for r in responses if r.status_code == 201)
        
        assert successful_requests == num_productos
        assert execution_time < 8.0  # Should complete within 8 seconds

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_complex_factura_creation_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test performance of creating complex facturas"""
        
        # Create additional products for complex factura
        productos = [test_producto]
        for i in range(5):
            producto_data = {
                "codigo": f"COMPLEX{i}",
                "nombre": f"Producto Complejo {i}",
                "tipo": "PRODUCTO",
                "precio_unitario": 75000.00 + (i * 5000),
                "unidad_medida": "UNI"
            }
            
            response = await async_client.post(
                "/api/v1/productos/",
                json=producto_data,
                headers=authenticated_headers
            )
            productos.append({"id": response.json()["id"]})
        
        # Create complex factura with multiple items
        start_time = time.time()
        
        factura_data = {
            "cliente_id": test_cliente.id,
            "fecha_emision": "2024-01-15",
            "observaciones": "Factura compleja para pruebas de rendimiento",
            "detalles": [
                {
                    "producto_id": producto["id"] if isinstance(producto, dict) else producto.id,
                    "cantidad": 2.0 + i,
                    "precio_unitario": 50000.00 + (i * 10000),
                    "descuento_porcentaje": i * 2.0
                }
                for i, producto in enumerate(productos)
            ]
        }
        
        response = await async_client.post(
            "/api/v1/facturas/",
            json=factura_data,
            headers=authenticated_headers
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == status.HTTP_201_CREATED
        assert execution_time < 3.0  # Should complete within 3 seconds
        
        # Verify calculations are correct
        data = response.json()
        assert len(data["detalles"]) == len(productos)
        assert float(data["total_factura"]) > 0

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_factura_listing_with_pagination_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test performance of listing facturas with pagination"""
        
        # Create multiple facturas for pagination test
        num_facturas = 20
        creation_tasks = []
        
        for i in range(num_facturas):
            factura_data = {
                "cliente_id": test_cliente.id,
                "fecha_emision": "2024-01-15",
                "observaciones": f"Factura pagination test {i}",
                "detalles": [
                    {
                        "producto_id": test_producto.id,
                        "cantidad": 1.0,
                        "precio_unitario": 50000.00
                    }
                ]
            }
            
            task = async_client.post(
                "/api/v1/facturas/",
                json=factura_data,
                headers=authenticated_headers
            )
            creation_tasks.append(task)
        
        # Wait for all facturas to be created
        await asyncio.gather(*creation_tasks)
        
        # Test pagination performance
        start_time = time.time()
        
        response = await async_client.get(
            "/api/v1/facturas/?limit=10&offset=0",
            headers=authenticated_headers
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert execution_time < 2.0  # Should complete within 2 seconds
        
        data = response.json()
        assert len(data) <= 10  # Respects limit


class TestConcurrentOperations:
    """Test system performance under concurrent load"""

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_cliente_creation(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test concurrent cliente creation performance"""
        
        num_concurrent = 20
        start_time = time.time()
        
        async def create_cliente(index):
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": f"9876543{index:02d}",
                "primer_nombre": f"Concurrent{index}",
                "primer_apellido": "Test",
                "direccion": f"Concurrent Address {index}",
                "ciudad": "Medellín",
                "departamento": "Antioquia"
            }
            
            return await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
        
        tasks = [create_cliente(i) for i in range(num_concurrent)]
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        successful_requests = sum(1 for r in responses if r.status_code == 201)
        assert successful_requests == num_concurrent
        assert execution_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_read_operations(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test concurrent read operations performance"""
        
        num_concurrent = 50
        endpoints = [
            "/api/v1/empresas/",
            "/api/v1/clientes/",
            "/api/v1/productos/",
            "/api/v1/facturas/"
        ]
        
        start_time = time.time()
        
        async def make_request(endpoint):
            return await async_client.get(endpoint, headers=authenticated_headers)
        
        # Create concurrent requests to different endpoints
        tasks = []
        for i in range(num_concurrent):
            endpoint = endpoints[i % len(endpoints)]
            tasks.append(make_request(endpoint))
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        execution_time = end_time - start_time
        successful_requests = sum(1 for r in responses if r.status_code == 200)
        
        assert successful_requests == num_concurrent
        assert execution_time < 3.0  # Should complete within 3 seconds

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_mixed_operations_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test mixed read/write operations performance"""
        
        start_time = time.time()
        
        async def create_factura():
            factura_data = {
                "cliente_id": test_cliente.id,
                "fecha_emision": "2024-01-15",
                "detalles": [
                    {
                        "producto_id": test_producto.id,
                        "cantidad": 1.0,
                        "precio_unitario": 50000.00
                    }
                ]
            }
            return await async_client.post(
                "/api/v1/facturas/",
                json=factura_data,
                headers=authenticated_headers
            )
        
        async def read_facturas():
            return await async_client.get(
                "/api/v1/facturas/",
                headers=authenticated_headers
            )
        
        # Mix of create and read operations
        tasks = []
        for i in range(10):
            if i % 2 == 0:
                tasks.append(create_factura())
            else:
                tasks.append(read_facturas())
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        execution_time = end_time - start_time
        successful_requests = sum(1 for r in responses if r.status_code in [200, 201])
        
        assert successful_requests == len(tasks)
        assert execution_time < 8.0  # Should complete within 8 seconds


class TestDatabasePerformance:
    """Test database operation performance"""

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_search_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test search operation performance"""
        
        # Create test data for search
        for i in range(20):
            cliente_data = {
                "tipo_persona": "NATURAL",
                "tipo_documento": "CC",
                "numero_documento": f"5555555{i:02d}",
                "primer_nombre": f"Search{i}",
                "primer_apellido": "Performance",
                "direccion": f"Search Address {i}",
                "ciudad": "Cali",
                "departamento": "Valle del Cauca"
            }
            
            await async_client.post(
                "/api/v1/clientes/",
                json=cliente_data,
                headers=authenticated_headers
            )
        
        # Test search performance
        start_time = time.time()
        
        response = await async_client.get(
            "/api/v1/clientes/?search=Search",
            headers=authenticated_headers
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert execution_time < 1.0  # Should complete within 1 second

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_complex_query_performance(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test complex query performance"""
        
        start_time = time.time()
        
        # Complex query with multiple filters
        response = await async_client.get(
            "/api/v1/facturas/?estado_dian=BORRADOR&fecha_inicio=2024-01-01&fecha_fin=2024-12-31",
            headers=authenticated_headers
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert execution_time < 2.0  # Should complete within 2 seconds


class TestMemoryUsage:
    """Test memory usage patterns"""

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.memory
    @pytest.mark.asyncio
    async def test_large_dataset_handling(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test handling of large datasets without memory issues"""
        
        # This test would monitor memory usage during large operations
        # In a real implementation, you'd use memory profiling tools
        
        start_time = time.time()
        
        # Request large dataset
        response = await async_client.get(
            "/api/v1/facturas/?limit=1000",
            headers=authenticated_headers
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert execution_time < 5.0  # Should complete within 5 seconds
        
        # Verify response size is reasonable
        data = response.json()
        assert isinstance(data, list)


class TestResponseTimes:
    """Test response time consistency"""

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_consistency(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test that response times are consistent across multiple requests"""
        
        num_requests = 20
        response_times = []
        
        for _ in range(num_requests):
            start_time = time.time()
            
            response = await async_client.get(
                "/api/v1/empresas/",
                headers=authenticated_headers
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            assert response.status_code == status.HTTP_200_OK
            response_times.append(execution_time)
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        # Assertions for performance consistency
        assert avg_time < 1.0  # Average response time should be under 1 second
        assert max_time < 2.0  # No request should take more than 2 seconds
        assert std_dev < 0.5   # Standard deviation should be low (consistent times)

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_authentication_performance(
        self, 
        async_client: AsyncClient,
        test_usuario: Usuario
    ):
        """Test authentication endpoint performance"""
        
        num_logins = 10
        response_times = []
        
        for _ in range(num_logins):
            login_data = {
                "username": test_usuario.email,
                "password": "testpass123"
            }
            
            start_time = time.time()
            
            response = await async_client.post(
                "/api/v1/auth/login",
                data=login_data
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            assert response.status_code == status.HTTP_200_OK
            response_times.append(execution_time)
        
        avg_time = statistics.mean(response_times)
        assert avg_time < 0.5  # Authentication should be fast


class TestScalabilityIndicators:
    """Test indicators of system scalability"""

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_throughput_measurement(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Measure system throughput under load"""
        
        duration = 5  # seconds
        request_count = 0
        start_time = time.time()
        
        async def make_request():
            nonlocal request_count
            response = await async_client.get(
                "/api/v1/empresas/",
                headers=authenticated_headers
            )
            if response.status_code == 200:
                request_count += 1
        
        # Generate load for specified duration
        tasks = []
        while time.time() - start_time < duration:
            tasks.append(make_request())
            await asyncio.sleep(0.1)  # Small delay between requests
        
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        throughput = request_count / total_time
        
        # Should handle at least 10 requests per second
        assert throughput >= 10

    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_resource_utilization_under_load(
        self, 
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_cliente: Cliente,
        test_producto: Producto
    ):
        """Test resource utilization under various load patterns"""
        
        # Create load with different operation types
        tasks = []
        
        # Read operations (should be fast)
        for _ in range(20):
            tasks.append(
                async_client.get("/api/v1/clientes/", headers=authenticated_headers)
            )
        
        # Write operations (slower)
        for i in range(5):
            factura_data = {
                "cliente_id": test_cliente.id,
                "fecha_emision": "2024-01-15",
                "detalles": [
                    {
                        "producto_id": test_producto.id,
                        "cantidad": 1.0,
                        "precio_unitario": 50000.00
                    }
                ]
            }
            tasks.append(
                async_client.post(
                    "/api/v1/facturas/",
                    json=factura_data,
                    headers=authenticated_headers
                )
            )
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        execution_time = end_time - start_time
        successful_responses = sum(
            1 for r in responses 
            if hasattr(r, 'status_code') and r.status_code in [200, 201]
        )
        
        # Should complete most operations successfully
        assert successful_responses >= len(tasks) * 0.9  # 90% success rate
        assert execution_time < 15.0  # Should complete within 15 seconds