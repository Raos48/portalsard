import pandas as pd
from app import SQLALCHEMY_DATABASE_URI, Estoque
import numpy as np
# Caminho do seu arquivo Excel
excel_path = 'Pasta1.xlsx'

# Substitui valores NaN por None (que será interpretado como NULL pelo MySQL)
df_excel = pd.read_excel(excel_path)
df_excel = df_excel.where(pd.notnull(df_excel), None)




from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Criar a engine e a sessão para o SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

for index, row in df_excel.iterrows():
    estoque_item = session.query(Estoque).filter(Estoque.id == row['id']).first()
    if estoque_item:
        # Se 'situacao' é NaN, substitua por None ou outro valor adequado
        situacao_value = row['situacao'] if not pd.isna(row['situacao']) else None
        estoque_item.situacao = situacao_value
        session.commit()

