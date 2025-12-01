

The pipeline is structured into five continuous stages: **Ingestion, Discovery, Generation, Validation, and Adaptation.** 



### 1. Ingestion & Pre-Processing

This stage connects to the raw data stream and prepares it for analysis.

* **Data Stream Connector:** Ingests high-volume, real-time data feeds (e.g., Kafka, CDC streams).
* **Initial Schema Check:** Performs a quick, basic check to ensure the incoming data conforms to the expected structure (e.g., JSON is valid, required columns exist).
* **Data Preparation:** Cleanses common noise, handles basic type conversions, and prepares the data into a structure suitable for the **Profiling Agent** (e.g., a Pandas DataFrame or Spark RDD).

---

### 2. Discovery & Profiling

The **Profiling Agent** analyzes the data to understand its shape and detect deviations. This stage uses ML algorithms.

* **Profiling Agent (ML-Based):**
    * **Statistical Analysis:** Computes detailed statistics (mean, standard deviation, cardinality, missingness percentage) for all relevant columns.
    * **Drift Detection:** Compares the **current statistical profile** against a historical **Baseline Profile**. It flags **data drift** (significant changes in distribution, e.g., average transaction amount suddenly increases).
    * **Anomaly Detection:** Uses ML algorithms (like **Isolation Forest** or **One-Class SVM**) to identify individual records that are statistical outliers, even if they don't violate existing rules.
* **Output:** Generates a **Profiling Report** and a list of detected **Anomalies/Drift Events**.

---

### 3. Rule Generation (The AI Core)

The **Rule Generation Agent (MCP Agent)** uses the LLM to translate insights from the Profiling Report into executable validation rules.

* **Input Context:** Receives the **Profiling Report** (from Stage 2), **Business Requirements** (e.g., "KYC data must be complete"), and the current set of **Active Rules**.
* **LLM Rule Generation:** The LLM acts as an expert Data Quality Engineer, reasoning as follows:
    * *If Drift is detected:* "The average `Monthly Income` is higher, the rule range needs to be expanded." $\rightarrow$ **Generates a refined range rule.**
    * *If Missingness is high for a critical field:* "The `SSN` field is now 5% missing, violating the AML policy." $\rightarrow$ **Generates a stricter non-null rule.**
* **Output:** A set of **Proposed New or Refined Validation Rules** (e.g., in `Great Expectations` format) ready for deployment or human review.

---

### 4. Validation & Quarantine

The **Validation Agent** applies the active, dynamic rules to the incoming data stream.

* **Rule Application:** Applies both the **static, approved business rules** and the **newly generated dynamic rules** to the data stream.
* **Validation:** Tags each record as **PASS** or **FAIL**.
* **Output Separation:**
    * **Clean Data:** Records that PASS are routed to the final destination.
    * **Quarantined Data:** Records that FAIL are routed to a secure quarantine zone for further analysis and remediation (managed by the UI).

---

### 5. Adaptation & Refinement (The Feedback Loop)

This is the continuous learning stage, crucial for self-correction.

* **Refinement Agent (LLM-Based):** Analyzes the results of Stage 4.
    * **False Positive Analysis:** If a high volume of records failed a new rule but were considered **valid** by the **Profiling Agent** (or human feedback), the LLM is prompted to adjust the rule's parameters (e.g., relax a strict tolerance).
    * **Performance Tracking:** Monitors the pass/fail rate of each rule.
* **Rule Set Update:** The Refinement Agent either updates the prompt/parameters for the **Rule Generation Agent** or proposes a modification to the active rule set, closing the loop and making the system truly adaptive.