import re

def remove_extra_spaces_comments(text):
    lines = text.split('\n')
    stripped = [line for line in lines if not line.strip().startswith('#')]
    clean_text = ' '.join(stripped)
    clean_text = re.sub('\s+', ' ', clean_text).strip()  
    clean_text = re.sub('\"\"\"(.*?)\"\"\"', '', clean_text, flags=re.MULTILINE|re.DOTALL) # remove multi-line comments
    clean_text = re.sub("'''(.*?)'''", '', clean_text, flags=re.MULTILINE|re.DOTALL) # remove multi-line comments
    return clean_text
code = """



words

        
        
        """
clean_code = remove_extra_spaces_comments(code)
print(clean_code)