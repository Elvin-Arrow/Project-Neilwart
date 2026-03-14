import argparse
import os
import sys
from extractor import extract_from_pdf, extract_from_pptx, extract_from_docx, extract_from_markdown
from ai_client import generate_notes, generate_notes_feed_forward, synthesize_notes, verify_notes
from providers import get_provider
from config.loader import config

def process_file(filepath, provider, strategy="map-reduce", output_dir=None, output_file=None):
    print(f"Processing file: {filepath} with strategy: {strategy}")
    if not os.path.exists(filepath):
        print(f"Error: File not found - {filepath}")
        return

    filename, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    # Determine the output path
    base_output_name = output_file if output_file else f"{os.path.basename(filename)}_notes.md"
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, base_output_name)
    else:
        output_path = os.path.join(os.path.dirname(filepath), base_output_name)
    
    # Check extension and get iterator
    if ext == '.pdf':
        iterator = extract_from_pdf(filepath)
    elif ext == '.pptx':
        iterator = extract_from_pptx(filepath)
    elif ext == '.docx':
        iterator = extract_from_docx(filepath)
    elif ext == '.md':
        iterator = extract_from_markdown(filepath)
    else:
        print(f"Unsupported file format: {ext}")
        return

    print(f"Generating notes into {output_path}...")
    
    try:
        all_items = list(iterator)
        if not all_items:
            print("  No content extracted from the file.")
            return
            
        is_image_global = all_items[0][1] # Assumes uniform type across chunks
        print(f"  Total units extracted: {len(all_items)}")

        if strategy == "map-reduce":
            # Phase 1: Map
            print("\n--- Phase 1: Map (Generating Notes for each Chunk) ---")
            mapped_notes = []
            for index, item in enumerate(all_items):
                print(f"  Mapping chunk {index + 1}/{len(all_items)}...")
                content, is_image = item
                notes = generate_notes(provider, content, is_image)
                if notes:
                    mapped_notes.append(notes)
                    
            if not mapped_notes:
                print("  Failed to map any notes.")
                return

            # Phase 2: Reduce
            print("\n--- Phase 2: Reduce (Synthesizing Groups of Notes) ---")
            synthesized_notes = []
            chunk_size = config['app']['reduce_chunk_size']
            for i in range(0, len(mapped_notes), chunk_size):
                group = mapped_notes[i:i+chunk_size]
                print(f"  Synthesizing group {i//chunk_size + 1}/{ (len(mapped_notes)-1)//chunk_size + 1}...")
                syn_notes = synthesize_notes(provider, group)
                if syn_notes:
                    synthesized_notes.append(syn_notes)

            # Phase 3: Combine
            print("\n--- Phase 3: Combine (Finalizing Document) ---")
            final_notes_raw = "\n\n---\n\n".join(synthesized_notes)
            
            # Phase 4: Verify (Temporarily Disabled by User Request)
            # print("\n--- Phase 4: Verify (Checking against Source Document) ---")
            # source_data = [item[0] for item in all_items]
            # verified_notes = verify_notes(source_data, final_notes_raw, is_image_global)

            # Output final document (without verification)
            with open(output_path, 'w', encoding='utf-8') as outfile:
                outfile.write(f"# Notes for {os.path.basename(filepath)}\n\n")
                outfile.write(final_notes_raw)
                
        elif strategy == "feed-forward":
            accumulated_notes = ""
            for index, item in enumerate(all_items):
                print(f"  Generating notes for unit {index + 1}/{len(all_items)} in feed-forward chain...")
                content, is_image = item
                
                try:
                    notes = generate_notes_feed_forward(provider, content, is_image, previous_notes=accumulated_notes)
                    if notes:
                        accumulated_notes = notes
                        # Overwrite file with the progressively updated notes
                        with open(output_path, 'w', encoding='utf-8') as outfile:
                            outfile.write(f"# Notes for {os.path.basename(filepath)}\n\n")
                            outfile.write(accumulated_notes)
                except Exception as e:
                    print(f"  Error generating notes for unit {index + 1}: {e}")

        print(f"\nSuccessfully finished processing {filepath}")
    except Exception as e:
        print(f"Failed to process {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description=f"Generate notes from PDF, Word, or PowerPoint files using AI Providers.")
    parser.add_argument("file", help="Path to the file to process")
    parser.add_argument("--transcript", type=str, default=None, 
                        help="Path to an optional transcript file (currently unused).")
    parser.add_argument("--strategy", choices=["map-reduce", "feed-forward"], default="map-reduce",  
                        help="Note generation strategy to use (default: map-reduce).")
    parser.add_argument("--provider", choices=["ollama", "openai", "gemini"], default=config.get("provider", "ollama"),
                        help="The AI provider to use. Defaults to what is in config.yaml.")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save the generated notes. If not specified, saves next to the input file.")
    parser.add_argument("--output-file", type=str, default=None,
                        help="Specific filename for the generated notes. If processing multiple files, this will overwrite the same file unless carefully managed.")
    
    args = parser.parse_args()
    
    print(f"Initializing {args.provider} provider...")
    try:
        provider = get_provider(args.provider)
    except Exception as e:
        print(f"Error initializing provider: {e}")
        sys.exit(1)

    process_file(
        args.file, 
        provider, 
        strategy=args.strategy, 
        output_dir=args.output_dir, 
        output_file=args.output_file
    )

if __name__ == "__main__":
    main()
