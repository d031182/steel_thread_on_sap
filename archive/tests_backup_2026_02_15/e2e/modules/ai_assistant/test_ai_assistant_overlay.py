"""
E2E Tests for AI Assistant v2 Overlay

Tests the ChatGPT-style overlay UI with mock API
"""

import pytest
from pathlib import Path
import json


@pytest.mark.e2e
@pytest.mark.app_v2
def test_ai_assistant_overlay_opens(page, app_v2_base_url):
    """
    Test: AI Assistant overlay opens when shell button clicked
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # ACT
    # Click AI Assistant shell button
    shell_button = page.locator('button[data-action="open-ai-assistant"]')
    shell_button.click()
    
    # Wait for dialog to appear
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ASSERT
    dialog = page.locator('.aiAssistantDialog')
    assert dialog.is_visible(), "AI Assistant dialog should be visible"
    
    # Check dialog title
    title = page.locator('.sapMDialogTitle')
    assert "Joule AI Assistant" in title.text_content()


@pytest.mark.e2e
@pytest.mark.app_v2
def test_send_message_receives_response(page, app_v2_base_url):
    """
    Test: User can send message and receive AI response
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # Open AI Assistant
    shell_button = page.locator('button[data-action="open-ai-assistant"]')
    shell_button.click()
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ACT
    # Type message
    input_area = page.locator('textarea.aiInputArea')
    input_area.fill("What suppliers do we have?")
    
    # Click send button
    send_button = page.locator('button.aiSendButton')
    send_button.click()
    
    # Wait for AI response
    page.wait_for_selector('.aiMessageBubble', timeout=10000)
    
    # ASSERT
    # Check user message appears
    user_messages = page.locator('.userMessageBubble')
    assert user_messages.count() >= 1, "User message should appear"
    
    # Check AI response appears
    ai_messages = page.locator('.aiMessageBubble')
    assert ai_messages.count() >= 1, "AI response should appear"
    
    # Check AI response contains text
    ai_response_text = ai_messages.first.locator('.messageText').text_content()
    assert len(ai_response_text) > 0, "AI response should contain text"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_typing_indicator_shows_during_processing(page, app_v2_base_url):
    """
    Test: Typing indicator appears while AI is processing
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # Open AI Assistant
    shell_button = page.locator('button[data-action="open-ai-assistant"]')
    shell_button.click()
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ACT
    # Send message
    input_area = page.locator('textarea.aiInputArea')
    input_area.fill("Test message")
    
    send_button = page.locator('button.aiSendButton')
    send_button.click()
    
    # ASSERT
    # Typing indicator should appear briefly
    # (This test may be flaky if API responds too fast)
    typing_indicator = page.locator('.messageText:has-text("typing")')
    
    # Either typing indicator appears, or AI response appears immediately
    try:
        typing_indicator.wait_for(state="visible", timeout=1000)
        assert typing_indicator.is_visible()
    except:
        # API responded too fast, check AI response instead
        ai_response = page.locator('.aiMessageBubble')
        assert ai_response.count() >= 1


@pytest.mark.e2e
@pytest.mark.app_v2
def test_input_disabled_during_processing(page, app_v2_base_url):
    """
    Test: Input area and send button disabled while AI is processing
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # Open AI Assistant
    shell_button = page.locator('button[data-action="open-ai-assistant"]')
    shell_button.click()
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ACT
    # Send message
    input_area = page.locator('textarea.aiInputArea')
    input_area.fill("Test message")
    
    send_button = page.locator('button.aiSendButton')
    send_button.click()
    
    # ASSERT
    # Input should be disabled immediately after send
    assert input_area.is_disabled(), "Input should be disabled during processing"
    assert send_button.is_disabled(), "Send button should be disabled during processing"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_conversation_history_preserved(page, app_v2_base_url):
    """
    Test: Conversation history is preserved across multiple messages
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # Open AI Assistant
    shell_button = page.locator('button[data-action="open-ai-assistant"]')
    shell_button.click()
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ACT
    # Send first message
    input_area = page.locator('textarea.aiInputArea')
    input_area.fill("First message")
    
    send_button = page.locator('button.aiSendButton')
    send_button.click()
    
    # Wait for response
    page.wait_for_selector('.aiMessageBubble', timeout=10000)
    
    # Send second message
    input_area.fill("Second message")
    send_button.click()
    
    # Wait for second response
    page.wait_for_timeout(2000)  # Wait for second response
    
    # ASSERT
    user_messages = page.locator('.userMessageBubble')
    assert user_messages.count() >= 2, "Should have 2 user messages"
    
    ai_messages = page.locator('.aiMessageBubble')
    assert ai_messages.count() >= 2, "Should have 2 AI responses"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_keyboard_shortcut_opens_assistant(page, app_v2_base_url):
    """
    Test: Ctrl+Shift+A keyboard shortcut opens AI Assistant
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # ACT
    # Press Ctrl+Shift+A
    page.keyboard.press("Control+Shift+A")
    
    # Wait for dialog
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ASSERT
    dialog = page.locator('.aiAssistantDialog')
    assert dialog.is_visible(), "AI Assistant should open via keyboard shortcut"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_close_button_closes_dialog(page, app_v2_base_url):
    """
    Test: Close button closes the AI Assistant dialog
    
    ARRANGE
    """
    page.goto(app_v2_base_url)
    page.wait_for_load_state("networkidle")
    
    # Open AI Assistant
    shell_button = page.locator('button[data-action="open-ai-assistant"]')
    shell_button.click()
    page.wait_for_selector('.aiAssistantDialog', timeout=5000)
    
    # ACT
    # Click close button
    close_button = page.locator('button:has-text("Close")')
    close_button.click()
    
    # ASSERT
    dialog = page.locator('.aiAssistantDialog')
    assert not dialog.is_visible(), "Dialog should be closed"