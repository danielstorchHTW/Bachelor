from prompt_generator import generate_prompt
from llama_api import query_llama
from get_db_schema import er_diagram_with_keys, dataframe_to_plantuml
from dotenv import load_dotenv
def main():

    load_dotenv()
     # 1. Text to SQL
     # z.B. Anzahl aller Produkte
    query = input("Bitte gib deine natürliche Sprachabfrage ein: ")
         
    # 2. Schema ziehen
    df_columns, df_pk, df_fk = er_diagram_with_keys("ugm")
    plantuml_output = dataframe_to_plantuml(df_columns, df_pk, df_fk)

    # 3. Prompt generieren
    prompt = generate_prompt(query, plantuml_output)
    print("\nGenerierter Prompt:")
    print(prompt)

    # 4. SQL mit Llama3 generieren
    try:
        sql_output = query_llama(prompt)
        print("\nGenerierte SQL-Anweisung:")
        print(sql_output)
    except Exception as e:
        print(f"Fehler bei der SQL-Generierung: {str(e)}")

if __name__ == "__main__":
    main()