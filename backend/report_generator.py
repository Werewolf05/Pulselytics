"""
PDF Report Generator for Pulselytics
Generates professional PDF analytics reports with charts and metrics
"""
import os
import io
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
        PageBreak, Image, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not installed. PDF generation disabled.")


# Set seaborn style
sns.set_style("whitegrid")
sns.set_palette("husl")


def generate_engagement_chart(data: Dict, output_path: str) -> str:
    """Generate engagement trend chart as PNG"""
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        trend = data.get('trend', [])
        if trend:
            df = pd.DataFrame(trend)
            ax.plot(df['date'], df['engagement'], marker='o', linewidth=2, markersize=6)
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Engagement', fontsize=10)
            ax.set_title('Engagement Trend', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path
    except Exception as e:
        print(f"Error generating engagement chart: {e}")
        return None


def generate_platform_chart(data: Dict, output_path: str) -> str:
    """Generate platform distribution chart as PNG"""
    try:
        fig, ax = plt.subplots(figsize=(6, 4))
        
        platforms = data.get('platforms', [])
        if platforms:
            df = pd.DataFrame(platforms)
            colors_list = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b']
            ax.bar(df['platform'], df['posts'], color=colors_list[:len(df)])
            ax.set_xlabel('Platform', fontsize=10)
            ax.set_ylabel('Posts', fontsize=10)
            ax.set_title('Platform Distribution', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path
    except Exception as e:
        print(f"Error generating platform chart: {e}")
        return None


def generate_pdf_report(
    client_name: str,
    date_range: str,
    analytics_data: Dict,
    output_path: str
) -> bool:
    """
    Generate a comprehensive PDF report
    
    Args:
        client_name: Name of the client
        date_range: Date range for the report (e.g., "30days", "90days")
        analytics_data: Dictionary containing analytics metrics
        output_path: Path where PDF will be saved
        
    Returns:
        True if successful, False otherwise
    """
    if not REPORTLAB_AVAILABLE:
        print("Error: ReportLab not installed. Run: pip install reportlab")
        return False
    
    try:
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Container for elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        # Title
        title_text = f"Social Media Analytics Report"
        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        subtitle = f"{client_name} | {date_range}"
        elements.append(Paragraph(subtitle, subtitle_style))
        
        # Generated date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#94a3b8'),
            alignment=TA_CENTER
        )
        gen_date = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(gen_date, date_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive Summary Section
        elements.append(Paragraph("Executive Summary", heading_style))
        
        # KPI Table
        kpi_data = [
            ['Metric', 'Value'],
            ['Total Posts', f"{analytics_data.get('total_posts', 0):,}"],
            ['Average Likes', f"{analytics_data.get('avg_likes', 0):,.1f}"],
            ['Average Comments', f"{analytics_data.get('avg_comments', 0):,.1f}"],
            ['Average Views', f"{analytics_data.get('avg_views', 0):,.0f}"],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Generate and add charts
        temp_dir = os.path.join(os.path.dirname(output_path), 'temp_charts')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Engagement chart
        elements.append(Paragraph("Engagement Trend", heading_style))
        engagement_chart_path = os.path.join(temp_dir, 'engagement.png')
        if generate_engagement_chart(analytics_data, engagement_chart_path):
            img = Image(engagement_chart_path, width=6*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2*inch))
        
        # Platform distribution
        elements.append(Paragraph("Platform Distribution", heading_style))
        platform_chart_path = os.path.join(temp_dir, 'platforms.png')
        if generate_platform_chart(analytics_data, platform_chart_path):
            img = Image(platform_chart_path, width=5*inch, height=3.3*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2*inch))
        
        # Top Posts Section
        elements.append(PageBreak())
        elements.append(Paragraph("Top Performing Posts", heading_style))
        
        top_posts = analytics_data.get('top_posts', [])[:5]
        if top_posts:
            for i, post in enumerate(top_posts, 1):
                post_data = [
                    [f"#{i}", f"{post.get('platform', 'N/A').capitalize()} | @{post.get('username', 'N/A')}"],
                    ['Caption', post.get('caption', 'N/A')[:150] + '...' if len(post.get('caption', '')) > 150 else post.get('caption', 'N/A')],
                    ['Engagement', f"❤ {post.get('likes', 0):,} | 💬 {post.get('comments', 0):,} | 👁 {post.get('views', 0):,}"]
                ]
                
                post_table = Table(post_data, colWidths=[0.8*inch, 5.2*inch])
                post_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f1f5f9')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(post_table)
                elements.append(Spacer(1, 0.15*inch))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#94a3b8'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Generated by Pulselytics | Social Media Analytics Platform", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Clean up temp charts
        try:
            if os.path.exists(engagement_chart_path):
                os.remove(engagement_chart_path)
            if os.path.exists(platform_chart_path):
                os.remove(platform_chart_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Test report generation
    sample_data = {
        'total_posts': 156,
        'avg_likes': 4523.5,
        'avg_comments': 234.7,
        'avg_views': 45678,
        'trend': [
            {'date': '2025-10-01', 'engagement': 5000},
            {'date': '2025-10-08', 'engagement': 5500},
            {'date': '2025-10-15', 'engagement': 6200},
            {'date': '2025-10-22', 'engagement': 5800},
            {'date': '2025-10-29', 'engagement': 6500},
        ],
        'platforms': [
            {'platform': 'instagram', 'posts': 45},
            {'platform': 'youtube', 'posts': 38},
            {'platform': 'twitter', 'posts': 52},
            {'platform': 'facebook', 'posts': 21},
        ],
        'top_posts': [
            {
                'platform': 'instagram',
                'username': 'nike',
                'caption': 'Just Do It - New campaign launch! #Nike #Sports',
                'likes': 15000,
                'comments': 450,
                'views': 75000
            },
            {
                'platform': 'youtube',
                'username': 'nike',
                'caption': 'Behind the Scenes: Making of the new collection',
                'likes': 12500,
                'comments': 320,
                'views': 125000
            }
        ]
    }
    
    output = os.path.join(os.path.dirname(__file__), 'test_report.pdf')
    success = generate_pdf_report('Nike', '30 days', sample_data, output)
    
    if success:
        print(f"✅ Test report generated: {output}")
    else:
        print("❌ Report generation failed")
