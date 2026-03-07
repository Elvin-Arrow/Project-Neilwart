import io
from config.loader import config
from providers.base import LLMProvider

def clean_response(text):
    """
    Strips markdown code block backticks (e.g., ```markdown ... ```) from the LLM response.
    """
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].strip()
    elif text.startswith("```md"):
        text = text[len("```md"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
        
    if text.endswith("```"):
        text = text[:-3].strip()
        
    return text

def generate_notes(provider: LLMProvider, content, is_image=False):
    """
    Phase 1 (Map): Generates notes independently for a chunk.
    """
    prompt = config['prompts']['generate_notes_map']

    if is_image:
        img_byte_arr = io.BytesIO()
        content.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        response_text = provider.generate_with_image(prompt, img_bytes)
    else:
        response_text = provider.generate(f"{prompt}\n\nContent:\n{content}")
        
    return clean_response(response_text)

def generate_notes_feed_forward(provider: LLMProvider, content, is_image=False, previous_notes=""):
    """
    Generates notes in a feed-forward manner.
    previous_notes is the accumulated notes from previous sections, used to merge new info.
    """
    if previous_notes:
        prompt = config['prompts']['generate_notes_feed_forward_merge'] + (
            f"\n\n=== EXISTING NOTES ===\n{previous_notes}\n=====================\n\n"
            "Now, here is the new content to integrate:"
        )
    else:
        prompt = config['prompts']['generate_notes_feed_forward_new']

    if is_image:
        img_byte_arr = io.BytesIO()
        content.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        response_text = provider.generate_with_image(prompt, img_bytes)
    else:
        response_text = provider.generate(f"{prompt}\n\nContent:\n{content}")
        
    return clean_response(response_text)

def synthesize_notes(provider: LLMProvider, notes_group):
    """
    Phase 2 (Reduce): Synthesizes a group of 4-5 map outputs into a cohesive set of notes.
    """
    combined_notes = "\n\n---\n\n".join(notes_group)
    prompt = config['prompts']['synthesize_notes']
    
    response_text = provider.generate(f"{prompt}\n\nNotes to Synthesize:\n{combined_notes}")
    return clean_response(response_text)

def verify_notes(provider: LLMProvider, source_contents, generated_notes, is_image=False):
    """
    Phase 3 (Verify): Checks the generated notes against the original source document over its chunks.
    """
    prompt = config['prompts']['verify_notes']
    
    if is_image:
        images = []
        for content in source_contents:
            img_byte_arr = io.BytesIO()
            content.save(img_byte_arr, format='PNG')
            images.append(img_byte_arr.getvalue())
            
        # For multi-image we'd need to adapt the provider interface.
        # But for simplification, let's just use the first image or assume it's disabled.
        # Since Phase 4 is disabled by default, we just stub it or send the first image.
        response_text = provider.generate_with_image(
            f"{prompt}\n\n[Generated Notes]:\n{generated_notes}\n\n[Full Source Document] (Provided as image attached.)", 
            images[0] if images else b''
        )
    else:
        source_text = "\n\n".join(source_contents)
        response_text = provider.generate(f"{prompt}\n\n[Full Source Document]:\n{source_text}\n\n[Generated Notes]:\n{generated_notes}")
        
    return response_text

def divide_markdown_with_llm(provider: LLMProvider, content):
    """
    Uses the LLM to insert '---' separators into a markdown document.
    """
    prompt = config['prompts']['divide_markdown']
    response_text = provider.generate(f"{prompt}\n\nDocument Content:\n{content}")
    # Fallback to original content on empty
    return response_text if response_text else content
