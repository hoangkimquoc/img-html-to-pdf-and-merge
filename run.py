import sys
import os

# Add src to path so we can import img_to_pdf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from img_to_pdf.__main__ import main
    sys.exit(main())
