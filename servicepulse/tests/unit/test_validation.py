"""Unit tests for input validation schemas."""

import pytest

from app.schemas.request import CreateRequestSchema


class TestCreateRequestValidation:
    def test_valid_request(self):
        data = CreateRequestSchema(
            customer_id="CUST-001",
            request_type="SERVICE",
            description="Test request",
        )
        assert data.customer_id == "CUST-001"

    def test_invalid_customer_id_pattern(self):
        with pytest.raises(ValueError):
            CreateRequestSchema(
                customer_id="INVALID",
                request_type="SERVICE",
                description="Test",
            )

    def test_invalid_customer_id_too_short(self):
        with pytest.raises(ValueError):
            CreateRequestSchema(
                customer_id="CUST-1",
                request_type="SERVICE",
                description="Test",
            )

    def test_empty_description(self):
        with pytest.raises(ValueError):
            CreateRequestSchema(
                customer_id="CUST-001",
                request_type="SERVICE",
                description="",
            )

    def test_description_too_long(self):
        with pytest.raises(ValueError):
            CreateRequestSchema(
                customer_id="CUST-001",
                request_type="SERVICE",
                description="x" * 1001,
            )

    def test_valid_request_type(self):
        for rt in ["SERVICE", "INQUIRY", "COMPLAINT"]:
            data = CreateRequestSchema(
                customer_id="CUST-001",
                request_type=rt,
                description="Test",
            )
            assert data.request_type.value == rt

    def test_invalid_request_type(self):
        with pytest.raises(ValueError):
            CreateRequestSchema(
                customer_id="CUST-001",
                request_type="INVALID",
                description="Test",
            )
