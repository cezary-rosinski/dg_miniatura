# README: Analytical Tools for the MINIATURA 8 Research Project
## Repository: cezary-rosinski/dg_miniatura

The code contained in this repository (**cezary-rosinski/dg_miniatura**) was **developed as part of the implementation of the MINIATURA 8 research activity** [1], financed by the National Science Centre (NCN) [2, 3]. This project aimed to conduct preliminary and pilot studies in literary research using digital humanities tools [4, 5].

The source code in this repository is **100.0% written in Python** [6] and was used for automated data processing, text mining, classification, and the creation of a graph knowledge base [7, 8].

---

## 1. Project Context and Details

### 1.1 Project Identification
| Category | Value | Source |
| :--- | :--- | :--- |
| **Title (English)** | **Right-wing violence after 1989 in German prose: generationality versus intersectionality** | [1, 3, 9] |
| **NCN Registration No.** | 2024/08/X/HS2/00396 | [1-3, 10] |
| **Start/End Date** | 2024-08-08 to 2025-08-07 | [1] |
| **Implementing Institution** | Adam Mickiewicz University in Poznań (UAM) | [1] |
| **Project PI** | Dr. Dominika Anna Gortych (UAM) | [4, 9, 11, 12] |
| **Data Curator/Programmer** | **Dr. Cezary Rosiński** (IBL PAN documentalist and data specialist, Python programmer) | [2, 9, 12, 13] |

### 1.2 Scientific Goal and Methodology
The primary goal was to verify the hypothesis concerning the dominance of prose texts representing right-wing motivated violence as a specific **generational experience of East German youth after 1989** (the so-called "Baseballschlägerjahre") [4, 14-16]. The project also hypothesized that literature disproportionately focused on perpetrators, marginalizing the perspective of victims in an **intersectional approach** [14-16].

To achieve this, the project planned to **build a digital, open-access database** compliant with FAIR principles, containing information about prose texts published after 1989 and dedicated to right-wing violence [17, 18].

### 1.3 Role of the Code in Research Implementation
The Python code was crucial in the second and third stages of the project:

*   **Data Harvesting:** An external service contract with Dr. Cezary Rosiński involved the **automatic searching of resources** from the `perlentaucher.de` service based on a catalog of 125 keywords [13]. This resulted in an initial list of five thousand texts [19].
*   **Classification:** The **executor, with AI support, developed Python code** aimed at labeling further texts corresponding to the project's assumptions [20]. This rigorous verification and classification process refined the corpus to **113 final positions** [7, 20-22].
*   **Graph Database Construction:** The third stage involved using digital humanities technologies—including Linked Open Data modeling, *text mining*, network analysis with **NetworkX**, and **Natural Language Processing (NLP)**—to build a graph database [7, 8, 23].
*   **Final Data Structure:** The database contains 113 records, described using **18 standard metadata fields** [21, 24, 25]. Metadata included bibliographic information, genre classification, narrative perspectives (generationality, intersectionality, other), types of violence, and ideological contexts (e.g., neo-Nazism, racism, sexism) [8, 12, 25, 26]. The data was designed to enable complex queries in the Cypher language [7].

---

## 2. Repository Contents Analysis

The `cezary-rosinski/dg_miniatura` repository contains metadata and Python scripts [27] reflecting the analytical and conversion stages described in the final report:

| File Name | Language | Function in the Project (Based on Report Context) | Source(s) |
| :--- | :--- | :--- | :--- |
| `dg_miniatura_data_harvesting.py` | Python | Script used for the **automatic collection of preliminary data** (e.g., from `perlentaucher.de`) based on keywords [13, 27]. | [13, 27] |
| `dg_miniatura_data_klasyfikator.py` | Python | **Classification code developed with AI support** [20] used to filter the initial list down to the final corpus of 113 texts [20, 27]. | [20, 27] |
| `dg_miniatura_NLP.py` | Python | Contains Natural Language Processing tools used for preliminary processing of text data [8, 27]. | [8, 27] |
| `dg_miniatura_analysis.py` | Python | Script used for data analysis, including likely network analysis (NetworkX) [8, 27]. | [8, 27] |
| `dg_miniatura_graph_database.py` | Python | Responsible for converting and modeling metadata into the **RDF graph database structure** [7, 27]. | [7, 27] |
| `dg_miniatura_final_dataset.py` | Python | Script likely used for the standardization and normalization of metadata, including supplementing personal names and geographical data with **Wikidata URIs** [24, 26-28]. | [24, 26-28] |
| `rechtsextremismus.ttl` | TTL | The **final graph database file** in Terse RDF Triple Language, containing the 113 prose texts metadata [7, 18, 21, 27]. | [7, 18, 21, 27] |
| `dg_miniatura_wiso.py` | Python | Auxiliary script component [27]. | [27] |
| `.gitignore` | Config | Configuration file [27]. | [27] |

---

## 3. Data Access and Licensing

The final dataset generated by the research activity has been made available in open access, adhering to FAIR principles (Findable, Accessible, Interoperable, Reusable) [17, 18, 29].

*   **Persistent Identifier (DOI):** The dataset is identified by **10.5281/zenodo.15656024** [9, 30].
*   **Main Repository:** The digital database is publicly available in the **Zenodo** repository [2, 3, 23, 30, 31].
*   **Backup:** A copy of the database was also deposited in the AmuRed research data repository [30, 31].
*   **Data Format:** Graph database in **Terse RDF Triple Language (TTL)** [18, 29].
*   **Licensing:** The dataset is published under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license [18, 29, 30]. Data are freely available for scholarly reuse with attribution [18, 29].
*   **Documentation:** Documentation to enable data exploration (e.g., using Neo4j software and the Cypher query language) is available in this GitHub repository [23, 32].
