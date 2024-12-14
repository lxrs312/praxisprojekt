# Vergleich von Optical-Character-Recognition-Services

Dieses Repository wurde im Rahmen meines Praxisprojekts im siebtem Semester erstellt und beschäftigt sich mit dem Vergleich verschiedener Optical-Character-Recognition (OCR)-Services. Der Schwerpunkt liegt auf der handschriftlichen Texterkennung in Dokumenten.

## Projektübersicht

**Titel:** Vergleich von Optical-Character-Recognition-Services unter dem Aspekt der handschriftlichen Texterkennung in Dokumenten

Im Rahmen dieses Projekts wurden fünf verschiedene OCR-Tools getestet. Dazu wurden spezielle Dokumente entwickelt, die sowohl maschinell als auch handschriftlich ausgefüllten Text enthalten. Die Auswertung basiert auf der Genauigkeit und Performance der OCR-Tools bei der Erkennung.

## Vorgehensweise

1. **Erstellung der Testdaten:**
   - 10 verschiedene Dokumentvorlagen wurden entworfen.
   - Von jeder Vorlage wurden 10 Exemplare gedruckt und von verschiedenen Personen handschriftlich ausgefüllt.
   - Jedes Exemplar enthält unterschiedliche Texte.
   - Alle Daten wurden in der Datei `input_data.json` gespeichert, um eine automatisierte Auswertung zu ermöglichen.

2. **Implementierung der OCR-Tools:**
   - Für jedes Tool wurde die Implementierung mithilfe des jeweiligen SDKs vorgenommen.

3. **Entwicklung zusätzlicher Klassen:**
   - **`timehandler`:** Startet und stoppt die Zeitnahme zur Messung der Verarbeitungszeit.
   - **`filehandler`:** Verantwortlich für das Speichern und Verwalten der Daten.
   - **`normalizer`:** Normalisiert den von den OCR-Tools erkannten Text sowie die Referenzdaten.
   - **`evaluator`:** Führt die automatische Auswertung durch und vergleicht erkannte Daten mit den Referenzdaten.
   - **`result`:** Speichert alle Metriken zur Genauigkeitsmessung.

4. **Visualisierung:**
   - Die Metriken wurden visualisiert, um Abhängigkeiten von Tool, Schriftfarbe und Autor zu analysieren.
   - Diverse Diagramme wurden erstellt, um die Ergebnisse anschaulich darzustellen.

## Speicherung der Daten

### data
Innerhalb des data-directories sind alle im Rahmen des Praxisprojekts entstandenen Daten gespeichert. Innerhalb der Unterordner der einzelnen Services findet man in **`raw_data`** für jedes Exemplar von jedem Dokument die exakte Ausgabe des Tools. **`processedData.json`** speichert die zusammengefassten Antworten aller Exemplare.

**`evaluatedData.json`** speichert die errechneten Metriken aus **`processedData.json`**.

**`summarizedData.json`** fasst **`evaluatedData.json`** zusammen und ergänzt diese um Metriken über Autor und Schriftfarbe.

### images
Im images-Ordner sind alle im Rahmen des Praxisprojekts entstandenen Diagramme gespeichert. Diese beziehen sich auf die Metriken von **`summarizedData.json`** 

### scans
Im scans-Ordner befindet sich eine .zip, welche alle befüllten und eingescannten Dokumente beinhaltet.

## Technologien

- Python
- SDKs der getesteten OCR-Tools
- Matplotlib für Visualisierungen
- JSON für die Speicherung der Testdaten

## Setup

Folgende Ressourcen wurden für das Setup der einzelnen Services genutzt:

https://azure.microsoft.com/en-us/products/aiservices/ai-document-intelligence

https://aws.amazon.com/de/textract/

https://cloud.google.com/document-ai/

https://github.com/tesseract-ocr/tesseract

## Kontakt

Bei Fragen oder Anmerkungen stehe ich gerne zur Verfügung.

