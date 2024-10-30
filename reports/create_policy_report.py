from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.pdfgen import canvas
from reportlab.platypus.tableofcontents import TableOfContents as TOC
from datetime import date
from io import BytesIO
import base64
from PIL import Image as PILImage

class CustomTableOfContents(TOC):
    def __init__(self):
        TOC.__init__(self)
        self.dotsMinLevel = 0  # Remove dots in the table of contents
    
    def wrap(self, availWidth, availHeight):
        "Overide wrap to set the availableWidth"
        self.availableWidth = availWidth
        return TOC.wrap(self, availWidth, availHeight)

    def drawEntries(self, canvas, page):
        """Don't do anything. We'll handle this in draw() method."""
        pass

    def draw(self):
        """Draw the table of contents without any placeholder text."""
        if len(self._entries) > 0:
            return TOC.draw(self)
        else:
            return []

class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [Frame(
            self.leftMargin, self.bottomMargin, self.width, self.height-0.4*inch, id='normal'
        )], onPage=header_footer, onPageEnd=header_footer)
        self.addPageTemplates([template])
        self.toc = CustomTableOfContents()
        self.content = {}
        self.pagesize = letter
        self.width, self.height = self.pagesize

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            elif style == 'Heading2':
                self.notify('TOCEntry', (1, text, self.page))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(7.5*inch, 0.75*inch, f"Page {self._pageNumber} of {page_count}")

def header_footer(canvas, doc):
    canvas.saveState()
    
    # Header
    page_width, page_height = letter

    # Adjust the header image to fit the width of the page
    header_image_path = 'static/letterhead.png'
    header_image_width = page_width
    header_image_height = 1*inch

    # canvas.drawImage(header_image_path, 0, page_height - header_image_height, width=header_image_width, height=header_image_height, preserveAspectRatio=True)
    
    # Footer
    canvas.setFont("Helvetica", 9)
    footer_text = f"{date.today().strftime('%B %d, %Y')} | {doc.content.get('title', '')}"
    canvas.drawString(1*inch, 0.75*inch, footer_text)
    
    canvas.restoreState()

def generate_table(data, colWidths=None):
    # Create paragraph styles for cell content
    header_style = ParagraphStyle(
        'HeaderStyle',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=HexColor('#000000')
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        wordWrap='CJK'
    )

    # Convert all cell contents to Paragraphs for proper wrapping
    formatted_data = []
    for i, row in enumerate(data):
        formatted_row = []
        for cell in row:
            if isinstance(cell, str):
                style = cell_style
                formatted_row.append(Paragraph(cell.replace('<', '&lt;').replace('>', '&gt;'), style))
            else:
                formatted_row.append(cell)  # Keep non-string items as is
        formatted_data.append(formatted_row)

    # Calculate column widths if not provided
    if colWidths is None:
        colWidths = [None] * len(data[0])  # Equal width for all columns
    t = Table(formatted_data, colWidths=colWidths)

    # Set alternating row colors using TableStyle
    t.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#000000')),
        ('LINEABOVE', (0,1), (-1,-1), .50, HexColor('#000000')),
        ('LINEBELOW', (0,-1), (-1,-1), 1, HexColor('#000000')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F0F3F9')),  # Even rows background
        ('BACKGROUND', (0, 2), (-1, -1), HexColor('#FFFFFF')),  # Odd rows background
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.25, HexColor('#CCCCCC')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

    ]))

    # Apply alternating row colors
    t.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#c2c4d2 '), HexColor('#FFFFFF')]),
    ]))

    return t

def create_policy_report_pdf(policy_report, plot_html):
    buffer = BytesIO()
    title = policy_report.get('policy_summary', {}).get('title', 'Policy Analysis Report')
    doc = MyDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=36, bottomMargin=72)
    doc.content = {'title': title}

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 0.4*inch, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=header_footer)
    doc.addPageTemplates([template])
    elements = []
 
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionHeader',
                              fontSize=14,
                              fontName='Helvetica-Bold',
                              textColor=HexColor('#FFFFFF')))
    styles.add(ParagraphStyle(name='ContentHeader',
                              fontSize=11,
                              fontName='Helvetica-Bold',
                              textColor=HexColor('#000000')))
    styles.add(ParagraphStyle(name='ContentText',
                              fontSize=10,
                              fontName='Helvetica',
                              textColor=HexColor('#000000')))
    
    # Add the header image and spacer to the elements list
    elements.append(PlatypusImage('static/letterhead.png', width=doc.width, height=1*inch))
    elements.append(Spacer(1, 86))
    
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 24))

    toc = CustomTableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name='TOCHeading1', fontSize=14, leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
        ParagraphStyle(name='TOCHeading2', fontSize=12, leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=14),
        ParagraphStyle(name='TOCHeading3', fontSize=10, leftIndent=60, firstLineIndent=-20, spaceBefore=2, leading=12),
    ]
    elements.append(PageBreak())
    elements.append(Paragraph("Table of Contents", styles['Heading1']))
    elements.append(toc)
    elements.append(PageBreak())

    elements.append(Paragraph("United Nations Goal 5 Targets: ", styles['Heading1']))
    elements.append(Spacer(1, 32))
    elements.append(Paragraph("5.1 End all forms of discrimination against all women and girls everywhere."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.2 Eliminate all forms of violence against all women and girls in the public and private spheres, including trafficking and sexual and other types of exploitation."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.3 Eliminate all harmful practices, such as child, early and forced marriage and female genital mutilation."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.4 Recognize and value unpaid care and domestic work through the provision of public services, infrastructure and social protection policies and the promotion of shared responsibility within the household and the family as nationally appropriate."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.5 Ensure women's full and effective participation and equal opportunities for leadership at all levels of decision-making in political, economic and public life."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.6 Ensure universal access to sexual and reproductive health and reproductive rights as agreed in accordance with the Programme of Action of the International Conference on Population and Development and the Beijing Platform for Action and the outcome documents of their review conferences."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.A Undertake reforms to give women equal rights to economic resources, as well as access to ownership and control over land and other forms of property, financial services, inheritance and natural resources, in accordance with national laws."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.B Enhance the use of enabling technology, in particular information and communications technology, to promote the empowerment of women."))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("5.C Adopt and strengthen sound policies and enforceable legislation for for the promotion of gender equality and the empowerment of all women and girls at all levels."))

    elements.append(PageBreak())

    # Add plot
    if plot_html:
        elements.append(Paragraph("Goal 5 Alignment Chart", styles['Heading1']))
        elements.append(Spacer(1, 22)) 
        try:
            img_data = plot_html.split('base64,')[1].split('"')[0]
            img_bytes = base64.b64decode(img_data)
            img = PILImage.open(BytesIO(img_bytes))
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            img_width = 7 * inch
            img_height = aspect * img_width
            elements.append(PlatypusImage(BytesIO(img_bytes), width=img_width, height=img_height))
        except Exception as e:
            print(f"Error processing plot image: {e}")
            elements.append(Paragraph("Error: Plot image could not be included"))
        elements.append(PageBreak())

    # Policy Summary
    elements.append(Paragraph("Policy Summary", styles['Heading1']))
    elements.append(Spacer(1, 22))  
    summary = policy_report.get('policy_summary', {})
    elements.append(Paragraph(f"<b>Focus Area:</b> {summary.get('focus_area', 'N/A')}"))
    elements.append(Spacer(1, 22))
    elements.append(Paragraph(f"<b>Brief Overview:</b> {summary.get('brief_overview', 'N/A')}"))
    elements.append(PageBreak())

    if 'sdg5_alignment' in policy_report:
        elements.append(Paragraph("Target Goal Alignment", styles['Heading1']))
        elements.append(Spacer(1, 24))
        sdg5 = policy_report['sdg5_alignment']
        elements.append(Paragraph(f"<b><h3>Overall Score:</b> {sdg5.get('overall_score', 'N/A')}/100</h3>"))
        elements.append(Spacer(1, 24))  # Add some space before the tables
    
        breakdown = sdg5.get('breakdown', [])
        for i, item in enumerate(breakdown):
            targets = item.get('targets', [item.get('target', 'N/A')])  # Fallback to 'target' if 'targets' is not present
            for j, t in enumerate(targets):
                target = "Target: " + t
                elements.append(Paragraph(target, styles['ContentHeader']))
                elements.append(Spacer(1, 12))  # Add some space before the table

                sdg5_data = [
                    ["Score", str(item.get('score', 'N/A'))],
                    ["Analysis", item.get('analysis', 'N/A')]
                ]
                
                # Generate and add the table
                elements.append(generate_table(sdg5_data, colWidths=[1.5*inch, 5*inch]))
                
                # Add space after each table except the last one
                if not (i == len(breakdown) - 1 and j == len(targets) - 1):
                    elements.append(Spacer(1, 64))  # Add some space after each table
    
        elements.append(PageBreak())

    if 'bias_analysis' in policy_report:
        bias = policy_report['bias_analysis']
        elements.append(Paragraph("Bias Analysis", styles['Heading1']))
        elements.append(Spacer(1, 22)) 
        if 'explicit_biases' in bias and bias['explicit_biases']:
            elements.append(Paragraph("Explicit Biases", styles['ContentHeader']))
            elements.append(Spacer(1, 22)) 
            for item in bias.get('explicit_biases', []):
                items = [
                    ["Description", str(item.get('description', 'N/A'))],
                    ["Potential Impact", str(item.get('potential_impact', 'N/A'))],
                    ["Recommendation", str(item.get('recommendation', 'N/A'))]
                                    ]
                elements.append(generate_table(items, colWidths=[1.5*inch, 5*inch]))
                elements.append(Spacer(1, 32))
                
        if 'implicit_biases' in bias and bias['implicit_biases']:
            elements.append(Paragraph("Implicit Biases", styles['ContentHeader']))
            elements.append(Spacer(1, 22)) 
            for item in bias.get('implicit_biases', []):
                items = [
                    ["Description", str(item.get('description', 'N/A'))],
                    ["Potential Impact", str(item.get('potential_impact', 'N/A'))],
                    ["Recommendation", str(item.get('recommendation', 'N/A'))]
                    
                ]
                elements.append(generate_table(items, colWidths=[1.5*inch, 5*inch]))
                elements.append(Spacer(1, 32))

                
        elements.append(PageBreak())

    # Cost Effectiveness Analysis
    if 'cost_effectiveness_analysis' in policy_report:
        cost = policy_report['cost_effectiveness_analysis']
        elements.append(Paragraph("Cost Effectiveness Analysis", styles['Heading1']))
        elements.append(Spacer(1, 22)) 
        items = [
            ["Overall Rating", cost.get('overall_rating', 'N/A')],
            ["Explanation", cost.get('explanation', 'N/A')],
            ["Key Factors", " ".join(cost.get('key_factors', []))]
                  ]
        elements.append(generate_table(items, colWidths=[1.5*inch, 5*inch]))
        elements.append(PageBreak())
        
    # Improvement Recommendations
    if 'improvement_recommendations' in policy_report:
        elements.append(Paragraph("Improvement Recommendations", styles['Heading1']))
        elements.append(Spacer(1, 22)) 
        for rec in policy_report['improvement_recommendations']:
            # Add "Area of Improvement" as a Paragraph
            area_of_improvement = "Area of Improvement: " + rec.get('area', 'N/A')
            elements.append(Paragraph(area_of_improvement, styles['Heading2']))
            elements.append(Spacer(1, 12))  # Add some space before the table
            
            items = [
                ["Current State", rec.get('current_state', 'N/A')],
                ["Proposed Change", rec.get('proposed_change', 'N/A')],
                ["Expected Impact", rec.get('expected_impact', 'N/A')],
                ["Implementation Challenges", rec.get('implementation_challenges', 'N/A')],
                ["Priority Level", rec.get('priority_level', 'N/A')],
            ]
            
            # Generate and add the table
            elements.append(generate_table(items, colWidths=[1.5*inch, 5*inch]))
            elements.append(PageBreak())

    # Overall Assessment
    if 'overall_assessment' in policy_report:
        elements.append(Paragraph("Overall Assessment", styles['Heading1']))
        elements.append(Spacer(1, 22)) 
        assessment = policy_report['overall_assessment']
        items = [
            ["Strengths", " ".join(assessment.get('strengths', []))],
            ["Weaknesses", " ".join(assessment.get('weaknesses', []))],
            ["Opportunities", " ".join(assessment.get('opportunities', []))],
            ["Threats", " ".join(assessment.get('threats', []))]
          
        ]
        elements.append(generate_table(items, colWidths=[1.5*inch, 5*inch]))
        elements.append(PageBreak())
    

    # Conclusion
    if 'conclusion' in policy_report:
        conclusion = policy_report['conclusion']
        elements.append(Paragraph("Conclusion", styles['Heading1']))
        elements.append(Spacer(1, 22)) 
        if 'summary' in conclusion:
            elements.append(Paragraph("Summary: ", styles['ContentHeader']))
            elements.append(Spacer(1, 12)) 
            elements.append(Paragraph(f"{conclusion.get('summary', 'N/A')}"))
            elements.append(Spacer(1, 22)) 

        if 'key_takeaways' in conclusion:
            elements.append(Paragraph(f"Key Takeaways:", styles['ContentHeader']))
            elements.append(Spacer(1, 12)) 
            for takeaway in conclusion.get('key_takeaways', []):
                elements.append(Paragraph(f"• {takeaway}"))
            elements.append(Spacer(1, 22)) 
        if 'final_recommendation' in conclusion:
            elements.append(Paragraph(f"Recommendations:", styles['ContentHeader']))
            elements.append(Spacer(1, 12)) 
            elements.append(Paragraph(f"{conclusion.get('final_recommendation', 'N/A')}"))
        elements.append(PageBreak())

    # Build the PDF
    doc.multiBuild(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()