import argparse
import sys
import logging

from convolingo.cli.interactive import InteractiveSession
from convolingo.cli.session import Session
from convolingo.cli.setup import SetupTool
from convolingo.utils.logging_setup import configure_logging
from convolingo.utils.config import DEFAULT_TARGET_LANGUAGE, DEFAULT_ORIGIN_LANGUAGE

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the ConvoLingo application"""
    # Create main parser
    parser = argparse.ArgumentParser(
        description='ConvoLingo - Language Learning Assistant'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Interactive session command
    interactive_parser = subparsers.add_parser(
        'interactive', 
        help='Start an interactive session with text input'
    )
    interactive_parser.add_argument(
        '--target', '-t',
        default=DEFAULT_TARGET_LANGUAGE,
        help=f'Target language to learn (default: {DEFAULT_TARGET_LANGUAGE})'
    )
    interactive_parser.add_argument(
        '--origin', '-o',
        default=DEFAULT_ORIGIN_LANGUAGE,
        help=f'Origin language (default: {DEFAULT_ORIGIN_LANGUAGE})'
    )
    
    # Basic session command
    session_parser = subparsers.add_parser(
        'session', 
        help='Start a basic session'
    )
    session_parser.add_argument(
        '--target', '-t',
        default=DEFAULT_TARGET_LANGUAGE,
        help=f'Target language to learn (default: {DEFAULT_TARGET_LANGUAGE})'
    )
    session_parser.add_argument(
        '--origin', '-o',
        default=DEFAULT_ORIGIN_LANGUAGE,
        help=f'Origin language (default: {DEFAULT_ORIGIN_LANGUAGE})'
    )
    session_parser.add_argument(
        '--duration', '-d',
        type=int,
        help='Session duration in seconds (default: indefinite)'
    )
    
    # Setup command
    setup_parser = subparsers.add_parser(
        'setup', 
        help='Set up the vocabulary tool'
    )
    setup_parser.add_argument(
        '--no-server',
        action='store_true',
        help='Do not run the webhook server'
    )
    setup_parser.add_argument(
        '--tool-id',
        help='Use existing tool ID instead of creating a new one'
    )
    
    # Parse args
    args = parser.parse_args()
    
    # Run the appropriate command
    try:
        if args.command == 'interactive':
            session = InteractiveSession()
            session.start(args.target, args.origin)
        elif args.command == 'session':
            session = Session()
            session.start(args.target, args.origin, getattr(args, 'duration', None))
        elif args.command == 'setup':
            setup = SetupTool()
            setup.run_setup(not getattr(args, 'no_server', False), 
                           getattr(args, 'tool_id', None))
        else:
            # If no command provided, show help
            parser.print_help()
            sys.exit(0)
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 