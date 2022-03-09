import os
import sys
import threading
import pikepdf
from tqdm import tqdm

#####
# Author Mustafa Azim
# HackPDF Tool
#####


dsep = os.sep
lsep = os.linesep
rsep = '\r'
ver = '0.1'

event = threading.Event()
completed = threading.Event()


def progressbar(progress: int):
    try:
        bar = tqdm(range(progress))
        bar.colour = 'GREEN'
        bar.unit = ' PDF/Sec'
        for i in bar:
            event.wait(0.01)
            event.clear()
        completed.set()
    except Exception as ex:
        print(f'Error progressbar    {ex}   {ex.args}')
        main.event = False
        completed.set()


def findpdf() -> list:
    files = os.listdir(os.getcwd())
    pdf = []
    completed.clear()
    event.clear()
    th = threading.Thread(target=progressbar, args=(100,))
    th.start()
    for f in files:
        if f.endswith('.pdf'):
            pdf.append(f)
            event.set()
    event.set()
    if len(pdf) > 0:
        os.makedirs(name='Output', exist_ok=True)
        print(f'Working on PDF' + f's:{rsep}' if len(pdf) > 1 else f':{rsep}')
        for p in pdf:
            print(f'-   {p}{rsep}')
        return pdf
    else:
        print(f'No PDF file(s) found!{lsep}')


def removepass():
    pdf = findpdf()
    path = os.getcwd()
    try:
        for pdffile in pdf:
            password = ''
            while True:
                try:
                    with pikepdf.Pdf.open(filename_or_stream=pdffile, password=password,
                                          allow_overwriting_input=True) as pfile:
                        pfile.save(filename_or_stream=f'{path}{dsep}Output{dsep}{pdffile}', encryption=False)
                        pfile.close()
                        break
                except Exception as ex:
                    for e in ex.args:
                        if str(e).lower().__contains__('invalid password'):
                            password = input(f'{pdffile} protected, enter password:')
                        else:
                            break

    except Exception as ex:
        print(f'Error removepass {ex.args}')


def merge():
    pdf = findpdf()
    path = os.getcwd()
    ordinalpdf = []
    try:
        unordered = []
        ordered = []
        isstringarray = False
        for i in pdf:
            n = str(i).split('_') if (str(i).__contains__('_')) else i
            if type(n) is list:
                if len(n) > 0 and n[0].isnumeric():
                    isstringarray = False
            elif str(n).isnumeric() and not str(n).isalpha():
                isstringarray = False
            else:
                isstringarray = True
                break
        if not isstringarray:
            for i in pdf:
                n = str(i).split('_') if (str(i).__contains__('_')) else i
                if type(n) is list:
                    if len(n) > 0 and n[0].isnumeric():
                        unordered.append(int(n[0]))
                elif str(n).isnumeric() and not str(n).isalpha():
                    unordered.append(int(n[0]))
                else:
                    unordered.append(n)

            _unordered = unordered
            cnt = len(unordered) - 1
            while cnt >= 0:
                if type(_unordered[cnt]) == int:
                    m = min(_unordered)
                    ordered.append(m)
                    _unordered.remove(m)
                elif type(_unordered[cnt]) == str:
                    ordered = _unordered
                    break
                cnt -= 1
            if len(ordinalpdf) < 1:
                for o in ordered:
                    for p in pdf:
                        if str(p).startswith(str(o)):
                            ordinalpdf.append(p)
                            break
        else:
            ordinalpdf = pdf

        m_password = ''
        if len(ordinalpdf) > 0:
            while True:
                try:
                    with pikepdf.Pdf.open(filename_or_stream=ordinalpdf[0], password=m_password,
                                          allow_overwriting_input=True) as masterpdf:
                        ordained = ordinalpdf
                        ordained.remove(ordained[0])
                        completed.clear()
                        event.clear()
                        th = threading.Thread(target=progressbar, args=(len(pdf),))
                        th.start()
                        for pdffile in ordained:
                            password = ''
                            event.clear()
                            while True:
                                try:
                                    with pikepdf.Pdf.open(filename_or_stream=pdffile, password=password,
                                                          allow_overwriting_input=True) as pfile:
                                        masterpdf.pages.extend(pfile.pages)
                                        event.set()
                                        pfile.close()
                                        break
                                except Exception as ex:
                                    for e in ex.args:
                                        if str(e).lower().__contains__('invalid password'):
                                            password = input(f'{pdffile} protected, enter password:')
                                        else:
                                            break
                        event.set()
                        masterpdf.save(filename_or_stream=f'{path}{dsep}Output{dsep}Merged.pdf', encryption=False)
                        break
                except Exception as ex:
                    for e in ex.args:
                        if str(e).lower().__contains__('invalid password'):
                            m_password = input(f'{pdffile} protected, enter password:')
                        else:
                            break

    except Exception as ex:
        print(f'Error merge {ex.args}')


def extractimages():
    pdf = findpdf()
    path = os.getcwd()
    try:
        for pdffile in pdf:
            password = ''
            while True:
                try:
                    with pikepdf.Pdf.open(filename_or_stream=pdffile, password=password,
                                          allow_overwriting_input=True) as pfile:
                        os.makedirs(f'Output{dsep}{pdffile}_imanges', exist_ok=True)
                        for p in pfile.pages:
                            for i in p.images.keys():
                                image = p.images[i]
                                pdfi = pikepdf.PdfImage(image)
                                pimage = pdfi.as_pil_image()
                                pimage.save(fp=f'{path}{dsep}Output{dsep}{pdffile}_imanges{dsep}{i}_page{p.index}.jpg')
                        pfile.close()
                        break
                except Exception as ex:
                    for e in ex.args:
                        if str(e).lower().__contains__('invalid password'):
                            password = input(f'{pdffile} protected, enter password:')
                        else:
                            break

    except Exception as ex:
        print(f'Error extractimages {ex.args}')


def options():
    print(f'What would you like to do for PDF file(s):{lsep}{lsep}'
          f'[1] Remove Password from file(s) (Requires old Password){lsep}'
          f'[2] Extract Images from file(s){lsep}'
          f'[3] Merge PDF files {lsep}'
          f'    if PDF files\' names contain ordinal number (n_) where n is integer number followed by \'_\'{lsep}'
          f'the merge will be executed in order.'
          f'Example: 1_a.pdf 2_a.pdf 3_a.pdf will be merged in order as 1_a.pdf 2_a.pdf 3_a.pdf and so on{lsep}'
          f'[4] Exit{lsep}{lsep}'
          f'          Processed files will be in Output folder in the script\'s directory         {lsep}'
          f'{os.getcwd()}{dsep}Output{lsep}'
          f'==========================================================================================================='
          f'{lsep}{lsep}'
          f'          PDFs files should be copied to the script\'s directory        {lsep}'
          f'{os.getcwd()}{lsep}'
          f'==========================================================================================================='
          f'{lsep}{lsep}')
    try:
        inp = input(f'Enter the option number:{lsep}')
        match inp:
            case '1':
                removepass()
            case '2':
                extractimages()
            case '3':
                merge()
            case '4':
                pass
            case _:
                pass
    except Exception as ex:
        print(f'options   {ex.args}')


def version():
    print(f'HackPDF tool    {ver}v    Mustafa Azim'
          f'    mustafaz.com{lsep}')


def main():
    try:
        os.chdir(str(__file__).removesuffix('/main').removesuffix('/main.py'))
        version()
        options()
        completed.wait(timeout=300)
        print(f'Done!   Exiting...')
        sys.exit()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
