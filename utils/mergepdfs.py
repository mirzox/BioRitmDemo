import os
import time

from django.conf import settings

from PyPDF2 import PdfFileMerger


def merge(file_names):
    merger = PdfFileMerger()
    base_dir = settings.BASE_DIR
    for pdf in file_names:
        merger.append(f"{base_dir}/{pdf.replace('media', 'mediafiles')}")
    o_path = f"/mediafiles/mergedresults/{str(time.time())}.pdf"
    merger.write(f"{base_dir}{o_path}")
    merger.close()
    return o_path.replace("mediafiles", 'media')
