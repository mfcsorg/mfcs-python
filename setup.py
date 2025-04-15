from setuptools import setup, find_packages
import os
import re

def update_common_rules():
    """Update COMMON_RULES in function_prompt.py with content from ToolPrompt.txt."""
    tool_prompt_path = os.path.join("mfcs-prompt", "ToolPrompt.txt")
    function_prompt_path = os.path.join("src", "mfcs", "function_calling", "function_prompt.py")
    
    if not os.path.exists(tool_prompt_path):
        print(f"Warning: {tool_prompt_path} not found. Skipping COMMON_RULES update.")
        return
        
    try:
        with open(tool_prompt_path, "r", encoding="utf-8") as f:
            tool_prompt_content = f.read()
            
        with open(function_prompt_path, "r", encoding="utf-8") as f:
            function_prompt_content = f.read()
            
        # Replace the COMMON_RULES content
        pattern = r'(COMMON_RULES = """).*?(""")'
        new_content = re.sub(pattern, f'\\1{tool_prompt_content}\\2', 
                           function_prompt_content, flags=re.DOTALL)
            
        with open(function_prompt_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print("Successfully updated COMMON_RULES with ToolPrompt.txt content")
    except Exception as e:
        print(f"Error updating COMMON_RULES: {e}")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Update COMMON_RULES before setup
update_common_rules()

setup(
    name="mfcs",
    version="0.1.1",
    author="shideqin",
    author_email="shisdq@gmail.com",
    description="A Python library for handling function calling in Large Language Models (LLMs)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mfcsorg/mfcs-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="llm, function-calling, prompt-engineering, ai, nlp",
) 