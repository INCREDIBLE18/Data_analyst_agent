"""
PDF Report Generator

Generates professional PDF reports with charts, insights, and formatted tables.
"""

from typing import Optional
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64


class PDFReportGenerator:
    """Generates PDF reports from query results."""
    
    def __init__(self):
        """Initialize PDF generator."""
        pass
    
    def generate_report(
        self,
        query: str,
        sql: str,
        data: pd.DataFrame,
        insights: str,
        chart_base64: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF report.
        
        Args:
            query: Original natural language query
            sql: Generated SQL query
            data: Query results
            insights: AI-generated insights
            chart_base64: Base64-encoded chart image (optional)
            
        Returns:
            PDF file as bytes
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)
            
            # Container for PDF elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#764ba2'),
                spaceAfter=12,
                spaceBefore=12
            )
            normal_style = styles['Normal']
            
            # Title
            timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            elements.append(Paragraph("SQL Data Analyst Report", title_style))
            elements.append(Paragraph(f"Generated on {timestamp}", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Query Section
            elements.append(Paragraph("User Question", heading_style))
            elements.append(Paragraph(query, normal_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # SQL Query Section
            elements.append(Paragraph("Generated SQL Query", heading_style))
            sql_para = Paragraph(f'<font name="Courier" size="9">{sql.replace("<", "&lt;").replace(">", "&gt;")}</font>', normal_style)
            elements.append(sql_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # AI Insights Section
            elements.append(Paragraph("AI Analysis", heading_style))
            insights_para = Paragraph(insights, normal_style)
            elements.append(insights_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # Chart (if provided)
            if chart_base64:
                try:
                    elements.append(Paragraph("Data Visualization", heading_style))
                    # Decode base64 image
                    img_data = base64.b64decode(chart_base64)
                    img_buffer = BytesIO(img_data)
                    img = Image(img_buffer, width=5*inch, height=3*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.2*inch))
                except:
                    pass  # Skip chart if error
            
            # Data Table Section
            elements.append(Paragraph("Query Results", heading_style))
            elements.append(Paragraph(f"Total Rows: {len(data)}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create table (limit to first 50 rows and 6 columns for better fit)
            table_data = []
            max_rows = min(50, len(data))
            max_cols = min(6, len(data.columns))  # Reduced from 8 to 6
            
            # Header row
            header = list(data.columns[:max_cols])
            table_data.append(header)
            
            # Data rows
            for i in range(max_rows):
                row = []
                for col in data.columns[:max_cols]:
                    val = data.iloc[i][col]
                    # Format numbers
                    if pd.api.types.is_numeric_dtype(type(val)):
                        if isinstance(val, float):
                            row.append(f"{val:.2f}")
                        else:
                            row.append(f"{val:,}")
                    else:
                        row.append(str(val)[:20])  # Reduced from 30 to 20 chars
                table_data.append(row)
            
            # Calculate column widths to fit page
            available_width = 6.5 * inch  # Leave margins
            col_width = available_width / max_cols
            col_widths = [col_width] * max_cols
            
            # Create table with fixed column widths
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True)
            ]))
            
            elements.append(table)
            
            if len(data) > max_rows:
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(f"Note: Showing first {max_rows} of {len(data)} rows", styles['Italic']))
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except ImportError:
            # If reportlab not installed, return simple text report
            return self._generate_text_report(query, sql, data, insights)
    
    def _generate_text_report(self, query: str, sql: str, data: pd.DataFrame, insights: str) -> bytes:
        """Generate HTML report as fallback when ReportLab is not available."""
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Limit data rows for HTML display
        max_rows = min(100, len(data))
        df_html = data.head(max_rows).to_html(index=False, classes='data-table', border=0)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SQL Data Analyst Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 32px;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            color: #667eea;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .query-box {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            font-size: 16px;
            line-height: 1.6;
        }}
        .sql-box {{
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .insights-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 10px;
            font-size: 15px;
            line-height: 1.8;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 13px;
        }}
        .data-table th {{
            background: #667eea;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
        }}
        .data-table td {{
            padding: 10px 8px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .data-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .data-table tr:hover {{
            background: #f0f0f0;
        }}
        .stats {{
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            color: #0066cc;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #666;
            font-size: 13px;
        }}
        @media print {{
            body {{ margin: 0; background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 SQL Data Analyst Report</h1>
            <p>Generated on {timestamp}</p>
        </div>
        
        <div class="section">
            <div class="section-title">💬 User Question</div>
            <div class="query-box">{query}</div>
        </div>
        
        <div class="section">
            <div class="section-title">📝 Generated SQL Query</div>
            <div class="sql-box">{sql}</div>
        </div>
        
        <div class="section">
            <div class="section-title">🤖 AI Analysis</div>
            <div class="insights-box">{insights}</div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 Query Results</div>
            <div class="stats">Total Rows: {len(data):,} | Showing: {max_rows:,} rows</div>
            {df_html}
        </div>
        
        <div class="footer">
            <p>Report generated by SQL Data Analyst Agent</p>
            <p>Powered by Groq AI • llama-3.3-70b Model</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content.encode('utf-8')
    
    def get_chart_as_base64(self, fig) -> Optional[str]:
        """
        Convert Plotly figure to base64-encoded PNG.
        
        Args:
            fig: Plotly figure object
            
        Returns:
            Base64-encoded image string or None
        """
        try:
            import plotly.io as pio
            img_bytes = pio.to_image(fig, format='png', width=800, height=500)
            return base64.b64encode(img_bytes).decode('utf-8')
        except:
            return None
