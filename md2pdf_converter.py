import markdown
from xhtml2pdf import pisa

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables'])
    
    # Add some basic styling so it looks good as a PDF
    styled_html = f"""
    <html>
    <head>
    <style>
        @page {{
            size: a4 portrait;
            margin: 2cm;
        }}
        body {{ 
            font-family: Helvetica, Arial, sans-serif; 
            font-size: 12pt;
            line-height: 1.6; 
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
        h2 {{ color: #2c3e50; margin-top: 20px; }}
        h3 {{ color: #34495e; }}
        code {{ 
            background-color: #f4f4f4; 
            padding: 2px 4px; 
            border-radius: 4px; 
            font-family: monospace;
            font-size: 10pt;
        }}
        pre {{ 
            background-color: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            border: 1px solid #e9ecef;
            white-space: pre-wrap; 
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        ul, ol {{ margin-bottom: 15px; }}
        li {{ margin-bottom: 5px; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    with open(pdf_path, 'w+b') as f:
        pisa_status = pisa.CreatePDF(styled_html, dest=f)

    if pisa_status.err:
        print("Error occurred while generating PDF")
    else:
        print(f"Successfully created PDF: {pdf_path}")

if __name__ == "__main__":
    convert_md_to_pdf('LSA_API_Usage_Guide_Updated.md', 'LSA_API_Usage_Guide_Updated.pdf')
