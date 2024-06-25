from fpdf import FPDF
import io

def generate_pdf(filename, audit_result):
    """
    生成包含审核结果的 PDF 文件。
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Audit Report for {filename}", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=str(audit_result))
    
    # 保存 PDF 到内存
    pdf_output = io.BytesIO()
    pdf.output(dest='S').encode('latin1')  # 'S' 表示将 PDF 内容写入字符串
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)
    
    return pdf_output