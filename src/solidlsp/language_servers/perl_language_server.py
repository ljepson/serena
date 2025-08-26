"""
Perl Language Server implementation using Perl::LanguageServer.
Provides comprehensive Perl language server capabilities with debugging support.
"""

import json
import logging
import os
import pathlib
import shutil
import subprocess
import threading
from typing import Any

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


class PerlLanguageServer(SolidLanguageServer):
    """
    Provides Perl specific instantiation of the LanguageServer class using Perl::LanguageServer.
    Contains various configurations and settings specific to Perl with LSP features.
    """

    def __init__(
        self, config: LanguageServerConfig, logger: LanguageServerLogger, repository_root_path: str, solidlsp_settings: SolidLSPSettings
    ):
        """
        Creates a PerlLanguageServer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        pls_executable = self._setup_runtime_dependencies(logger, config, repository_root_path)
        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=pls_executable, cwd=repository_root_path),
            "perl",
            solidlsp_settings,
        )
        self.analysis_complete = threading.Event()
        self.service_ready_event = threading.Event()

        # Set timeout for Perl::LanguageServer requests
        self.set_request_timeout(30.0)  # 30 seconds for initialization and requests

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        """Override to ignore Perl-specific directories that cause performance issues."""
        perl_ignored_dirs = [
            "blib",  # Build library directory
            ".build",  # Build directory
            "cover_db",  # Devel::Cover database
            "nytprof",  # Devel::NYTProf output
            "nytprof.out",  # NYTProf output file
            "_build",  # Module::Build output
            "local",  # Local perl libraries (carton/cpanm)
            ".carton",  # Carton cache
            ".cpanm",  # cpanm work directory
            "fatlib",  # Fatpacked libraries
            "perl5",  # Local::Lib directory
            "extlib",  # External libraries
            "inc",  # Module bundled in inc/
            "share",  # File::ShareDir files
            "xt",  # Extended tests (author/release tests)
        ]
        return super().is_ignored_dirname(dirname) or dirname in perl_ignored_dirs

    @override
    def _get_wait_time_for_cross_file_referencing(self) -> float:
        """Override to provide optimal wait time for Perl::LanguageServer cross-file reference resolution.

        Perl::LanguageServer may need some time to index larger Perl codebases, especially those
        with complex module hierarchies.
        """
        return 2.0  # 2 seconds should be sufficient for Perl::LanguageServer

    @staticmethod
    def _find_perl_executable() -> str:
        """
        Find the Perl executable in the system PATH.
        Returns the path to perl or raises an error if not found.
        """
        perl_path = shutil.which("perl")
        if not perl_path:
            raise RuntimeError(
                "Perl is not installed or not found in PATH. Please install Perl using one of these methods:\n"
                "  - System package manager (brew install perl, apt install perl, yum install perl, etc.)\n"
                "  - From source: https://www.perl.org/get.html\n"
                "  - Using perlbrew: curl -L https://install.perlbrew.pl | bash && perlbrew install perl-5.38.0\n"
                "  - Using plenv: git clone https://github.com/tokuhirom/plenv.git ~/.plenv"
            )
        return perl_path

    @staticmethod
    def _check_perl_language_server_installed(perl_path: str) -> bool:
        """
        Check if Perl::LanguageServer is installed by trying to load it.
        """
        try:
            result = subprocess.run(
                [perl_path, "-MPerl::LanguageServer", "-e", "print $Perl::LanguageServer::VERSION"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _install_perl_language_server(perl_path: str, logger: LanguageServerLogger) -> None:
        """
        Install Perl::LanguageServer using cpanm or cpan.
        """
        # Try cpanm first (faster and more reliable)
        cpanm_path = shutil.which("cpanm")
        if cpanm_path:
            logger.log("Installing Perl::LanguageServer using cpanm...", logging.INFO)
            try:
                subprocess.run([cpanm_path, "Perl::LanguageServer"], check=True, capture_output=True)
                logger.log("Successfully installed Perl::LanguageServer using cpanm", logging.INFO)
                return
            except subprocess.CalledProcessError as e:
                logger.log(f"cpanm installation failed: {e}", logging.WARNING)

        # Fall back to cpan
        logger.log("Installing Perl::LanguageServer using cpan...", logging.INFO)
        try:
            # Use perl -MCPAN instead of direct cpan command for better compatibility
            subprocess.run(
                [perl_path, "-MCPAN", "-e", "install Perl::LanguageServer"], check=True, capture_output=True, input="yes\n", text=True
            )
            logger.log("Successfully installed Perl::LanguageServer using cpan", logging.INFO)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(
                f"Failed to install Perl::LanguageServer: {error_msg}\n"
                "Please try installing manually:\n"
                "  - Using cpanm: cpanm Perl::LanguageServer\n"
                "  - Using cpan: perl -MCPAN -e 'install Perl::LanguageServer'\n"
                "  - Check https://metacpan.org/pod/Perl::LanguageServer for more details"
            ) from e

    @staticmethod
    def _get_perl_language_server_command(perl_path: str, logger: LanguageServerLogger) -> str:
        """
        Get the command to start Perl::LanguageServer.
        """
        # Check if Perl::LanguageServer is installed
        if not PerlLanguageServer._check_perl_language_server_installed(perl_path):
            logger.log("Perl::LanguageServer not found, attempting to install...", logging.INFO)
            PerlLanguageServer._install_perl_language_server(perl_path, logger)

        # Perl::LanguageServer needs to be started with proper arguments
        # It requires --stdio for LSP communication
        logger.log("Starting Perl::LanguageServer in stdio mode", logging.INFO)
        return f"{perl_path} -MPerl::LanguageServer -e 'Perl::LanguageServer::run()' -- --stdio --version 2.6.0"

    @staticmethod
    def _setup_runtime_dependencies(logger: LanguageServerLogger, config: LanguageServerConfig, repository_root_path: str) -> str:
        """
        Setup runtime dependencies for PLS and return the command string to start the server.
        """
        # Check if Perl is installed
        perl_path = PerlLanguageServer._find_perl_executable()

        try:
            result = subprocess.run([perl_path, "--version"], check=True, capture_output=True, text=True)
            perl_version = result.stdout.strip().split("\n")[0]
            logger.log(f"Perl version: {perl_version}", logging.INFO)

            # Extract version number for compatibility checks
            import re

            version_match = re.search(r"v(\d+)\.(\d+)\.(\d+)", perl_version)
            if version_match:
                major, minor, patch = map(int, version_match.groups())
                if major < 5 or (major == 5 and minor < 16):
                    logger.log(
                        f"Warning: Perl {major}.{minor}.{patch} detected. Perl::LanguageServer works best with Perl 5.16+", logging.WARNING
                    )

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(f"Error checking Perl installation: {error_msg}") from e

        # Get Perl::LanguageServer command
        perl_ls_command = PerlLanguageServer._get_perl_language_server_command(perl_path, logger)

        # Return the command as a string (ProcessLaunchInfo expects a string)
        return perl_ls_command

    @staticmethod
    def _detect_perl_project_type(repository_root_path: str) -> dict[str, Any]:
        """
        Detect the type of Perl project and return configuration hints.
        """
        project_info = {
            "type": "generic",
            "has_makefile": False,
            "has_build_pl": False,
            "has_cpanfile": False,
            "has_minil": False,
            "lib_dirs": [],
            "inc_dirs": [],
        }

        # Check for build system files
        if os.path.exists(os.path.join(repository_root_path, "Makefile.PL")):
            project_info["has_makefile"] = True
            project_info["type"] = "ExtUtils::MakeMaker"

        if os.path.exists(os.path.join(repository_root_path, "Build.PL")):
            project_info["has_build_pl"] = True
            project_info["type"] = "Module::Build"

        if os.path.exists(os.path.join(repository_root_path, "cpanfile")):
            project_info["has_cpanfile"] = True

        if os.path.exists(os.path.join(repository_root_path, "minil.toml")):
            project_info["has_minil"] = True
            project_info["type"] = "Minilla"

        # Check for common library directories
        for lib_dir in ["lib", "local/lib/perl5", "extlib", "fatlib"]:
            lib_path = os.path.join(repository_root_path, lib_dir)
            if os.path.exists(lib_path):
                project_info["lib_dirs"].append(lib_path)

        # Check for include directories
        for inc_dir in ["inc", "share"]:
            inc_path = os.path.join(repository_root_path, inc_dir)
            if os.path.exists(inc_path):
                project_info["inc_dirs"].append(inc_path)

        return project_info

    @staticmethod
    def _get_perl_exclude_patterns(repository_root_path: str) -> list[str]:
        """
        Get Perl-specific exclude patterns for better performance.
        """
        base_patterns = [
            "**/blib/**",  # Build library directory
            "**/.build/**",  # Build directory
            "**/cover_db/**",  # Devel::Cover database
            "**/nytprof/**",  # Devel::NYTProf output
            "**/nytprof.out",  # NYTProf output file
            "**/_build/**",  # Module::Build output
            "**/local/**",  # Local perl libraries
            "**/.carton/**",  # Carton cache
            "**/.cpanm/**",  # cpanm work directory
            "**/fatlib/**",  # Fatpacked libraries
            "**/perl5/**",  # Local::Lib directory
            "**/extlib/**",  # External libraries when not part of project
            "**/xt/**",  # Extended tests (author/release tests)
            "**/.git/**",  # Git directory
            "**/node_modules/**",  # Node modules (for web projects)
        ]

        return base_patterns

    def _get_initialize_params(self) -> InitializeParams:
        """
        Returns Perl::LanguageServer specific initialization parameters.
        """
        # Note: Perl::LanguageServer doesn't require custom include paths in initialization
        # It uses the standard Perl @INC path resolution

        initialize_params = {
            "processId": os.getpid(),
            "rootPath": self.repository_root_path,
            "rootUri": pathlib.Path(self.repository_root_path).as_uri(),
            "capabilities": {
                "workspace": {
                    "workspaceEdit": {"documentChanges": True},
                    "configuration": True,
                },
                "textDocument": {
                    "documentSymbol": {
                        "hierarchicalDocumentSymbolSupport": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "completion": {
                        "completionItem": {
                            "snippetSupport": True,
                        }
                    },
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                },
            },
        }

        return initialize_params

    def _start_server(self) -> None:
        """
        Starts the Perl::LanguageServer for Perl
        """

        def register_capability_handler(params: dict) -> None:
            assert "registrations" in params
            for registration in params["registrations"]:
                self.logger.log(f"Registered capability: {registration['method']}", logging.INFO)
            return

        def execute_client_command_handler(params: dict) -> list:
            return []

        def do_nothing(params: dict) -> None:
            return

        def window_log_message(msg: dict) -> None:
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)
            # Check for Perl::LanguageServer ready signals
            message_text = msg.get("message", "")
            if any(keyword in message_text.lower() for keyword in ["ready", "initialized", "startup complete"]):
                self.logger.log("Perl::LanguageServer service ready signal detected", logging.INFO)
                self.analysis_complete.set()
                self.completions_available.set()

        def progress_handler(params: dict) -> None:
            # Perl::LanguageServer may send progress notifications during indexing
            if "value" in params:
                value = params["value"]
                if value.get("kind") == "end":
                    self.logger.log("Perl::LanguageServer indexing complete", logging.INFO)
                    self.analysis_complete.set()
                    self.completions_available.set()

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request("workspace/executeClientCommand", execute_client_command_handler)
        self.server.on_notification("$/progress", progress_handler)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        self.logger.log("Starting Perl::LanguageServer process", logging.INFO)
        self.server.start()
        initialize_params = self._get_initialize_params()

        self.logger.log(
            "Sending initialize request from LSP client to LSP server and awaiting response",
            logging.INFO,
        )
        self.logger.log(f"Sending init params: {json.dumps(initialize_params, indent=4)}", logging.DEBUG)
        init_response = self.server.send.initialize(initialize_params)
        self.logger.log(f"Received init response: {init_response}", logging.DEBUG)

        # Verify expected capabilities
        assert "capabilities" in init_response
        capabilities = init_response["capabilities"]

        # Perl::LanguageServer should provide these basic capabilities
        assert "textDocumentSync" in capabilities
        text_document_sync = capabilities["textDocumentSync"]
        if isinstance(text_document_sync, int):
            assert text_document_sync in [1, 2], f"Unexpected textDocumentSync value: {text_document_sync}"
        elif isinstance(text_document_sync, dict):
            assert "change" in text_document_sync or "openClose" in text_document_sync, "textDocumentSync should have expected properties"

        # Log important capabilities
        important_capabilities = [
            "completionProvider",
            "hoverProvider",
            "definitionProvider",
            "referencesProvider",
            "documentSymbolProvider",
            "signatureHelpProvider",
            "documentFormattingProvider",
        ]

        for cap in important_capabilities:
            if cap in capabilities:
                self.logger.log(f"Perl::LanguageServer {cap}: available", logging.DEBUG)
            else:
                self.logger.log(f"Perl::LanguageServer {cap}: not available", logging.DEBUG)

        self.server.notify.initialized({})

        # Wait for Perl::LanguageServer to complete its initial indexing
        self.logger.log("Waiting for Perl::LanguageServer to complete initial indexing...", logging.INFO)
        if self.analysis_complete.wait(timeout=30.0):
            self.logger.log("Perl::LanguageServer initial indexing complete, server ready", logging.INFO)
        else:
            self.logger.log("Timeout waiting for Perl::LanguageServer indexing completion, proceeding anyway", logging.WARNING)
            # Fallback: assume indexing is complete after timeout
            self.analysis_complete.set()
            self.completions_available.set()
