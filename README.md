# LexiGrade

LexiGrade is an automatic CEFR-aligned text simplification system designed to generate graded readers using a controlled, reproducible NLP pipeline that combines linguistic analysis and large language models (LLMs).

The project is multilingual, currently supporting English and Spanish, and focuses on meaning preservation, explicit constraints, and local-first inference, making it suitable for research, education, and experimental use in computational linguistics and applied NLP.

---

## Features

- Automatic text simplification aligned to CEFR levels (A1–C2)
- Sentence-level simplification with explicit target control
- Meaning-preservation validation
- Detection of removed, added, or contradictory information
- Modular NLP evaluation pipeline
- Local LLM inference using Ollama
- Fully containerized and Kubernetes-ready (k3s)

---

## Conceptual Overview

LexiGrade implements a multi-stage pipeline designed to avoid uncontrolled paraphrasing and hallucination.

The system operates as follows:

1. Input text is segmented into manageable chunks
2. Each segment is simplified to a target CEFR level
3. The simplified output is evaluated for semantic fidelity
4. Only validated outputs are returned as final results

The primary objective is faithful simplification rather than stylistic rewriting.

---

## Architecture

LexiGrade is composed of four main components:

- Frontend: Web interface for user interaction
- Backend API: Orchestrates chunking, LLM calls, and validation
- Ollama: Local LLM inference engine
- Kubernetes (k3s): Orchestration and deployment environment

### Component Diagram

![LexiGrade Components](docs/architecture/lexigrade_components.drawio.svg)

### Interaction Flow

![LexiGrade Interaction Flow](docs/architecture/lexigrade-interaction-flow.drawio.svg)

---

## Deployment Overview

LexiGrade is designed to run locally on a Kubernetes cluster using k3s.

The repository intentionally avoids cloud-specific tooling. GPU configuration, drivers, and runtime setup are considered out of scope and must be handled by the user.

You can learn install k3s by following the instructions at https://docs.k3s.io/installation and learn integrating NVIDIA GPUs at https://github.com/UntouchedWagons/K3S-NVidia.

---

## Repository Structure

```
lexigrade/
├── client/
│   └── frontend/
├── docs/
│   └── architecture/
│       ├── lexigrade-interaction-flow.drawio.svg
│       └── lexigrade_components.drawio.svg
├── server/
│   ├── infra/
│   │   └── k8s/
│   │       ├── api/
│   │       ├── ollama/
│   │       ├── build-images.sh
│   │       ├── deploy.sh
│   │       └── namespace.yaml
│   ├── resources/
│   ├── src/
│   └── requirements.txt
└── README.md
```

---

## Prerequisites

- Linux environment
- Docker
- k3s
- kubectl
- Node.js and npm (required to build the frontend)
- Optional: NVIDIA GPU with appropriate drivers

You can follow without a GPU, but performance will be significantly reduced.

---

## Ollama Integration

LexiGrade uses a custom Ollama container image.

The image includes:
- Custom Ollama Modelfiles defining LexiGrade-specific models
- An initialization entrypoint responsible for creating the models at runtime

Model weights are not included in the image. Base models are downloaded automatically on first startup and cached locally.

---

## Build Images

To build and import the required images into the k3s runtime, run:

```./server/infra/k8s/build-images.sh```

Importing images into the k3s containerd runtime requires root privileges. You may be prompted for your sudo password.

---

## Deploy to k3s

To deploy LexiGrade to your local k3s cluster, run:

```./server/infra/k8s/deploy.sh```

Check the status of deployed resources:

```kubectl get pods -n lexigrade```

---

## Deploy Frontend

The frontend application is not deployed as a container and does not run inside Kubernetes.

To build and run the frontend locally:

1. Navigate to the frontend directory:

    ```cd ./client/frontend```

2. Install dependencies:

    ```npm install```

3. Start the development server::

    ```npm run dev```

The frontend will be available at the local address printed in the terminal.

    

---

## Model Initialization

On first startup:

- Ollama downloads the required base models  
- Custom LexiGrade models are created from the provided Modelfiles  

Model data is cached in the container volume mounted at `/root/.ollama`.

---

## Research Orientation

LexiGrade was designed with research and experimentation in mind.

Key design principles include:

- Explicit control over CEFR targets  
- Separation between generation and evaluation  
- Deterministic prompts and constrained outputs  
- Modular evaluation stages  

These characteristics make the system suitable for studies in text simplification, graded reader generation, and controlled LLM behavior.

---

## Citation

If you use LexiGrade in academic work, please cite:

LexiGrade: Automatic CEFR-Aligned Text Simplification Using Large Language Models

A BibTeX entry may be added in future releases.

---

## Notes

- This project prioritizes reproducibility and transparency over managed infrastructure  
- Cloud deployment and GPU orchestration are intentionally left to advanced users  
- The system can be extended with persistent volumes, Helm charts, or cloud runtimes if needed  

---

## Project Status

- Backend: Complete  
- Frontend: Integrated  
- Ollama integration: Stable  
- Kubernetes deployment: Local k3s  
- Documentation: Complete  

---
## License

MIT License
