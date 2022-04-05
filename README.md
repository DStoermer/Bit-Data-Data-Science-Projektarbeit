# Bit-Data-Data-Science-Projektarbeit
Mein Hauptanteil in der Gruppenprojektarbeit "Predicting Player Numbers with Regard to historical Data and Game Attributes"

Das Ziel dieser Projektarbeit war es die Spielerzahlen von einzelnen Spielen des Weltgrößten Spielevertreiber Steam zu predicten.

Die Daten wurden von einem third party Tool auf https://steamdb.info/ gefetcht, dann in die SQLite3 Datenbank "game_data.db" eingefügt und schließlich durch das von mir geschrieben Skript "db-to-csv.py" in das von uns gewünschte Format gebracht.

Das Skript baut eine CSV Datei auf Basis der UNIX-Timestamps, indem es je nach Timestamp queried.
Dieser Workaround war nötig, da SQLite3 Probleme bei einer gesamtem Query hatte.
Dazu mussten einige Exceptions per IFNULL eingebaut werden um Datenqualitätsfehler der Datenbank vorzubeugen.

Das Skript db-to-csv.py kann mit der Datenbank game_data.db zusammen die CSV Datei erstellen.
Verwendete Libraries sind:
- sqlite3 (Part des Python Standardpakets)
- tqdm (Library um den Fortschritt per Ladebalken zu visualisieren)
