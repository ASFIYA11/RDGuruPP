# RDguru++ --- A Conversational Intelligent Agent for Rare Diseases

RDguru++ is an academic project concept for a conversational assistant
intended to support rare-disease exploration by combining phenotype
information, information retrieval, and large-language-model responses.
The project presentation describes a workflow that uses Human Phenotype
Ontology (HPO) terms, phenotype matching, PheLR, a Groq-hosted LLM, and
a Double Deep Q-Network (DDQN) for multi-source diagnostic fusion.

> **Medical safety notice:** RDguru++ is an academic decision-support
> prototype, not a medical device or a substitute for a qualified
> clinician. It must not be used to diagnose, treat, or rule out a
> disease. AI-generated information may be incomplete or incorrect.
> Clinical decisions must be made by qualified healthcare professionals
> using validated evidence.

## Project Motivation

Rare diseases can be difficult to identify because symptoms may overlap
across conditions and relevant information can be distributed across
medical knowledge sources. The project aims to provide a conversational
interface through which users can describe phenotypic findings and
receive structured, information-supported responses for further review.

The presentation identifies limitations in the existing approach,
including latency from LLM processing, instability associated with DQN
value overestimation, and limited transparency of diagnostic reasoning.
RDguru++ proposes using a Groq LLM, adaptive knowledge retrieval, and
DDQN-based fusion to address these design goals. These are project
objectives; measurable improvements should only be claimed after
controlled evaluation.

## Proposed Workflow

``` text
User's symptom / phenotype description
                 |
                 v
        Data preparation
  Clean and structure clinical text
                 |
                 v
      HPO term extraction / mapping
                 |
                 v
       Multi-source analysis
  +----------------+------------------+
  |                |                  |
  v                v                  v
Phenotype       Retrieved case     LLM-based
matching        information        reasoning
  |                |                  |
  +----------------+------------------+
                 |
                 v
       DDQN-based fusion
   (as described in the proposal)
                 |
                 v
 Structured conversational response
 with supporting information and caveats
```

The exact implementation and behavior depend on the code and
configuration used in a given version. The workflow above reflects the
architecture described in the project presentation, not a claim of
clinically validated performance.

## Main Features Described in the Project

-   Conversational interface for rare-disease-related queries
-   Processing of phenotype descriptions and mapping to HPO terms
-   Similarity-based retrieval of relevant case text using embeddings
    and FAISS
-   Integration of Groq LLM responses
-   Proposed multi-source diagnostic fusion using DDQN
-   Conversation context and structured responses
-   Intended emphasis on explainability and response efficiency

## Technology Stack

The project presentation lists the following technologies:

-   **Python** --- core programming language
-   **PyTorch** --- neural-network implementation and proposed DDQN
    training
-   **Groq API / Groq LLM** --- language-model inference
-   **LangChain** --- LLM integration and conversation-related
    components
-   **FAISS** --- vector similarity search
-   **Sentence Transformers** --- text embedding generation
-   **Pandas and NumPy** --- data handling and numerical operations
-   **scikit-learn** --- preprocessing and dimensionality-reduction
    utilities
-   **Pronto** --- ontology loading and access
-   **SQLite** --- local relational data storage
-   **Chainlit** --- conversational application interface
-   **Transformers** --- model-related utilities

Check the actual repository's dependency file and source code before
assuming that every listed package is required by the current
implementation.

## Architecture and Modules

### 1. Data Preparation Module

The presentation describes collecting relevant datasets and medical
sources, cleaning inconsistent data, and converting clinical
descriptions into structured phenotype representations such as HPO
terms. Prepared data is stored for later retrieval and analysis.

### 2. DDQN Model Training Module

The proposal describes encoding patient information into state vectors
and combining outputs from phenotype matching, PheLR, and LLM reasoning.
It describes online and target networks, experience replay, reward-based
learning, RMSProp, and mean squared error loss.

A DDQN component should only be described as trained or operational if
the implementation includes the relevant training logic, reward design,
saved model, and evaluation evidence. The presentation alone does not
establish validated diagnostic performance.

### 3. Chatbot Interface Module

The presentation describes a conversational interface that accepts
rare-disease-related questions, integrates the LLM and proposed DDQN
model, retrieves relevant information, and displays structured responses
while maintaining conversation context.

## Retrieval with Embeddings and FAISS

The sample code in the presentation loads case text from SQLite,
generates embeddings using `SentenceTransformer("all-MiniLM-L6-v2")`,
normalizes the vectors, and creates a FAISS `IndexFlatIP` index. The
retrieval function embeds a query and searches for similar case-text
vectors.

At a high level:

1.  Load case text from the database.
2.  Convert the text into numerical embeddings.
3.  Normalize embeddings.
4.  Add the embeddings to a FAISS index.
5.  Embed a query and retrieve the nearest indexed cases.
6.  Use retrieved material as context for subsequent analysis.

Similarity-based retrieval finds text that is close in embedding space;
it does not by itself establish that a disease is present or that a
retrieved case is clinically equivalent.

## Setup

The presentation identifies Windows, Python, and VS Code as the
development environment. It lists SQLite as the database and the
libraries noted above.

The exact installation and run commands depend on the repository files.
Once the source repository is available, document the verified commands
from its actual dependency and application configuration files.

A typical Python environment setup is:

``` bash
python -m venv .venv
```

**Windows PowerShell:**

``` powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

``` bat
.venv\Scripts\activate.bat
```

**macOS / Linux:**

``` bash
source .venv/bin/activate
```

If the repository contains a `requirements.txt`, install its pinned
dependencies with:

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Do not run the application until required model files, ontology files,
database files, and API settings have been configured according to the
source code.

## Configuration and Secrets

The application may require a Groq API key and paths to local data,
model, database, or ontology files. Verify the exact configuration names
in the implementation.

-   Keep API keys and credentials out of source code.
-   Store secrets in environment variables or an appropriate secret
    manager.
-   Do not commit populated `.env` files, private datasets, or sensitive
    health information.
-   Use only data that you are authorized to access and process.
-   Avoid logging identifiable health information.

A `.env.example` file may document variable names with placeholder
values, but it should never contain real credentials.

## Evaluation

No diagnostic accuracy, sensitivity, specificity, latency, or clinical
validation result is asserted in this README because such results cannot
be established from the project presentation alone.

Recommended evaluation areas include:

-   **Phenotype extraction:** precision, recall, and F1 against a
    reviewed reference set
-   **Retrieval quality:** recall@k, precision@k, or expert relevance
    assessment
-   **Disease-ranking quality:** top-k accuracy or ranking metrics on a
    carefully defined, held-out dataset
-   **LLM responses:** factual support, completeness, consistency, and
    expert review
-   **System performance:** latency, failure rate, and resource use
    under defined test conditions
-   **Safety:** unsupported claims, inappropriate certainty, missing
    caveats, and handling of insufficient information

Evaluation datasets must be separated appropriately to avoid leakage.
Results should be reported with the dataset, sample size, methodology,
baseline, and limitations. A prototype's evaluation results must not be
presented as evidence of clinical effectiveness.

## Limitations and Responsible Use

-   LLM responses can contain incorrect or unsupported statements.
-   Similar symptoms can occur in different diseases, and phenotype
    similarity is not a definitive diagnosis.
-   The quality of retrieval depends on the coverage, quality, and
    freshness of the underlying data.
-   The proposed DDQN fusion approach requires implementation-level
    verification and empirical evaluation.
-   A research prototype does not establish clinical validity, safety,
    or regulatory approval.

RDguru++ should be presented as an educational/research prototype for
exploring conversational rare-disease information, not as a replacement
for professional medical assessment.

## Future Improvements

Potential improvements, subject to the actual implementation, include:

-   Reproducible setup instructions and pinned dependencies
-   Automated tests for data preparation, retrieval, and API/model
    integration
-   Versioned datasets and documented data provenance
-   Evaluation against a held-out, expert-reviewed benchmark
-   Source references for retrieved evidence and clearer uncertainty
    reporting
-   Monitoring of latency, failures, and retrieval quality
-   Stronger privacy controls and safe handling of sensitive data
-   A documented baseline comparison before claiming performance
    improvements

## Project Summary

RDguru++ proposes a conversational rare-disease information assistant
that combines phenotype processing, similarity-based retrieval, LLM
reasoning, and a DDQN-based fusion approach. The project presentation
describes a Python-based stack involving PyTorch, Groq, LangChain,
Sentence Transformers, FAISS, SQLite, and Chainlit.

The project's central engineering challenge is to integrate these
components while ensuring that outputs are traceable, evaluated,
privacy-conscious, and appropriately cautious for a medical-information
setting.


