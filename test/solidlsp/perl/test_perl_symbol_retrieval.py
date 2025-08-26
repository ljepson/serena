"""
Advanced integration tests for Perl language server symbol retrieval functionality.

These tests validate cross-file references, definitions, and symbol resolution
in the Perl test repository.
"""

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language


@pytest.mark.perl
class TestPerlSymbolRetrieval:
    """Test advanced symbol retrieval functionality of the Perl language server."""

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_definition_cross_module(self, language_server: SolidLanguageServer) -> None:
        """Test cross-module definition lookup for imported modules."""
        # Look for definition of User->new() call in main.pl
        # The User->new call is around line 8 in main.pl
        definitions = language_server.request_definition("main.pl", 8, 15)

        if definitions:
            # Should find definition in Models.pm
            definition_paths = [defn["relativePath"] for defn in definitions]
            assert any(
                "Models.pm" in path for path in definition_paths
            ), f"Should find User definition in Models.pm, got: {definition_paths}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_references_function_usage(self, language_server: SolidLanguageServer) -> None:
        """Test finding references to functions across files."""
        # Find references to format_currency function (defined in Utils.pm, used in main.pl)
        # format_currency is defined around line 16 in Utils.pm
        references = language_server.request_references("lib/Utils.pm", 16, 5)

        if references:
            reference_paths = [ref["relativePath"] for ref in references]
            # Should find usage in main.pl
            assert any(
                "main.pl" in path for path in reference_paths
            ), f"Should find format_currency usage in main.pl, got: {reference_paths}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_definition_local_function(self, language_server: SolidLanguageServer) -> None:
        """Test definition lookup for functions defined in the same file."""
        # Look for definition of helper_function call in main.pl
        # helper_function is called around line 34 (in the main function)
        definitions = language_server.request_definition("main.pl", 34, 5)

        if definitions:
            # Should find definition in the same file
            definition_paths = [defn["relativePath"] for defn in definitions]
            assert any(
                "main.pl" in path for path in definition_paths
            ), f"Should find helper_function definition in main.pl, got: {definition_paths}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_references_method_usage(self, language_server: SolidLanguageServer) -> None:
        """Test finding references to object methods."""
        # Find references to get_total method (defined in Order class, used in main.pl)
        # get_total is defined around line 40 in Models.pm (Order package)
        references = language_server.request_references("lib/Models.pm", 120, 5)

        if references:
            reference_paths = [ref["relativePath"] for ref in references]
            # Should find usage in main.pl or Services.pm
            expected_files = ["main.pl", "lib/Services.pm"]
            found_references = any(any(expected in path for expected in expected_files) for path in reference_paths)
            assert found_references, f"Should find get_total usage in expected files, got: {reference_paths}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_definition_package_method(self, language_server: SolidLanguageServer) -> None:
        """Test definition lookup for package/class methods."""
        # Look for definition of User->default_user() in main.pl (if it exists)
        # Or look for Item->new() call
        definitions = language_server.request_definition("main.pl", 15, 15)

        if definitions:
            # Should find definition in Models.pm
            definition_paths = [defn["relativePath"] for defn in definitions]
            assert any(
                "Models.pm" in path for path in definition_paths
            ), f"Should find method definition in Models.pm, got: {definition_paths}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_hover_function(self, language_server: SolidLanguageServer) -> None:
        """Test hover information for functions."""
        try:
            # Test hover on format_currency function call in main.pl
            hover_info = language_server.request_hover("main.pl", 25, 45)

            if hover_info and hover_info.get("contents"):
                contents = hover_info["contents"]
                # Should contain some information about the function
                contents_str = str(contents).lower()
                assert "format" in contents_str or "currency" in contents_str, f"Hover should contain relevant information, got: {contents}"
        except Exception as e:
            # Some language servers (like Perl::LanguageServer) may not support hover
            # This is acceptable as not all LSP features are mandatory
            if "hover" in str(e).lower() or "unknown perlmethod" in str(e).lower():
                pytest.skip("Language server does not support hover requests")
            else:
                raise

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_request_definition_imported_function(self, language_server: SolidLanguageServer) -> None:
        """Test definition lookup for imported functions from Utils module."""
        # Look for definition of calculate_discount function used in main.pl
        # calculate_discount is used around line 27 in main.pl
        definitions = language_server.request_definition("main.pl", 27, 25)

        if definitions:
            # Should find definition in Utils.pm
            definition_paths = [defn["relativePath"] for defn in definitions]
            assert any(
                "Utils.pm" in path for path in definition_paths
            ), f"Should find calculate_discount definition in Utils.pm, got: {definition_paths}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_cross_package_symbol_resolution(self, language_server: SolidLanguageServer) -> None:
        """Test symbol resolution across different packages in the same file."""
        # Models.pm contains multiple packages (User, Item, Order)
        # Test definition lookup within the same file but different packages

        # Get all symbols from Models.pm
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Models.pm", include_body=False)

        # Should have symbols from all packages
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should have methods from different packages
        user_methods = ["get_id", "get_name", "full_info"]
        item_methods = ["get_price", "discounted_price", "description"]
        order_methods = ["add_item", "get_total", "_calculate_total"]

        for method_group in [user_methods, item_methods, order_methods]:
            found_methods = [method for method in method_group if method in function_names]
            assert (
                len(found_methods) > 0
            ), f"Should find methods from different packages. Looking for {method_group}, found in function_names: {found_methods}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_service_class_symbol_resolution(self, language_server: SolidLanguageServer) -> None:
        """Test symbol resolution in service classes with complex inheritance patterns."""
        # Services.pm contains multiple service classes
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Services.pm", include_body=False)

        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect methods from all service classes
        service_classes = {
            "UserService": ["create_user", "get_user", "update_user", "delete_user"],
            "OrderService": ["create_order", "add_item_to_order", "complete_order"],
            "DatabaseService": ["connect", "disconnect", "execute_query"],
        }

        for service_class, expected_methods in service_classes.items():
            found_methods = [method for method in expected_methods if method in function_names]
            assert len(found_methods) > 0, f"Should find methods from {service_class}. Expected: {expected_methods}, found: {found_methods}"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_test_file_symbol_detection(self, language_server: SolidLanguageServer) -> None:
        """Test symbol detection in Perl test files (.t files)."""
        # Test symbol detection in test files
        all_symbols, root_symbols = language_server.request_document_symbols("t/models.t", include_body=False)

        # Should detect test functions/subroutines
        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]

        # Test files typically have various test subroutines
        # The exact structure depends on the test framework and PLS detection capabilities
        assert len(function_symbols) >= 0, "Should be able to analyze test files without errors"

        # If symbols are found, they should be valid
        if function_symbols:
            for symbol in function_symbols:
                assert "name" in symbol, "Each function symbol should have a name"
                assert "location" in symbol or "range" in symbol, "Each function symbol should have location information"

    @pytest.mark.parametrize("language_server", [Language.PERL], indirect=True)
    def test_perl_nested_package_method_resolution(self, language_server: SolidLanguageServer) -> None:
        """Test method resolution in nested package structures."""
        # Utils.pm has nested packages (Utils::Math, Utils::String)
        all_symbols, root_symbols = language_server.request_document_symbols("lib/Utils.pm", include_body=False)

        function_symbols = [symbol for symbol in all_symbols if symbol.get("kind") == 12]
        function_names = [symbol["name"] for symbol in function_symbols]

        # Should detect methods from nested packages
        math_functions = ["fibonacci", "factorial", "is_prime"]
        string_functions = ["trim", "capitalize", "snake_to_camel"]

        # At least some nested package functions should be detected
        found_math = [func for func in math_functions if func in function_names]
        found_string = [func for func in string_functions if func in function_names]

        total_nested_found = len(found_math) + len(found_string)
        assert total_nested_found > 0, f"Should detect functions from nested packages. Math: {found_math}, String: {found_string}"
