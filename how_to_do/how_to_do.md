<h4> How to do:</h4>

----------------------------------



Depois de projetar, implementar e popular a tabela relacional, projetamos o novo esquema da tabela dimensional de acordo com a convenção de nomenclatura.

:heavy_check_mark:     Tabela `produto` do sistema OLTP

<table style="border: 1px solid black; border-collapse: collapse;">
  <tr>
    <th style="border: 1px solid black; padding: 5px;">Tabela de Origem (OLTP)</th>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">idproduto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">nome_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">descricao</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">tipo_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">valor_minimo</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">valor_maximo</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">numero_parcelas_maximo</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">condicoes_especiais</td>
  </tr>
</table>



:heavy_check_mark:   Tabela `dimproduto` do sistema OLAP

<table style="border: 1px solid black; border-collapse: collapse;">
  <tr>
    <th style="border: 1px solid black; padding: 5px;">Tabela de Destino sem a Nomenclatura  (OLAP)</th>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">DimProduto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">sk_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">idproduto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">nome_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">tipo_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">valor_minimo</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">valor_maximo</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">numero_parcelas_maximo</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px;">condicoes_especiais</td>
  </tr>
</table>



:heavy_check_mark:   Novo design da Tabela `dimproduto`

<table style="border: 1px solid black; border-collapse: collapse;">
  <tr>
    <th style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">Tabela de Destino com a nova Nomenclatura (OLAP)</th>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">dimproduto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">sk_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">codigo_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">nome_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">descricao_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">categoria_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">valor_minimo_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">valor_maximo_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">max_parcelas_produto</td>
  </tr>
  <tr>
    <td style="border: 1px solid black; padding: 5px; background-color: #d3d3d3;">condicoes_especiais_produto</td>
  </tr>
</table>



:heavy_check_mark:   ETL:



:small_orange_diamond: **EXTRAÇÃO:**

---------------------------

Nessa etapa realizamos a conexão com o banco de dados previamente definidos no Airflow.

Banco de dados`oltp_db` Usamos `SQL` pra selecionar a tabela da qual vamos extrair os dados :`produto`. Salvamos os dado em `df_produto` e enviamos para  `xcom_push`. A **chave** é df_produto e o **valor** são todos os dados de df_produto.

```                                                          
def extract_data(**kwargs):

  olap_hook = PostgresHook(postgres_conn_id='oltp_db')
  sql = 'SELECT * FROM produto;'
  df_produto = olap_hook.get_pandas_df(sql)


  if df_produto.empty:
    raise ValueError("Nenhum dado foi extraído da tabela produto.")

kwargs['ti'].xcom_push(key='df_produto', value=df_produto)


```



:small_orange_diamond: **TRANSFORMAÇÃO:**

-------------------------

A etapa de transformação é a minha favorita, pois é onde escrevemos as alterações que queremos. Recuperamos os dados de `df_produto` com `xcom_pull`. Mapeamos os campos de origem e apontamos pros campos  de destino. Usamos uma função do pandas para renomear as colunas de destino: `df_produto.rename(columns={...})`

```                                                   
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

```



:white_check_mark: Na etapa de transformação nos limpamos os dados, enriquecemos, modificamos pra que eles atendam a requisitos de análise ou armazenamento. Nessa etapa também convertemos os tipos de dados, renomeamos colunas, aplicamos regras de negócio, etc.

:ballot_box_with_check: Consideramos que a tabela de destino **dimproduto** já exista no sistema OLAP e já possua dados inseridos. Então vamos pegar os dados transformados (da etapa de transformação) e combinar eles com os dados existentes no banco de dados. Assim vamos identificar quais registros são novos e quais já existem ou precisam ser atualizados.

É importante entender essa lógica para passar pra etapa de carregamento.



:small_orange_diamond: **CARREGAMENTO:**

------------------------------------------------

Abrimos a conexão com o banco de dados `engine.connect()` dentro do bloco `whith` ...`as`.

Selecionamos as colunas `codigo_produto` e `sk_produto` usando SQL. Salvamos na variável `existing_sk_produto`. 

Realizamos o merge entre os dados transformados `df_produto` e os dados que já existe `exiting_sk_produto` na tabela para inserir ou atualizar.

Na pratica comparamos o s dados de `df_produto` e `existing_sk_produto` onde:

`df_produto`: É o DataFrame com os dados transformados na etapa anterior.

`existing_sk_produto`: DataFrame com os dados que existem da tabela `dimproduto`.

`merge_df`: Junção  (`merge`) o DataFrame `df_produto` com o DataFrame `existing_sk_produto` com base na coluna `codigo_produto`.

`````` 
with engine.connect() as conn:
        existing_sk_produto = pd.read_sql('SELECT codigo_produto, sk_produto FROM dimproduto', conn)
        merged_df = pd.merge(df_produto, existing_sk_produto, on='codigo_produto', how='left')
       
``````



Usamos uma ferramenta do pandas pra trabalhar com dados faltantes `isna()` na coluna `sk_produto` . 

`.isna()`identifica quais itens de `sk_produto` é NaN, **se o valor de `sk_produto` é NaN**, isso indica que o produto correspondente **não está presente na tabela `dimproduto` **e, portanto, deve ser inserido na tabela `dimproduto` no Data Warehouse.



Se o dataframe `to_insert` não estiver vazio, selecionamos as colunas encessárias pra ser incluídas na tabela antes da inserção.

 Usando o método `to_sql` do pandas inserimos os dados do DataFrame `to_insert` na tabela `dimproduto` do banco de dados. (nome da tabela, conexão, adiciona).



``````
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
        
``````



Agora vamos atualizar as colunas e inserir os dados!

Filtramos o DataFrame para manter apenas as linhas onde `sk_produto` não é NaN. Ou seja, onde estas linhas já têm uma correspondência existente na tabela `dimproduto` e precisam ser atualizadas.

``````
to_update = merged_df[~merged_df['sk_produto'].isna()]
``````

O operador  `~` inverte valores booleanos. Então onde `~merged_df['sk_produto'].isna()` se torna True para os valores que **não são** NaN.

Se**`to_update.empty`** verifica se o DataFrame `to_update` está vazio, entõ o **`not to_update.empty`**  inverte o resultado. Então, `if not to_update.empty` é True se o DataFrame `to_update` contiver pelo menos uma linha.

Em **`for index, row in to_update.iterrows()`**: criamos um loop que percorre cada linha do DataFrame `to_update`.

```
         to_update = merged_df[~merged_df['sk_produto'].isna()]
        if not to_update.empty:
            for index, row in to_update.iterrows():
                update_sql = '''
                UPDATE dimproduto
                SET nome_produto = %s,
                descricao_produto = %s,
                categoria_produto = %s, 
                valor_minimo_produto = %s,
                valor_maximo_produto = %s, 
                max_parcelas_produto = %s,
                condicoes_especiais_produto = %s
                WHERE sk_produto = %s
                '''
                conn.execute(update_sql,
                row['nome_produto'],
                row['descricao_produto'],
                row['categoria_produto'], 
                row['valor_minimo_produto'],
                row['valor_maximo_produto'], 
                row['max_parcelas_produto'],
                row['condicoes_especiais_produto'],
                row['sk_produto'])
    
    print("Dados carregados com sucesso!")

```

 Na primeira parte, atualizamos os campos e modificamos os registros existentes na tabela dimproduto.

Na segunda  parte apontamos o valores que devem ser inseridos no lugar dos placeholders (%) linha por linha.

Na prática, juntamos (mesclamos) os novos dados do produto com os dados existentes na tabela `dimproduto` e identificamos quais registros precisavam ser inseridos ou atualizados. E finalmente, inserimos novos registros que não existiam ainda na tabela e atualizamos os registros existentes com base nos dados mesclados.

Definimos as tarefas

``````
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
``````



Definimos a precedencia das tasks:

``````
extract_task >> transform_task >> load_task
``````



A nova tabela dimensional dimproduto teve seus campos reescritos e os dados inseridos.

![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXctBDhwGcWy24czdR-p6epQPH0IEd4S_HLSwZ7oicvRTjQKYTbOZMpSDB5tNIdoDNkLwqBCoEySXg8kI5Kprb9UAxPX9_PsAc3S-7-GoM9YvJ2rQYZZv7jh-i2r4B88mr72MD1ZDsedAyFr9tqW4xGn5_Dt?key=mcTeGO_pylJdcN1ITL-rTQ)

Tivemos uma série de erros antes do pipeline funcionar...

![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfJMooIfyxL3ZcaF3sZINnieXW6Hh0S--PoiOIaopKV5fIxdk80lRx0R-NlbowPzCGRMqOyKi17-VDaqhIqhKYlM9KNQId0qiQPZeA1ATHQ0Vr8ETbSrS60cq0Yil6sgV3Gf_4xMh-FAdUy7WTLLfvr827o?key=mcTeGO_pylJdcN1ITL-rTQ)

![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXea6yuR8stTHIyc2lJv06ICnXugX6UcqCANGB91wYe2ZbfxPvlXNvYJVvtgYD_PJpFwbc3LGb_7yqVr5kyUWN8m_vFnUUel9pRx7-8UMqsvIHVSd44St3US0w78vN1dDtrLAbhNJScNBu6kOUq0MGUKk6M?key=mcTeGO_pylJdcN1ITL-rTQ)

E todos eles estavam relacionados aos nomes dos campos escritos de forma inadequada ou a atribuição correta dos dados em variável.



Mas no final deu certo!



![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcIL9H1MGkjV9Qv4eBZhaJ9gEvBjR27HMBRrxV67IZIC31AzKaJI4Owp7PndLfXF2_OG_0CC3r7uhaXmDQUXu-Gyzs0D6wQJw1DpEKuoYauLTcXAAcvbBDVdzXpJoRDyGVpJRQkw-Wcd85gHMEV9Tz8ZZn4?key=mcTeGO_pylJdcN1ITL-rTQ) 



:pushpin:[DAG para esse ETL aqui](DAG).

:pushpin: [SQL das tabelas aqui](SQL).















