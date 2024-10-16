import pandas as pd 
import duckdb
from pathlib import Path

class MarketData:
    def __init__(self, data_path):   
        self.data_path = Path(data_path)
        self.con = duckdb.connect(database=':memory:')

    def load_sales(self):
        try:
            if not self.data_path.exists():
                raise FileNotFoundError(f"File not found: {self.data_path}")
            df = pd.read_excel(self.data_path, sheet_name='vendas', header=0, dtype=object)
            df['DATA'] = pd.to_datetime(df['DATA'], format='%d-%m-%y')
            df['VALOR_VENDA'] = pd.to_numeric(df['VALOR_VENDA']).round(2)
            self.con.execute("CREATE TABLE sales AS SELECT * FROM df")
        except Exception as e:
            print(f"Error loading sales data: {e}")
            raise

    def load_products(self):
        df = pd.read_excel(self.data_path, sheet_name='produtos', header=0, dtype=object)
        self.con.execute("CREATE TABLE products AS SELECT * FROM df")

    def best_selling_day(self): 
        return self.con.execute("SELECT STRFTIME('%d/%m/%Y', DATA), SUM(VALOR_VENDA) AS TOTAL_VENDA FROM sales GROUP BY DATA ORDER BY TOTAL_VENDA DESC LIMIT 1").fetchone()

    def daily_sales(self):
        self.con.execute("CREATE VIEW IF NOT EXISTS daily_sales AS SELECT DATA, SUM(VALOR_VENDA) AS TOTAL_VENDA FROM sales GROUP BY DATA ORDER BY DATA").fetchall()

    def monthly_sales(self):
        self.con.execute("CREATE VIEW IF NOT EXISTS monthly_sales AS SELECT STRFTIME('%m/%Y', DATA) AS MES, SUM(VALOR_VENDA) AS TOTAL_VENDA FROM sales GROUP BY MES ORDER BY MES").fetchall()

    def sales_per_product(self):
        return self.con.execute("CREATE VIEW IF NOT EXISTS sales_per_product AS  SELECT p.PREÇO_KG, SUM(s.VALOR_VENDA) AS TOTAL_VENDA, p.NOME_PRODUTO FROM sales s INNER JOIN products p ON s.ID_PRODUTO = p.ID_PRODUTO GROUP BY p.PREÇO_KG, p.NOME_PRODUTO ORDER BY TOTAL_VENDA DESC").fetchall()

    def best_selling_product_in_kg(self):
        return self.con.execute("SELECT p.NOME_PRODUTO, COUNT(p.ID_PRODUTO), SUM(s.VALOR_VENDA) AS TOTAL_VENDAS, SUM((s.VALOR_VENDA / p.PREÇO_KG)) AS Quantidade_Vendida_KG FROM sales s INNER JOIN products p ON s.ID_PRODUTO = p.ID_PRODUTO GROUP BY p.NOME_PRODUTO ORDER BY Quantidade_Vendida_KG DESC LIMIT 1").fetchone()

    def best_banana_selling_day(self):
        return self.con.execute("SELECT STRFTIME('%d/%m/%Y', s.DATA), SUM(VALOR_VENDA) AS TOTAL_VENDA, COUNT(p.ID_PRODUTO) FROM sales s INNER JOIN products p ON s.ID_PRODUTO = p.ID_PRODUTO  WHERE p.NOME_PRODUTO = 'Banana' GROUP BY DATA ORDER BY TOTAL_VENDA DESC LIMIT 1").fetchone()

    def sales_by_time_range(self):
        return self.con.execute("CREATE VIEW IF NOT EXISTS sales_by_time_range AS SELECT FAIXA_HORARIO AS HORA, SUM(VALOR_VENDA) AS TOTAL FROM sales GROUP BY HORA ORDER BY HORA").fetchall()
    

if __name__ == '__main__':
    data_path = 'data/Cópia de Teste visualização de dados.xlsx'
    market_data = MarketData(data_path) 
    market_data.load_sales()
    market_data.load_products()
    market_data.best_selling_day()
    market_data.daily_sales()
    market_data.monthly_sales()
    market_data.sales_per_product()
    market_data.best_selling_product_in_kg()
    market_data.best_banana_selling_day()
    market_data.sales_by_time_range()