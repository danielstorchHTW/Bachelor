Dieses Projekt generiert SQL-Abfragen aus natürlicher Sprache unter Verwendung eines Datenbankschemas. 
Das Schema wird aus einer PostgreSQL-Datenbank extrahiert und in PlantUML-Notation visualisiert, bevor es in den Prompt eines Sprachmodells eingebunden wird. Das Modell (Llama3-2B) erzeugt dann die SQL-Abfrage.

Für die Ausführung .env Erstellen mit:
- LLAMA_API_USERNAME
- LLAMA_API_PASSWORD
- pg_userid
- pg_password 
- pg_host = 'icla1lxc.f4.htw-berlin.de'
- pg_db = 'adbkt'


Funktionen:

 Extraktion des Datenbankschemas:

       - Extrahiert Tabellen, Spalten, Primär-  und Fremdschlüssel aus einer PostgreSQL-Datenbank.

       - Stellt die Informationen in einer lesbaren Struktur bereit (PlantUML).

 Text-to-SQL Generierung:

        - Nimmt eine natürlichsprachliche Abfrage (z. B. "Anzahl aller Produkte") entgegen.

        - Integriert das Datenbankschem in den Prompt.
        - Generiert eine SQL-Abfrage mithilfe des Sprachmodells Llama3-2B.
