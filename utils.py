# -*- coding: utf-8 -*-
import re
import textwrap
from pypdf import PdfMerger

from PIL import Image, ImageDraw, ImageFont

file_background = 'files/bg.png'


def create_pdf_file(title, text, doctor, comment, user_id, index):
    img = Image.open(file_background).convert('RGB')
    font = ImageFont.truetype("Manrope-Regular.ttf", size=60)
    idraw = ImageDraw.Draw(img)

    doctor = "Врач: " + doctor

    idraw.text((165, 120), '\n'.join(line.strip() for line in re.findall(r'.{1,60}(?:\s+|$)', doctor)), font=font,
               fill=(0, 0, 0))
    idraw.text((165, 250), '\n'.join(line.strip() for line in re.findall(r'.{1,60}(?:\s+|$)', title)), font=font,
               fill=(0, 0, 0))
    idraw.text((165, 350), '\n'.join(line.strip() for line in re.findall(r'.{1,60}(?:\s+|$)', text)), font=font,
               fill=(0, 0, 0))
    idraw.text((165, 2630), '\n'.join(line.strip() for line in re.findall(r'.{1,60}(?:\s+|$)', comment)), font=font,
               fill=(0, 0, 0))


    file_path = f'images/{user_id}_{index}.pdf'
    img.save(file_path)
    return file_path
    # img = Image.open('test_text.png')
    # img.show()


def merge_pdf_files(pdf_files, user_id):

    merger = PdfMerger()

    for pdf in pdf_files:
        merger.append(pdf)

    file_name = f"{user_id} памятка.pdf"
    merger.write(file_name)
    merger.close()
    return file_name