"""
Tests for XMLValidator.
"""

import pytest

from validated_llm.validators.xml import HAS_LXML, XMLValidator


class TestXMLValidator:
    """Test XMLValidator functionality."""

    def test_valid_xml_basic(self):
        """Test validation of basic valid XML."""
        validator = XMLValidator()
        xml_content = """<?xml version="1.0"?>
        <root>
            <item id="1">First item</item>
            <item id="2">Second item</item>
        </root>"""

        result = validator.validate(xml_content)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata["root_tag"] == "root"
        assert result.metadata["total_elements"] == 3  # root + 2 items

    def test_invalid_xml_syntax(self):
        """Test validation of XML with syntax errors."""
        validator = XMLValidator()

        # Unclosed tag
        result = validator.validate("<root><item>text</root>")
        assert not result.is_valid
        assert "Invalid XML syntax" in result.errors[0]

        # Missing closing tag
        result = validator.validate("<root><item>text</item>")
        assert not result.is_valid

        # Invalid attribute syntax
        result = validator.validate("<root attr=value>text</root>")
        assert not result.is_valid

    def test_required_root_element(self):
        """Test validation with required root element."""
        validator = XMLValidator(require_root_element="document")

        # Correct root element
        result = validator.validate("<document><title>Test</title></document>")
        assert result.is_valid

        # Wrong root element
        result = validator.validate("<root><title>Test</title></root>")
        assert not result.is_valid
        assert "Root element must be 'document'" in result.errors[0]

    def test_required_root_element_non_strict(self):
        """Test required root element in non-strict mode."""
        validator = XMLValidator(require_root_element="document", strict_mode=False)

        # Wrong root element becomes a warning in non-strict mode
        result = validator.validate("<root><title>Test</title></root>")
        assert result.is_valid
        assert len(result.warnings) == 1
        assert "Root element must be 'document'" in result.warnings[0]

    def test_nested_xml_structure(self):
        """Test validation of nested XML structures."""
        validator = XMLValidator()
        xml_content = """<?xml version="1.0"?>
        <catalog>
            <book id="1">
                <title>Python Programming</title>
                <author>
                    <name>John Doe</name>
                    <email>john@example.com</email>
                </author>
                <price currency="USD">29.99</price>
            </book>
        </catalog>"""

        result = validator.validate(xml_content)

        assert result.is_valid
        assert result.metadata["root_tag"] == "catalog"
        assert result.metadata["total_elements"] == 7  # catalog + book + title + author + name + email + price

    def test_xml_with_namespaces(self):
        """Test XML with namespace declarations."""
        validator = XMLValidator(check_namespaces=True)
        xml_content = """<?xml version="1.0"?>
        <root xmlns:custom="http://example.com/custom">
            <custom:item>Test</custom:item>
        </root>"""

        result = validator.validate(xml_content)
        assert result.is_valid

    def test_xml_with_comments_and_cdata(self):
        """Test XML with comments and CDATA sections."""
        validator = XMLValidator()
        xml_content = """<?xml version="1.0"?>
        <root>
            <!-- This is a comment -->
            <description><![CDATA[This text contains <special> characters]]></description>
            <item>Normal text</item>
        </root>"""

        result = validator.validate(xml_content)
        assert result.is_valid

    def test_empty_elements(self):
        """Test validation of empty elements."""
        validator = XMLValidator()

        # Self-closing empty element
        result = validator.validate("<root><empty/></root>")
        assert result.is_valid

        # Empty element with closing tag
        result = validator.validate("<root><empty></empty></root>")
        assert result.is_valid

    def test_xml_attributes(self):
        """Test validation of XML attributes."""
        validator = XMLValidator()

        # Valid attributes
        xml_content = """<root>
            <item id="1" name="Test" active="true">Content</item>
        </root>"""
        result = validator.validate(xml_content)
        assert result.is_valid

        # Duplicate attributes (invalid)
        xml_content = '<root><item id="1" id="2">Content</item></root>'
        result = validator.validate(xml_content)
        assert not result.is_valid

    @pytest.mark.skipif(not HAS_LXML, reason="lxml not installed")
    def test_xsd_schema_validation(self):
        """Test XML validation against XSD schema."""
        xsd_schema = """<?xml version="1.0"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="person">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="name" type="xs:string"/>
                        <xs:element name="age" type="xs:integer"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>"""

        validator = XMLValidator(xsd_schema=xsd_schema)

        # Valid according to schema
        valid_xml = """<?xml version="1.0"?>
        <person>
            <name>John Doe</name>
            <age>30</age>
        </person>"""
        result = validator.validate(valid_xml)
        assert result.is_valid
        assert result.metadata.get("schema_valid") is True

        # Invalid according to schema (wrong type for age)
        invalid_xml = """<?xml version="1.0"?>
        <person>
            <name>John Doe</name>
            <age>thirty</age>
        </person>"""
        result = validator.validate(invalid_xml)
        assert not result.is_valid
        assert "Schema validation error" in str(result.errors)

    def test_validator_description(self):
        """Test that validator provides helpful description."""
        # Basic validator
        validator = XMLValidator()
        description = validator.get_validator_description()
        assert "XML Validator" in description
        assert "well-formed XML" in description

        # With root element requirement
        validator = XMLValidator(require_root_element="config")
        description = validator.get_validator_description()
        assert "Root element must be: <config>" in description

        # With XSD schema
        if HAS_LXML:
            xsd_schema = """<?xml version="1.0"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root" type="xs:string"/>
            </xs:schema>"""
            validator = XMLValidator(xsd_schema=xsd_schema)
            description = validator.get_validator_description()
            assert "XSD schema" in description
