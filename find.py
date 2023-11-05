import csv

# Pfad zur CSV-Datei
csv_file_path = './data/EURUSD.csv'

# Liste für Zeilen mit Nicht-Float-Werten
nicht_float_zeilen = []

# CSV-Datei öffnen und durchgehen
with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)  # Kopfzeile überspringen
    for row_index, row in enumerate(csv_reader, start=2):  # Start bei 2 wegen der Kopfzeile
        if len(nicht_float_zeilen) >= 10:
            # Wenn wir schon 10 Ergebnisse haben, brechen wir die Schleife ab
            break
        try:
            # Versuchen Sie, den Wert in Spalte 5 (Index 4) als Float zu konvertieren.
            float(row[4])
        except ValueError:
            # Wenn ein ValueError auftritt, ist der Wert kein gültiger Float.
            nicht_float_zeilen.append((row_index, row))
        except IndexError:
            # Falls die Zeile weniger als 5 Spalten hat.
            print(f"Fehler: Zeile {row_index} hat weniger als 5 Spalten: {row}")

# Ergebnis ausgeben
if nicht_float_zeilen:
    print("Die ersten 10 Zeilen mit Nicht-Float-Werten in Spalte 5 gefunden:")
    for index, zeile in nicht_float_zeilen:
        print(f"Zeile {index}: {zeile}")
else:
    print("Weniger als 10 Nicht-Float-Werte gefunden, oder alle Werte in Spalte 5 sind Floats.")
