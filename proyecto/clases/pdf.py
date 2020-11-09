from fpdf import FPDF
from flask import make_response
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Logo
        self.image('proyecto/static/images/logo2.png', 10, 8, 15)
        # Arial bold 15
        self.set_font('Helvetica', 'B', 20)
        # Move to the right
        self.cell(105)
        # Title
        self.cell(50, 10, 'StarCyber', 0, 0, 'C')
        fecha = datetime.now()
        self.set_font('Arial', 'B', 10)
        self.cell(130, 10, 'Fecha: ' + str(fecha.day) + '-' + str(fecha.month) + '-' + str(fecha.year), 0, 0, 'R')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 8, '2020', 0, 0, 'L')
        self.cell(0, 10, 'Pagina ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def pdfPloteo(plts):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page(orientation='L')
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.cell(50, 10, 'Reportes de ploteos', 0, 0, 'C')
    pdf.ln(10)
    pdf.set_font('Courier', 'B', 8)
    col_width = page_width / 4
    pdf.ln(1)
    th = pdf.font_size
    pdf.cell(30)
    pdf.cell(15, th, "ID", 1, 0, 'C')
    pdf.cell(60, th, "Fecha_ploteada", 1, 0, 'C')
    pdf.cell(40, th, "Latitud", 1, 0, 'C')
    pdf.cell(40, th, "Longitud", 1, 0, 'C')
    pdf.cell(60, th, "Registro", 1, 0, 'C')
    pdf.ln(th)
    pdf.set_font('Courier', '', 8)

    for plt in plts:
        pdf.cell(30)
        pdf.cell(15, th, str(plt.plo_id), 1,0,'C')
        pdf.cell(60, th, str(plt.plo_fecha_creacion), 1,0,'C')
        pdf.cell(40, th, str(plt.plo_lat), 1,0,'C')
        pdf.cell(40, th, str(plt.plo_lon), 1,0,'C')
        pdf.cell(60, th, str(plt.plo_fecha), 1,0,'C')
        pdf.ln(th)

    pdf.ln(10)
    pdf.set_font('Times', '', 10.0)
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'inline', filename="reportes.pdf")
    response.headers.set('Content-Type', 'application/pdf')
    return response

def pdfPloteo2(plts):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page(orientation='L')
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.cell(50, 10, 'Reportes de canciones', 0, 0, 'C')
    pdf.ln(10)
    pdf.set_font('Courier', 'B', 8)
    col_width = page_width / 4
    pdf.ln(1)
    th = pdf.font_size
    pdf.cell(60)
    pdf.cell(15, th, "ID", 1, 0, 'C')
    pdf.cell(60, th, "Busqueda", 1, 0, 'C')
    pdf.cell(60, th, "Fecha Busqueda", 1, 0, 'C')
    pdf.ln(th)
    pdf.set_font('Courier', '', 8)

    for plt in plts:
        pdf.cell(60)
        pdf.cell(15, th, str(plt.son_id), 1,0,'C')
        pdf.cell(60, th, str(plt.son_busqueda), 1,0,'C')
        pdf.cell(60, th, str(plt.son_fecha), 1,0,'C')
        pdf.ln(th)

    pdf.ln(10)
    pdf.set_font('Times', '', 10.0)
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'inline', filename="reportes_canciones.pdf")
    response.headers.set('Content-Type', 'application/pdf')
    return response