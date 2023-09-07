def remove_invalid_char(code):
    invalid_char = "\u200b"
    
    # Remove invalid character
    cleaned_code = code.replace(invalid_char, "")
    
    return cleaned_code

your_code = """

hi


"""

cleaned_code = remove_invalid_char(your_code)
print(cleaned_code)