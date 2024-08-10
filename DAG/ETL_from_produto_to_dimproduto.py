from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 5),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ETL_produto_dimproduto',
    default_args=default_args,
    description='ETL to load produto data into dimproduto',
    schedule_interval=None,  
)

def extract_data(**kwargs):
    olap_hook = PostgresHook(postgres_conn_id='oltp_db')
    sql = 'SELECT * FROM produto;'
    df_produto = olap_hook.get_pandas_df(sql)
    
    if df_produto.empty:
        raise ValueError("Nenhum dado foi extraído da tabela produto.")
    

    kwargs['ti'].xcom_push(key='df_produto', value=df_produto)

def transform_data(**kwargs):
    ti = kwargs['ti']
    df_produto = ti.xcom_pull(key='df_produto')
    
    if df_produto is None or df_produto.empty:
        raise ValueError("Nenhum dado foi extraído da tabela produto.")
    
   
    df_produto = df_produto.rename(columns={
        'idproduto': 'codigo_produto',
        'nome_produto': 'nome_produto',
        'descricao': 'descricao_produto',
        'tipo_produto': 'categoria_produto',
        'valor_minimo': 'valor_minimo_produto',
        'valor_maximo': 'valor_maximo_produto',
        'numero_parcelas_maximo': 'max_parcelas_produto',
        'condicoes_especiais': 'condicoes_especiais_produto'
    })
    
    
    if df_produto.empty:
        raise ValueError("Nenhum dado foi transformado.")
    
    ti.xcom_push(key='transformed_data_produto', value=df_produto)

def load_data(**kwargs):
    ti = kwargs['ti']
    df_produto = ti.xcom_pull(key='transformed_data_produto')
    
    if df_produto is None or df_produto.empty:
        raise ValueError("Nenhum dado foi extraído da etapa de transformação.")
    
    olap_hook = PostgresHook(postgres_conn_id='olap_dw')
    engine = olap_hook.get_sqlalchemy_engine()
    
    with engine.connect() as conn:
        existing_sk_produto = pd.read_sql('SELECT codigo_produto, sk_produto FROM dimproduto', conn)
        merged_df = pd.merge(df_produto, existing_sk_produto, on='codigo_produto', how='left')
        
        to_insert = merged_df[merged_df['sk_produto'].isna()]
        if not to_insert.empty:
            to_insert = to_insert[['codigo_produto',
                                    'nome_produto',
                                    'descricao_produto',
                                    'categoria_produto', 
                                   'valor_minimo_produto',
                                   'valor_maximo_produto',
                                   'max_parcelas_produto', 
                                   'condicoes_especiais_produto']]
            to_insert.to_sql('dimproduto', con=engine, if_exists='append', index=False)
        
        to_update = merged_df[~merged_df['sk_produto'].isna()]
        if not to_update.empty:
            for index, row in to_update.iterrows():
                update_sql = '''
                UPDATE dimproduto
                SET nome_produto = %s, descricao_produto = %s, categoria_produto = %s, 
                    valor_minimo_produto = %s, valor_maximo_produto = %s, 
                    max_parcelas_produto = %s, condicoes_especiais_produto = %s
                WHERE sk_produto = %s
                '''
                conn.execute(update_sql, row['nome_produto'], row['descricao_produto'], row['categoria_produto'], 
                             row['valor_minimo_produto'], row['valor_maximo_produto'], 
                             row['max_parcelas_produto'], row['condicoes_especiais_produto'], 
                             row['sk_produto'])
    
    print("Dados carregados com sucesso!")



extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

extract_task >> transform_task >> load_task
