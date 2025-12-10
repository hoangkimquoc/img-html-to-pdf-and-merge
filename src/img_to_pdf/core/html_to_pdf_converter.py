"""HTML to PDF converter using Selenium with system Chrome/Edge for accurate CSS rendering."""

import os
import tempfile
import logging
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)


class SeleniumHtmlToPdfConverter:
    """Convert HTML files to PDF using Selenium with system browser (no download needed)."""
    
    def __init__(self):
        self.driver = None
        
    def _get_driver(self):
        """Get Selenium WebDriver using system browser (Chrome or Edge)."""
        if self.driver is not None:
            return self.driver
            
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        
        # Try Chrome first, then Edge
        for browser_type in ['chrome', 'edge']:
            try:
                if browser_type == 'chrome':
                    options = ChromeOptions()
                    options.add_argument('--headless=new')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--window-size=1920,1080')
                    self.driver = webdriver.Chrome(options=options)
                    logger.info("Using Chrome browser")
                else:
                    options = EdgeOptions()
                    options.add_argument('--headless=new')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--window-size=1920,1080')
                    self.driver = webdriver.Edge(options=options)
                    logger.info("Using Edge browser")
                
                return self.driver
            except Exception as e:
                logger.warning(f"Failed to initialize {browser_type}: {e}")
                continue
        
        raise RuntimeError("No compatible browser found. Please install Chrome or Edge.")
    
    def convert_file_sync(self, html_path: str, output_pdf_path: Optional[str] = None) -> Optional[str]:
        """
        Convert HTML file to PDF synchronously using Selenium.
        
        Args:
            html_path: Path to the HTML file
            output_pdf_path: Optional output PDF path
            
        Returns:
            PDF file path if successful, None otherwise
        """
        try:
            if not os.path.exists(html_path):
                logger.error(f"HTML file not found: {html_path}")
                return None
            
            # Create output path if not specified
            if output_pdf_path is None:
                temp_dir = tempfile.gettempdir()
                temp_name = f"html_to_pdf_{os.path.basename(html_path)}.pdf"
                output_pdf_path = os.path.join(temp_dir, temp_name)
            
            # Get browser driver
            driver = self._get_driver()
            
            # Navigate to HTML file
            file_url = f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
            logger.info(f"Loading HTML from: {file_url}")
            driver.get(file_url)
            
            # Wait for page to fully load (including fonts, CSS, images)
            import time
            time.sleep(3)  # Give time for all resources to load
            
            # Get page dimensions
            driver.set_window_size(1920, 1080)
            
            # Take screenshot
            logger.info("Capturing screenshot...")
            screenshot_bytes = driver.get_screenshot_as_png()
            
            # Save screenshot to temp file
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_img.write(screenshot_bytes)
            temp_img.close()
            temp_img_path = temp_img.name
            
            # Convert PNG to PDF using PIL
            logger.info("Converting to PDF...")
            pil_img = Image.open(temp_img_path)
            if pil_img.mode == 'RGBA':
                # Convert RGBA to RGB for PDF
                rgb_img = Image.new('RGB', pil_img.size, (255, 255, 255))
                rgb_img.paste(pil_img, mask=pil_img.split()[3])
                pil_img = rgb_img
            elif pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            # Save as PDF
            pil_img.save(output_pdf_path, 'PDF', quality=95)
            
            # Clean up
            try:
                os.unlink(temp_img_path)
            except:
                pass
            
            logger.info(f"PDF created successfully: {output_pdf_path}")
            return output_pdf_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup(self):
        """Clean up browser resources."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def __del__(self):
        """Ensure cleanup on deletion."""
        self.cleanup()


# For backward compatibility with existing code
class HtmlToPdfConverter(SeleniumHtmlToPdfConverter):
    """Alias for backward compatibility."""
    pass
