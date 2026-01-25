#!/usr/bin/env python3
"""
Git Helper Script - Parameterized Git Operations
Provides reliable git command execution for AI assistant
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_git_command(command_args, capture_output=True):
    """
    Execute a git command and return the result
    
    Args:
        command_args: List of command arguments (e.g., ['status', '--short'])
        capture_output: Whether to capture and return output
    
    Returns:
        dict with 'success', 'output', 'error' keys
    """
    try:
        full_command = ['git'] + command_args
        result = subprocess.run(
            full_command,
            capture_output=capture_output,
            text=True,
            check=False
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip() if capture_output else '',
            'error': result.stderr.strip() if capture_output else '',
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -1
        }


def git_status():
    """Get git status"""
    result = run_git_command(['status', '--short'])
    print("Git Status:")
    if result['success']:
        print(result['output'] if result['output'] else "No changes")
    else:
        print(f"Error: {result['error']}")
    return result


def git_add(paths):
    """
    Add files to git staging
    
    Args:
        paths: List of paths or single path string
    """
    if isinstance(paths, str):
        paths = [paths]
    
    result = run_git_command(['add'] + paths)
    if result['success']:
        print(f"✅ Added to staging: {', '.join(paths)}")
    else:
        print(f"❌ Failed to add files: {result['error']}")
    return result


def git_commit(message):
    """
    Commit staged changes
    
    Args:
        message: Commit message
    """
    result = run_git_command(['commit', '-m', message])
    if result['success']:
        print(f"✅ Committed: {message[:60]}...")
        print(result['output'])
    else:
        print(f"❌ Commit failed: {result['error']}")
    return result


def git_add_and_commit(paths, message):
    """
    Add files and commit in one operation
    
    Args:
        paths: List of paths or single path string
        message: Commit message
    """
    print("\n=== Git Add & Commit ===\n")
    
    # Add files
    add_result = git_add(paths)
    if not add_result['success']:
        return add_result
    
    print()
    
    # Commit
    commit_result = git_commit(message)
    
    print("\n=== Complete ===\n")
    return commit_result


def git_log(count=5):
    """Show recent commit log"""
    result = run_git_command(['log', f'-{count}', '--oneline'])
    print(f"\nRecent {count} commits:")
    if result['success']:
        print(result['output'])
    else:
        print(f"Error: {result['error']}")
    return result


def main():
    parser = argparse.ArgumentParser(description='Git Helper Script')
    subparsers = parser.add_subparsers(dest='command', help='Git command to execute')
    
    # Status command
    subparsers.add_parser('status', help='Show git status')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add files to staging')
    add_parser.add_argument('paths', nargs='+', help='Paths to add')
    
    # Commit command
    commit_parser = subparsers.add_parser('commit', help='Commit staged changes')
    commit_parser.add_argument('message', help='Commit message')
    
    # Add and commit command
    add_commit_parser = subparsers.add_parser('add-commit', help='Add and commit in one step')
    add_commit_parser.add_argument('paths', nargs='+', help='Paths to add')
    add_commit_parser.add_argument('-m', '--message', required=True, help='Commit message')
    
    # Log command
    log_parser = subparsers.add_parser('log', help='Show recent commits')
    log_parser.add_argument('-n', '--count', type=int, default=5, help='Number of commits to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'status':
        result = git_status()
    elif args.command == 'add':
        result = git_add(args.paths)
    elif args.command == 'commit':
        result = git_commit(args.message)
    elif args.command == 'add-commit':
        result = git_add_and_commit(args.paths, args.message)
    elif args.command == 'log':
        result = git_log(args.count)
    else:
        print(f"Unknown command: {args.command}")
        return 1
    
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())