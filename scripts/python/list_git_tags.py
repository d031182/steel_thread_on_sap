"""
List Git Tags with Descriptions

Shows the 50 most recent git tags with their commit messages.
"""
import subprocess
import sys

def main():
    # Get all tags sorted by date (newest first)
    result = subprocess.run(
        ['git', 'tag', '--sort=-creatordate'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error getting tags: {result.stderr}")
        return 1
    
    tags = result.stdout.strip().split('\n')[:50]  # Get first 50
    
    print("=" * 80)
    print("Last 50 Git Tags (Most Recent First)")
    print("=" * 80)
    print()
    
    for i, tag in enumerate(tags, 1):
        # Get tag message or commit message
        msg_result = subprocess.run(
            ['git', 'tag', '-n1', tag],
            capture_output=True,
            text=True
        )
        
        tag_info = msg_result.stdout.strip()
        
        print(f"{i:2d}. {tag_info}")
    
    print()
    print("=" * 80)
    print(f"Total tags shown: {len(tags)}")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())