if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Ensure project root is on sys.path when running as a script
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from utils.text_processing import DocumentProcessing

def main():
    document_processing = DocumentProcessing()
    document_processing.create_vector_db_from_directory("me")


if __name__ == "__main__":
    main()

