import pytest
import requests
from core.services.query_template_service import QueryTemplateService

BASE_URL = "http://localhost:5000"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestQueryTemplatesAPI:
    """Query templates API contract tests"""

    def test_list_templates_returns_valid_contract(self):
        """Test: List templates returns valid contract"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/query-templates", timeout=5
        )

        assert response.status_code == 200
        data = response.json()

        # Verify contract
        assert "templates" in data
        assert isinstance(data["templates"], list)
        assert len(data["templates"]) >= 3  # At least our 3 built-in templates

        # Verify template structure
        template = data["templates"][0]
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "category" in template
        assert "tags" in template

    def test_list_templates_with_category_filter(self):
        """Test: Filter templates by category"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/query-templates?category=supplier",
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all returned templates have matching category
        for template in data["templates"]:
            assert template["category"] == "supplier"

    def test_get_template_details(self):
        """Test: Get complete template details"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/query-templates/supplier_invoices_by_vendor",
            timeout=5,
        )

        assert response.status_code == 200
        template = response.json()

        # Verify complete contract
        assert template["id"] == "supplier_invoices_by_vendor"
        assert "sql_template" in template
        assert "parameters" in template
        assert isinstance(template["parameters"], list)

        # Verify parameter structure
        param = template["parameters"][0]
        assert "name" in param
        assert "type" in param
        assert "required" in param
        assert "validation_rule" in param

    def test_get_nonexistent_template_returns_404(self):
        """Test: Nonexistent template returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/query-templates/nonexistent",
            timeout=5,
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_search_templates(self):
        """Test: Search templates by query"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/query-templates/search?q=invoice",
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()

        assert "query" in data
        assert data["query"] == "invoice"
        assert "results" in data
        assert len(data["results"]) > 0

    def test_search_templates_requires_query(self):
        """Test: Search without query returns error"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/query-templates/search", timeout=5
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_validate_valid_parameters(self):
        """Test: Validate valid parameters"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph/query-templates/supplier_invoices_by_vendor/validate",
            json={"parameters": {"supplier_name": "Acme Corp"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["valid"] is True
        assert "errors" not in data or len(data["errors"]) == 0

    def test_validate_invalid_parameters(self):
        """Test: Validate invalid parameters"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph/query-templates/supplier_invoices_by_vendor/validate",
            json={"parameters": {}},  # Missing required parameter
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["valid"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0

    def test_render_query_with_valid_parameters(self):
        """Test: Render query with valid parameters"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph/query-templates/supplier_invoices_by_vendor/render",
            json={"parameters": {"supplier_name": "Acme Corp"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()

        assert "query" in data
        assert "Acme Corp" in data["query"]
        assert "SELECT" in data["query"]

    def test_render_query_validates_parameters(self):
        """Test: Render query validates parameters first"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph/query-templates/supplier_invoices_by_vendor/render",
            json={"parameters": {}},  # Missing required parameter
            timeout=5,
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_template_service_initialization(self):
        """Test: Service initializes with built-in templates"""
        service = QueryTemplateService()

        # Verify built-in templates exist
        assert service.get_template("supplier_invoices_by_vendor") is not None
        assert service.get_template("invoice_summary_by_date") is not None
        assert service.get_template("purchase_order_with_items") is not None