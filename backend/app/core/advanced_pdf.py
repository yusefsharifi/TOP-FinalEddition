import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from typing import List, Dict, Any, Optional, Union
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from datetime import datetime
import hashlib
from cryptography.fernet import Fernet
import base64
from reportlab.lib.colors import HexColor

class AdvancedPDFGenerator:
    def __init__(self):
        # Register Persian fonts
        self.register_persian_fonts()
        self.styles = getSampleStyleSheet()
        self.persian_style = ParagraphStyle(
            'Persian',
            parent=self.styles['Normal'],
            fontName='Vazir',
            fontSize=12,
            alignment=2,  # Right alignment
            leading=20,
            wordWrap='RTL'
        )
        
        # Initialize encryption key
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def register_persian_fonts(self):
        """Register Persian fonts for PDF generation"""
        # Register Vazir font
        pdfmetrics.registerFont(TTFont('Vazir', 'fonts/Vazir.ttf'))
        pdfmetrics.registerFont(TTFont('Vazir-Bold', 'fonts/Vazir-Bold.ttf'))
        
        # Register font family
        registerFontFamily('Vazir', normal='Vazir', bold='Vazir-Bold')
    
    def add_logo(self, logo_path: str, width: float = 2*inch) -> Image:
        """Add logo to the document"""
        img = Image(logo_path, width=width, height=width/2)
        return img
    
    def create_qr_code(self, data: str, size: int = 100) -> BytesIO:
        """Create QR code from data"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    def add_signature(self, signature_path: str, width: float = 2*inch) -> Image:
        """Add signature to the document"""
        img = Image(signature_path, width=width, height=width/3)
        return img
    
    def create_header(self, title: str, logo_path: Optional[str] = None) -> List[Any]:
        """Create document header with logo and title"""
        elements = []
        
        if logo_path:
            elements.append(self.add_logo(logo_path))
            elements.append(Spacer(1, 20))
        
        # Add title with Persian support
        reshaped_text = arabic_reshaper.reshape(title)
        bidi_text = get_display(reshaped_text)
        elements.append(Paragraph(bidi_text, self.persian_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_footer(self, text: str, page_number: bool = True) -> List[Any]:
        """Create document footer with text and page number"""
        elements = []
        
        # Add footer text
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        elements.append(Paragraph(bidi_text, self.persian_style))
        
        if page_number:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"صفحه {self.page_number}", self.persian_style))
        
        return elements
    
    def create_table(self, data: List[Dict[str, Any]], headers: List[str]) -> Table:
        """Create styled table with Persian support"""
        # Prepare table data with Persian support
        table_data = [headers]
        for row in data:
            table_row = []
            for header in headers:
                value = str(row.get(header, ''))
                reshaped_text = arabic_reshaper.reshape(value)
                bidi_text = get_display(reshaped_text)
                table_row.append(bidi_text)
            table_data.append(table_row)
        
        # Create table
        table = Table(table_data)
        
        # Apply styles
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Vazir-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Vazir'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
    
    def add_digital_signature(self, signature_data: str) -> str:
        """Add digital signature to the document"""
        # Create hash of the document
        document_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Encrypt the hash
        encrypted_hash = self.cipher_suite.encrypt(document_hash.encode())
        
        return base64.b64encode(encrypted_hash).decode()
    
    def generate_pdf(self, 
                    data: List[Dict[str, Any]], 
                    headers: List[str],
                    title: str,
                    logo_path: Optional[str] = None,
                    signature_path: Optional[str] = None,
                    footer_text: Optional[str] = None,
                    qr_data: Optional[str] = None,
                    encrypt: bool = False) -> BytesIO:
        """Generate PDF with all advanced features"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Add header
        elements.extend(self.create_header(title, logo_path))
        
        # Add table
        elements.append(self.create_table(data, headers))
        
        # Add QR code if provided
        if qr_data:
            elements.append(Spacer(1, 20))
            qr_buffer = self.create_qr_code(qr_data)
            qr_image = Image(qr_buffer)
            elements.append(qr_image)
        
        # Add signature if provided
        if signature_path:
            elements.append(Spacer(1, 20))
            elements.append(self.add_signature(signature_path))
        
        # Add footer
        if footer_text:
            elements.append(PageBreak())
            elements.extend(self.create_footer(footer_text))
        
        # Build PDF
        doc.build(elements)
        
        # Encrypt if requested
        if encrypt:
            pdf_data = buffer.getvalue()
            encrypted_data = self.cipher_suite.encrypt(pdf_data)
            buffer = BytesIO(encrypted_data)
        
        buffer.seek(0)
        return buffer 