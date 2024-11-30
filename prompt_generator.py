#Prompt erstellen
def generate_prompt(query, relevant_schema):
    prompt = f"""
    Gegeben sei das folgende relevante Datenbankschema:
    {relevant_schema}

    Schreibe eine SQL-Anweisung für die folgende Anfrage:
    {query}
    """
    return prompt