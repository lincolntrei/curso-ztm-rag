# coding: utf-8

# # PDF para imagens
# Esse código visa converter pdf para imagens jpg.

# In[1]:


from pdf2image import convert_from_path
import os, glob


# In[2]:


def get_pdf(caminho_pdf):
    padrao = os.path.join(caminho_pdf, "*.pdf")
    return glob.glob(padrao)


# In[3]:


def pdf_para_imagens(lista_pdf, caminho_saida, dpi=500):
    for pdf in lista_pdf:
        paginas = convert_from_path(pdf, dpi=dpi)
        nome_pdf = os.path.basename(pdf)
        nome_pdf = os.path.splitext(nome_pdf)[0]
        for i, pagina in enumerate(paginas):
            pagina.save(f"{caminho_saida}/{nome_pdf}_pag{i + 1}.jpg", 'JPEG')


# In[4]:


caminho_pdf = "pdf"
caminho_img = "img"

lista_pdf = get_pdf(caminho_pdf)
pdf_para_imagens(lista_pdf, caminho_img)

