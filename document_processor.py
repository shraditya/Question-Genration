import PyPDF2
import docx
import os
import re
from typing import List


class DocumentProcessor:
    """Process different document formats and extract text content"""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file path"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file path"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error processing DOCX: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file path"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error processing TXT: {str(e)}")
            return ""

    @staticmethod
    def process_document(file_path: str) -> str:
        """Process document based on file extension"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return ""

        file_extension = file_path.lower().split('.')[-1]

        if file_extension == 'pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            return DocumentProcessor.extract_text_from_docx(file_path)
        elif file_extension in ('txt', 'md'):
            return DocumentProcessor.extract_text_from_txt(file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and preprocess extracted text"""
        text = ' '.join(text.split())
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text
