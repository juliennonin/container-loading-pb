import os

def convert(dir, filename):
    create_out = f'mkdir {dir}/out'
    tikz_to_pdf = f'pdflatex -output-directory={dir}/out {dir}/{filename}'
    pdf_to_png = f'convert -density 300 {dir}/out/{filename}.pdf -quality 90 {dir}/{filename}.png'
    remove_out = f'rm -rd {dir}/out'
    # os.system('ls')
    os.system(create_out)
    os.system(tikz_to_pdf)
    os.system(pdf_to_png)
    os.system(remove_out)
