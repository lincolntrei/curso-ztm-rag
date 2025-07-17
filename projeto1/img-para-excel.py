# coding: utf-8

# # Conversão de img para excel

# Conversão de img para excel, pegando dados tabulares de imagens e colocando em excel

# In[37]:


import os, base64, glob
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import Markdown, display


# In[2]:


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = openai_api_key)


# In[3]:


def get_path_imagens(imagens_path):
    imagens = sorted([f for f in os.listdir(imagens_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    return [os.path.join(imagens_path, i) for i in imagens]


# In[38]:


def get_path_imagens_filtradas(img_path, padrao = "jpg"):
    path_img_padrao = os.path.join(img_path, f"*.{padrao}")
    return glob.glob(path_img_padrao)


# In[4]:


def converter_imagem(file_path):
    with open(file_path, "rb") as arquivo_imagem:
        return base64.b64encode(arquivo_imagem.read()).decode("utf-8")


# In[5]:


def montar_user_content(imagem_base64):
    user_content = [
        {"type": "text",
         "text": "Convert this menu image into structured Excel Sheet Format."},
        {"type": "image_url",
         "image_url": {
             "url": f"data:image/jpeg;base64,{imagem_base64}",
             "detail": "high"}}
    ]
    return user_content


# In[6]:


def gerar_conteudo(client, system_prompt, imagem_b64, MODEL = "gpt-4o"):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": montar_user_content(imagem_b64)}
        ],
        temperature=0
    )
    return response.choices[0].message.content


# In[7]:


def get_df_menu():
    return pd.DataFrame(columns=['CategoryTitle', 'CategoryTitleEnglish', 'SubcategoryTitle', 'SubcategoryTitleEnglish',
                                 'ItemName', 'ItemNameEnglish', 'ItemPrice', 'Calories', 'PortionSize', 'Availability', 
                                 'ItemDescription', 'ItemDescriptionEnglish'])


# In[29]:


def add_linhas(df, conteudo):
    for linha in conteudo.split('\n'):
        if linha.startswith('|') and not linha.startswith('|-'): # Garantindo que sejam dados e não header format
            colunas = [col.strip() for col in linha.split('|')[1:-1]]
            if len(colunas) == len(df.columns):
                if 'CategoryTitle' in colunas: continue # Garantindo que linha não seja header
                nova_linha = pd.Series(colunas, index=df.columns)
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            else:
                print(f"Pulando linha {linha}")
    return df


# In[9]:


system_prompt = """
Convert the menu image(s) to a structured excel sheet following the provided template and instructions
You are a data assistant that converts restaurant or cafe menus into structured Excel sheet that adheres to a specific template.
The template includes categories, subcategories, item names, prices, 
Your task is to interpret and extract the data according to the following rules and structure:

Overview:
- Each row in the spreadsheet represents a unique menu item.
- Items are organized under categories or subcategories.
- Category and Subcategory names are repeated for all items that belong to the same group.
- Some fields (e.g., subcategory columns) may be blank when not applicable.
- Item details such as names, prices, descriptions, etc., should be unique for each row.
- The price of each item must not have currency simbol.
- The uploaded menu will be appended to the current menu. Do not delete or modify any existing menu items.

Column Guide:
- **Column A — CategoryTitle:** Required. Up to 256 characters. Example: "Bebidas"
- **Column B — CategoryTitleEnglish:** Optional. Up to 256 characters. Example: "Beverages"
- **Column C — SubcategoryTitle:** Optional. Up to 256 characters or leave blank. Example: "Sucos"
- **Column D — SubcategoryTitleEnglish:** Optional. Up to 256 characters or leave blank. Example: "Juices"
- **Column E — ItemName:** Required. Up to 256 characters. Example: "Água Mineral"
- **Column F — ItemNameEnglish:** Optional. Up to 256 characters or leave blank. Example: "Mineral Water"
- **Column G — ItemPrice:** Required. Accept formats: "2.50" or "2,50"
- **Column H — Calories:** Optional. Numeric only. Example: "150"
- **Column I — PortionSize:** Required. Text value. Example: "500ml"
- **Column J — Availability:** Optional. Accepts only 1 (available) or 0 (not available)
- **Column K — ItemDescription:** Optional. Up to 500 characters. Example: "Contém minerais essenciais"
- **Column L — ItemDescriptionEnglish:** Optional. Up to 500 characters. Example: "Contains essential minerals"

Notes:
- Make sure all data strictly follows the accepted formats and values to maintain consistency.
- Always check for accuracy and consistency before processing the spreadsheet.
- Your role is to extract structured and clean data from these Excel rows based on this specification.
"""


# ## Testes

# In[10]:


imagens_path = os.path.join(os.getcwd(), "img")


# In[11]:


imagens_path_list = get_path_imagens(imagens_path)
imagens_b64 = [converter_imagem(i) for i in imagens_path_list]


# In[35]:


df = get_df_menu()
for imagem in imagens_b64:
    conteudo = gerar_conteudo(client, system_prompt, imagem)
    df = add_linhas(df, conteudo)


# In[39]:


df.to_excel("dados.xlsx", index=False)

