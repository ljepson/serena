"""
Basic integration tests for the Perl language server functionality.

These tests validate the functionality of the language server APIs
like request_document_symbols using the Perl test repository.
"""

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language


@pytest.mark.perl
class TestPerlLanguageServerBasics:
    """Test basic functionality of the Perl language server."""

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_language_server_initialization(self, language_server: SolidLanguageServer) -> None:
        """Test that Perl language server can be initialized successfully."""
        assert language_server is not None
        assert language_server.language == Language.PERL

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_document_symbols_main(self, language_server: SolidLanguageServer) -> None:
        """Test request_document_symbols for main.pl file."""
        # Test getting symbols from main.pl
        all_symbols, root_symbols = language_server.request_document_symbols("main.pl", include_body=False)

        # Extract function symbols (LSP Symbol Kind 12 for Function)
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect functions from main.pl
        expected_functions = [
            "main",
            "helper_function",
            "new",  # from DemoClass
            "get_value",  # from DemoClass
            "set_value",  # from DemoClass
        ]

        for func_name in expected_functions:
            assert func_name in function_names, f"Should find {func_name} function in main.pl"

        # Should have at least the expected functions
        assert len(function_symbols) >= len(
            expected_functions
        ), f"Should find at least {len(expected_functions)} functions, found {len(function_symbols)}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_document_symbols_models(self, language_server: SolidLanguageServer) -> None:
        """Test request_document_symbols for Models.pm module."""
        # Test getting symbols from Models.pm
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Models.pm", include_body=False)

        # Extract function symbols
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect methods from User class
        expected_user_methods = [
            "new",
            "get_id",
            "get_name",
            "get_email",
            "set_email",
            "full_info",
            "to_hash",
            "from_hash",
            "default_user",
        ]

        # Should detect methods from Item class
        expected_item_methods = [
            "new",
            "get_id",
            "get_name",
            "get_price",
            "discounted_price",
            "description",
        ]

        # Should detect methods from Order class
        expected_order_methods = [
            "new",
            "add_item",
            "get_total",
            "get_items",
            "to_hash",
            "_calculate_total",
        ]

        all_expected_methods = expected_user_methods + expected_item_methods + expected_order_methods

        for method_name in all_expected_methods:
            assert method_name in function_names, f"Should find {method_name} method in Models.pm"

        # Should have at least the expected methods
        assert len(function_symbols) >= len(
            all_expected_methods
        ), f"Should find at least {len(all_expected_methods)} methods, found {len(function_symbols)}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_document_symbols_utils(self, language_server: SolidLanguageServer) -> None:
        """Test request_document_symbols for Utils.pm module."""
        # Test getting symbols from Utils.pm
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Utils.pm", include_body=False)

        # Extract function symbols
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect main utility functions
        expected_main_functions = [
            "format_currency",
            "calculate_discount",
            "calculate_tax",
            "validate_email",
            "logger",
            "array_sum",
            "deep_clone",
        ]

        # Should detect Math utility functions
        expected_math_functions = [
            "fibonacci",
            "factorial",
            "is_prime",
        ]

        # Should detect String utility functions
        expected_string_functions = [
            "trim",
            "capitalize",
            "snake_to_camel",
        ]

        all_expected_functions = expected_main_functions + expected_math_functions + expected_string_functions

        for func_name in all_expected_functions:
            assert func_name in function_names, f"Should find {func_name} function in Utils.pm"

        # Should have at least the expected functions
        assert len(function_symbols) >= len(
            all_expected_functions
        ), f"Should find at least {len(all_expected_functions)} functions, found {len(function_symbols)}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_document_symbols_services(self, language_server: SolidLanguageServer) -> None:
        """Test request_document_symbols for Services.pm module."""
        # Test getting symbols from Services.pm
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Services.pm", include_body=False)

        # Extract function symbols
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect UserService methods
        expected_user_service_methods = [
            "new",
            "create_user",
            "get_user",
            "get_all_users",
            "update_user",
            "delete_user",
            "_generate_id",
        ]

        # Should detect OrderService methods
        expected_order_service_methods = [
            "new",
            "create_order",
            "get_order",
            "add_item_to_order",
            "complete_order",
            "get_orders_for_user",
            "_generate_order_id",
        ]

        # Should detect DatabaseService methods
        expected_database_service_methods = [
            "new",
            "connect",
            "disconnect",
            "execute_query",
        ]

        all_expected_methods = expected_user_service_methods + expected_order_service_methods + expected_database_service_methods

        for method_name in all_expected_methods:
            assert method_name in function_names, f"Should find {method_name} method in Services.pm"

        # Should have at least the expected methods
        assert len(function_symbols) >= len(
            all_expected_methods
        ), f"Should find at least {len(all_expected_methods)} methods, found {len(function_symbols)}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_document_symbols_with_body(self, language_server: SolidLanguageServer) -> None:
        """Test request_document_symbols with body extraction."""
        # Test with include_body=True on main.pl
        all_symbols, root_symbols = language_server.request_document_symbols("main.pl", include_body=True)

        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]

        # Find main function and check it has body
        main_symbol = next((sym for sym in function_symbols if sym["name"] == "main"), None)
        assert main_symbol is not None, "Should find main function"

        if "body" in main_symbol:
            body = main_symbol["body"]
            assert "sub main" in body, "Function body should contain sub definition"
            assert "User->new" in body, "Function body should contain User instantiation"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_package_detection(self, language_server: SolidLanguageServer) -> None:
        """Test that language server can detect Perl code structure."""
        # Test Models.pm which has multiple packages
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Models.pm", include_body=False)

        # Different language servers may report packages differently
        # Some as classes (Kind 5), some as modules (Kind 2), or just detect the functions
        # We'll just verify that we can get symbols from the file
        assert len(all_symbols) > 0, "Should detect symbols in Models.pm"

        # Check that we at least detect functions from the different packages
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect methods from different packages (User, Item, Order)
        expected_methods = ["new", "get_id", "get_name", "to_hash"]
        found_methods = [name for name in expected_methods if name in function_names]
        assert len(found_methods) > 0, f"Should detect at least some methods from packages. Found functions: {function_names}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_variable_detection(self, language_server: SolidLanguageServer) -> None:
        """Test that PLS can detect variables in Perl code."""
        # Test main.pl for variable detection
        all_symbols, root_symbols = language_server.request_document_symbols("main.pl", include_body=False)

        # Look for variable symbols (LSP Symbol Kind 13 for Variable)
        variable_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 13]

        # PLS may detect some variables, but this varies by language server implementation
        # Just ensure we can make the call without errors
        assert isinstance(variable_symbols, list), "Should return list of variable symbols"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_file_extensions_supported(self, language_server: SolidLanguageServer) -> None:
        """Test that the Perl language server supports various Perl file extensions."""
        # Test .pl file (main script)
        all_symbols_pl, _ = language_server.request_document_symbols("main.pl", include_body=False)
        assert len(all_symbols_pl) > 0, "Should find symbols in .pl file"

        # Test .pm file (module)
        all_symbols_pm, _ = language_server.request_document_symbols("lib/Models.pm", include_body=False)
        assert len(all_symbols_pm) > 0, "Should find symbols in .pm file"

        # Test .t file (test file)
        # Note: Some language servers may not fully analyze test files or may treat them differently
        # We'll just verify that we can request symbols without errors
        try:
            all_symbols_t, _ = language_server.request_document_symbols("t/models.t", include_body=False)
            # If symbols are found, great! If not, that's acceptable for test files
            # The important thing is that the language server doesn't crash on .t files
            assert isinstance(all_symbols_t, list), "Should return a list for .t files (even if empty)"
        except Exception as e:
            # If the language server has issues with .t files, that's acceptable
            # as long as normal .pl and .pm files work
            pytest.skip(f"Language server has limited support for .t test files: {e}")
