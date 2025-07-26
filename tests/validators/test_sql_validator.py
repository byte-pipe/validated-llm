"""Tests for SQLValidator."""

import pytest

from validated_llm.validators.sql import SQLValidator


class TestSQLValidator:
    """Test suite for SQLValidator."""

    def test_basic_select_query(self):
        """Test validation of basic SELECT query."""
        validator = SQLValidator()

        # Valid SELECT query
        result = validator.validate("SELECT * FROM users WHERE age > 18;")
        assert result.is_valid
        assert result.metadata["statement_count"] == 1
        assert "SELECT" in result.metadata["statement_types"]

        # Without semicolon (should still be valid by default)
        result = validator.validate("SELECT name, email FROM customers")
        assert result.is_valid

    def test_require_semicolon(self):
        """Test semicolon requirement."""
        validator = SQLValidator(require_semicolon=True)

        # Missing semicolon
        result = validator.validate("SELECT * FROM users")
        assert result.is_valid  # Still valid but with warning
        assert len(result.warnings) == 1
        assert "semicolon" in result.warnings[0]

        # With semicolon
        result = validator.validate("SELECT * FROM users;")
        assert result.is_valid
        assert len(result.warnings) == 0

    def test_multiple_statements(self):
        """Test multiple SQL statements."""
        validator = SQLValidator(allow_multiple_statements=True)

        sql = """
        CREATE TABLE users (id INTEGER, name TEXT);
        INSERT INTO users VALUES (1, 'John');
        SELECT * FROM users;
        """

        result = validator.validate(sql)
        assert result.is_valid
        assert result.metadata["statement_count"] == 3
        assert set(result.metadata["statement_types"]) == {"CREATE", "INSERT", "SELECT"}

        # Test with multiple statements disabled
        validator = SQLValidator(allow_multiple_statements=False)
        result = validator.validate(sql)
        assert not result.is_valid
        assert "Multiple SQL statements not allowed" in result.errors[0]

    def test_allowed_statements(self):
        """Test allowed statement types."""
        validator = SQLValidator(allowed_statements=["SELECT", "INSERT"])

        # Allowed statement
        result = validator.validate("SELECT * FROM users;")
        assert result.is_valid

        # Not allowed statement
        result = validator.validate("DELETE FROM users WHERE id = 1;")
        assert not result.is_valid
        assert "not in allowed list" in result.errors[0]

    def test_blocked_statements(self):
        """Test blocked statement types."""
        validator = SQLValidator(blocked_statements=["DROP", "DELETE"])

        # Allowed statement
        result = validator.validate("SELECT * FROM users;")
        assert result.is_valid

        # Blocked statement
        result = validator.validate("DROP TABLE users;")
        assert not result.is_valid
        assert "is blocked" in result.errors[0]

    def test_sql_injection_patterns(self):
        """Test detection of SQL injection patterns."""
        validator = SQLValidator(check_dangerous_patterns=True)

        # Safe query
        result = validator.validate("SELECT * FROM users WHERE id = 123;")
        assert result.is_valid

        # SQL injection attempts
        dangerous_queries = [
            "SELECT * FROM users WHERE name = 'admin' OR 1=1;",
            "SELECT * FROM users; DROP TABLE users;",
            "SELECT * FROM users WHERE id = 1; DELETE FROM users;",
            "SELECT * FROM users UNION SELECT * FROM information_schema.tables;",
            "SELECT * FROM users WHERE name = '' OR ''='';",
        ]

        for query in dangerous_queries:
            result = validator.validate(query)
            assert not result.is_valid
            assert "Dangerous SQL patterns detected" in result.errors[0]
            assert len(result.metadata["dangerous_patterns_found"]) > 0

    def test_syntax_validation(self):
        """Test SQL syntax validation."""
        validator = SQLValidator(check_syntax=True, dialect="sqlite")

        # Valid syntax
        result = validator.validate("SELECT id, name FROM users WHERE age > 18;")
        assert result.is_valid

        # Invalid syntax
        invalid_queries = [
            "SELECT FROM users;",  # Missing columns
            "INSERT users VALUES (1, 'test');",  # Missing INTO
            "UPDATE users WHERE id = 1;",  # Missing SET
            "DELETE users WHERE id = 1;",  # Missing FROM
            "SELECT * FROM WHERE age > 18;",  # Missing table
        ]

        for query in invalid_queries:
            result = validator.validate(query)
            assert not result.is_valid or len(result.warnings) > 0

    def test_balanced_delimiters(self):
        """Test validation of balanced parentheses and quotes."""
        validator = SQLValidator()

        # Unbalanced parentheses
        result = validator.validate("SELECT * FROM users WHERE (age > 18")
        assert not result.is_valid
        assert "Unbalanced parentheses" in str(result.errors)

        # Unbalanced quotes
        result = validator.validate("SELECT * FROM users WHERE name = 'John")
        assert not result.is_valid
        assert "Unbalanced single quotes" in str(result.errors)

    def test_code_block_extraction(self):
        """Test extraction of SQL from code blocks."""
        validator = SQLValidator()

        # SQL in code block
        output = """
        Here's the query you need:

        ```sql
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.name
        HAVING COUNT(o.id) > 5;
        ```
        """

        result = validator.validate(output)
        assert result.is_valid
        assert result.metadata["statement_count"] == 1
        assert "SELECT" in result.metadata["statement_types"]

    def test_complex_queries(self):
        """Test validation of complex SQL queries."""
        validator = SQLValidator()

        # CTE (Common Table Expression)
        cte_query = """
        WITH ranked_users AS (
            SELECT id, name, age,
                   ROW_NUMBER() OVER (ORDER BY age DESC) as rank
            FROM users
        )
        SELECT * FROM ranked_users WHERE rank <= 10;
        """

        result = validator.validate(cte_query)
        assert result.is_valid
        assert "WITH" in result.metadata["statement_types"] or "SELECT" in result.metadata["statement_types"]

        # Subquery
        subquery = """
        SELECT name, email
        FROM users
        WHERE id IN (
            SELECT user_id
            FROM orders
            WHERE total > 100
        );
        """

        result = validator.validate(subquery)
        assert result.is_valid

    def test_insert_variations(self):
        """Test different INSERT statement variations."""
        validator = SQLValidator()

        # INSERT with VALUES
        result = validator.validate("INSERT INTO users (name, age) VALUES ('John', 25);")
        assert result.is_valid

        # INSERT with SELECT
        result = validator.validate("INSERT INTO users_backup SELECT * FROM users;")
        assert result.is_valid

        # Multiple VALUES
        result = validator.validate(
            """
        INSERT INTO users (name, age) VALUES
        ('John', 25),
        ('Jane', 30),
        ('Bob', 35);
        """
        )
        assert result.is_valid

    def test_max_query_length(self):
        """Test maximum query length restriction."""
        validator = SQLValidator(max_query_length=50)

        # Short query
        result = validator.validate("SELECT * FROM users;")
        assert result.is_valid

        # Long query
        long_query = "SELECT " + ", ".join([f"col{i}" for i in range(50)]) + " FROM users;"
        result = validator.validate(long_query)
        assert not result.is_valid
        assert "exceeds maximum length" in result.errors[0]

    def test_empty_output(self):
        """Test validation of empty output."""
        validator = SQLValidator()

        result = validator.validate("")
        assert not result.is_valid
        assert "Output is empty" in result.errors[0]

        result = validator.validate("   ")
        assert not result.is_valid

    def test_case_sensitivity(self):
        """Test case sensitivity option."""
        # By default, case insensitive
        validator = SQLValidator(case_sensitive=False)
        result = validator.validate("select * from users;")
        assert result.is_valid
        assert "SELECT" in result.metadata["statement_types"]

    def test_validation_instructions(self):
        """Test generation of validation instructions."""
        validator = SQLValidator(allowed_statements=["SELECT", "INSERT"], require_semicolon=True, max_query_length=1000)

        instructions = validator.get_validation_instructions()
        assert "SQL QUERY VALIDATION REQUIREMENTS" in instructions
        assert "INSERT, SELECT" in instructions  # sorted order
        assert "MUST end with a semicolon" in instructions
        assert "Maximum query length: 1000" in instructions
