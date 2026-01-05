#!/usr/bin/env python3
"""
Stock Picker Launcher
Allows running in console mode or web UI mode
"""
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Stock Picker - Automated Stock Analysis & Alerts')
    parser.add_argument(
        '--mode',
        choices=['console', 'web'],
        default='web',
        help='Run mode: console (terminal-based) or web (web dashboard). Default: web'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web server host (web mode only). Default: 0.0.0.0'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web server port (web mode only). Default: 5000'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════╗
║          Stock Picker Pro - Market Analysis Tool         ║
╚══════════════════════════════════════════════════════════╝
""")

    if args.mode == 'console':
        print("Starting in CONSOLE mode...")
        print("=" * 60)
        from stock_picker import main as console_main
        console_main()
    else:
        print("Starting in WEB mode...")
        print(f"Dashboard URL: http://localhost:{args.port}")
        print("=" * 60)
        from web_app import run_web_app
        run_web_app(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
