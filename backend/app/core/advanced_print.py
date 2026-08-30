from typing import List, Dict, Any, Optional, Union, Tuple
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, A5, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import qrcode
from datetime import datetime
import json
import os

class AdvancedPrintGenerator:
    def __init__(self, page_size: str = 'A4', orientation: str = 'portrait'):
        self.buffer = BytesIO()
        self.page_size = getattr(eval(orientation), page_size)
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.elements = []
        self._register_fonts()
    
    def _register_fonts(self):
        """Register Persian fonts"""
        # Register Vazir font
        pdfmetrics.registerFont(TTFont('Vazir', 'Vazir.ttf'))
        pdfmetrics.registerFont(TTFont('VazirBold', 'Vazir-Bold.ttf'))
        
        # Create Persian styles
        self.styles.add(ParagraphStyle(
            name='Persian',
            fontName='Vazir',
            fontSize=12,
            alignment=TA_RIGHT
        ))
        
        self.styles.add(ParagraphStyle(
            name='PersianBold',
            fontName='VazirBold',
            fontSize=12,
            alignment=TA_RIGHT
        ))
    
    def add_title(self, title: str, font_size: int = 16, bold: bool = True):
        """Add title to the document"""
        # Reshape Persian text
        reshaped_text = arabic_reshaper.reshape(title)
        bidi_text = get_display(reshaped_text)
        
        style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['PersianBold' if bold else 'Persian'],
            fontSize=font_size,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.elements.append(Paragraph(bidi_text, style))
        self.elements.append(Spacer(1, 12))
    
    def add_header(self, header: str, font_size: int = 14):
        """Add header to the document"""
        # Reshape Persian text
        reshaped_text = arabic_reshaper.reshape(header)
        bidi_text = get_display(reshaped_text)
        
        style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['PersianBold'],
            fontSize=font_size,
            spaceAfter=20
        )
        
        self.elements.append(Paragraph(bidi_text, style))
        self.elements.append(Spacer(1, 12))
    
    def add_text(self, text: str, font_size: int = 12, bold: bool = False):
        """Add text to the document"""
        # Reshape Persian text
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        style = ParagraphStyle(
            'CustomText',
            parent=self.styles['PersianBold' if bold else 'Persian'],
            fontSize=font_size,
            spaceAfter=12
        )
        
        self.elements.append(Paragraph(bidi_text, style))
    
    def add_table(self, data: List[Dict[str, Any]], headers: List[str],
                 col_widths: Optional[List[float]] = None,
                 style: Optional[Dict[str, Any]] = None):
        """Add table to the document"""
        # Prepare table data
        table_data = []
        
        # Add headers
        header_row = []
        for header in headers:
            # Reshape Persian text
            reshaped_text = arabic_reshaper.reshape(header)
            bidi_text = get_display(reshaped_text)
            header_row.append(bidi_text)
        table_data.append(header_row)
        
        # Add data rows
        for row in data:
            data_row = []
            for header in headers:
                value = str(row.get(header, ''))
                # Reshape Persian text
                reshaped_text = arabic_reshaper.reshape(value)
                bidi_text = get_display(reshaped_text)
                data_row.append(bidi_text)
            table_data.append(data_row)
        
        # Create table
        if col_widths is None:
            col_widths = [self.page_size[0] / len(headers)] * len(headers)
        
        table = Table(table_data, colWidths=col_widths)
        
        # Apply default style
        default_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'VazirBold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Vazir'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
        
        # Apply custom style if provided
        if style:
            default_style.extend(style)
        
        table.setStyle(TableStyle(default_style))
        self.elements.append(table)
        self.elements.append(Spacer(1, 12))
    
    def add_image(self, image_path: str, width: float = 400, height: float = 300):
        """Add image to the document"""
        img = Image(image_path, width=width, height=height)
        self.elements.append(img)
        self.elements.append(Spacer(1, 12))
    
    def add_qr_code(self, data: str, size: float = 100):
        """Add QR code to the document"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Add image to document
        qr_img = Image(buffer, width=size, height=size)
        self.elements.append(qr_img)
        self.elements.append(Spacer(1, 12))
    
    def add_page_break(self):
        """Add page break"""
        self.elements.append(PageBreak())
    
    def add_footer(self, text: str, font_size: int = 10):
        """Add footer to the document"""
        # Reshape Persian text
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        
        style = ParagraphStyle(
            'CustomFooter',
            parent=self.styles['Persian'],
            fontSize=font_size,
            spaceBefore=20,
            alignment=TA_CENTER
        )
        
        self.elements.append(Paragraph(bidi_text, style))
    
    def add_watermark(self, text: str, opacity: float = 0.3):
        """Add watermark to the document"""
        def watermark(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(Color(0, 0, 0, alpha=opacity))
            canvas.setFont('Vazir', 60)
            # Reshape Persian text
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            canvas.rotate(45)
            canvas.drawCentredString(doc.width/2, doc.height/2, bidi_text)
            canvas.restoreState()
        
        self.doc.build(self.elements, onFirstPage=watermark, onLaterPages=watermark)
    
    def generate_pdf(self) -> BytesIO:
        """Generate PDF file"""
        self.doc.build(self.elements)
        self.buffer.seek(0)
        return self.buffer 