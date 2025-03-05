# Tool ID
VOCABULARY_TOOL_ID = "b7bf97bf-c4cb-4d41-9db2-038460f17870"

def mock_tool_call(text):
    """
    Simple mock of the vocabulary tool that would be called via VAPI
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: A message indicating the tool was called
    """
    print(f"[DEBUG] Tool {VOCABULARY_TOOL_ID} would be called for: {text}")
    return "Tool called successfully" 