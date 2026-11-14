import subprocess,glob,os
H=r'~\Documents\tax-formalization-data\taxcourt\validation\holdout\raw'
for pdf in glob.glob(os.path.join(H,'*.pdf')):
    out=subprocess.run(['pdftotext','-enc','UTF-8',pdf,'-'],capture_output=True).stdout.decode('utf-8','replace')
    pages=out.split('\f')
    if pages and not pages[-1].strip(): pages=pages[:-1]
    txt=''.join(f'\n=== [page {n}] ===\n'+p for n,p in enumerate(pages,1))
    open(pdf[:-4]+'.txt','w',encoding='utf-8',newline='\n').write(txt)
print('done')
