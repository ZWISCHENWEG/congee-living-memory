import glob

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Clean up previous patch if it exists
    if "MockAIProvider" in content:
        # We need to overwrite the patch entirely, so it's easier to just strip it and re-add it.
        # But wait, it's safer to just rewrite it properly.
        pass

    import_app = "from app.main import app"
    
    if import_app not in content:
        print(f"Skipping {filepath} (app.main not found)")
        return
        
    patch = """
from tests_mock import MockAIProvider, MockEmbeddingProvider
from app.services.ai import get_ai_provider
from app.services.embedding.factory import get_embedding_provider
app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
app.dependency_overrides[get_embedding_provider] = lambda: MockEmbeddingProvider()
"""
    
    # If already patched with just AIProvider, we can just replace that block
    if "app.dependency_overrides[get_ai_provider]" in content and "MockEmbeddingProvider" not in content:
        # replace the old patch block
        old_patch = """
    from tests_mock import MockAIProvider
    from app.services.ai import get_ai_provider
    app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
"""
        content = content.replace(old_patch, "\n" + patch + "\n")
    elif "MockEmbeddingProvider" not in content:
        content = content.replace(import_app, import_app + "\n" + patch)
        
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

for test_file in ["test_auto_memory.py", "test_chat_memory.py", "test_conflict_memory.py", "test_duplicate_memory.py", "test_forget_memory.py", "test_memory_update.py"]:
    patch_file(test_file)
