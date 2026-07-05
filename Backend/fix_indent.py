import glob

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    out_lines = []
    for line in lines:
        if line.startswith("from tests_mock import"):
            out_lines.append("    " + line)
        elif line.startswith("from app.services.ai import"):
            out_lines.append("    " + line)
        elif line.startswith("from app.services.embedding.factory import"):
            out_lines.append("    " + line)
        elif line.startswith("app.dependency_overrides"):
            out_lines.append("    " + line)
        else:
            out_lines.append(line)
            
    with open(filepath, 'w') as f:
        f.writelines(out_lines)
    print(f"Fixed {filepath}")

for test_file in ["test_auto_memory.py", "test_chat_memory.py", "test_conflict_memory.py", "test_duplicate_memory.py", "test_forget_memory.py", "test_memory_update.py"]:
    fix_file(test_file)
