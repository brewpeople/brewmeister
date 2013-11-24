import math
import cStringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from brew import cache


@cache.memoize()
def make_pdf(data):
    page_width, page_height = A4
    page_margin = 10.0
    qr_width, qr_height = 60.0, 60.0

    qr_margin = 5.0     # this is a desired margin, not the actual one
    num_rows = int(math.floor((page_height - 2 * page_margin) / (qr_height + qr_margin)))
    num_cols = int(math.floor((page_width - 2 * page_margin) / (qr_width + qr_margin)))

    qr_vertical_margin = ((page_height - 2 * page_margin) - num_rows * qr_height) / num_rows
    qr_horizontal_margin = ((page_width - 2 * page_margin) - num_cols * qr_width) / num_cols

    qr = QrCodeWidget(data)
    output = cStringIO.StringIO()
    p = canvas.Canvas(output, pagesize=A4)
    b = qr.getBounds()
    w, h = b[2]-b[0], b[3]-b[1]

    d = Drawing(qr_width, qr_height,
                transform=[qr_width / w, 0, 0, qr_height / h, 0, 0])
    d.add(qr)

    for i in xrange(num_cols):
        x = page_margin + i * (qr_horizontal_margin + qr_width)

        for j in xrange(num_rows):
            y = page_margin + j * (qr_vertical_margin + qr_height)
            renderPDF.draw(d, p, x, y)

    p.showPage()
    p.save()

    pdf_output = output.getvalue()
    output.close()
    return pdf_output
