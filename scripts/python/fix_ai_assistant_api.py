"""
Fix AI Assistant API to pass SQL service from DI container

This script updates api.py to pass the injected SQL service to agent methods.
"""

import re

api_file = "modules/ai_assistant/backend/api.py"

# Read the file
with open(api_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Update send_message endpoint
pattern1 = r"(# Get Joule agent\s+agent = get_joule_agent\(\))"
replacement1 = r"# Get injected SQL service from DI container\n        sql_service = current_app.config['AI_ASSISTANT_SQL_SERVICE']\n        \n        \1"

content = re.sub(pattern1, replacement1, content, count=1)

# Pattern 2: Add sql_service parameter to first process_message call (send_message endpoint)
pattern2 = r"(ai_response = asyncio\.run\(agent\.process_message\(\s+user_message=user_message,\s+conversation_history=history,\s+context=session\.context\.dict\(\))\s*\)"
replacement2 = r"\1,\n                sql_execution_service=sql_service\n            )"

content = re.sub(pattern2, replacement2, content, count=1)

# Pattern 3: Add sql_service parameter to process_message_stream call (chat_stream endpoint)
pattern3 = r"(async for event in agent\.process_message_stream\(\s+user_message=user_message,\s+conversation_history=history,\s+context=session\.context\.dict\(\))\s*\):"
replacement3 = r"\1,\n                        sql_execution_service=sql_service\n                    ):"

content = re.sub(pattern3, replacement3, content)

# Pattern 4: Add sql_service parameter to second process_message call (chat endpoint)
# This one needs to be more careful since there are two process_message calls
# We need to find the second one (in the chat() function)
pattern4 = r"(# Process message with agent \(async\)\s+ai_response = asyncio\.run\(agent\.process_message\(\s+user_message=req\.message,\s+conversation_history=history,\s+context=session\.context\.dict\(\))\s*\)"
replacement4 = r"\1,\n                sql_execution_service=sql_service\n            )"

content = re.sub(pattern4, replacement4, content)

# Write the file back
with open(api_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Updated {api_file}")
print("Changes:")
print("1. Added sql_service = current_app.config['AI_ASSISTANT_SQL_SERVICE'] in send_message")
print("2. Added sql_execution_service parameter to process_message calls (x2)")
print("3. Added sql_execution_service parameter to process_message_stream call")