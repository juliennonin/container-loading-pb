import os
create_out = 'mkdir out'
tikz_to_pdf = 'pdflatex -output-directory=out testA'
pdf_to_png = 'convert -density 300 out/testA.pdf -quality 90 testA.png'
remove_out = 'rm -rd out'
os.system(create_out)
os.system(tikz_to_pdf)
os.system(pdf_to_png)
os.system(remove_out)
