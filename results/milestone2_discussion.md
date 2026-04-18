## Model Choice and Rationale

The mode we chose was Meta-Llama-3-8B-Instruct from HuggingFaceEndpoint. We chose this model because it seems to provide strong instruction-following capabilities and generates coherent, context-aware responses. HuggingFaceEndpoint allows us to leverage an open-source model without requiring local deployment, whichh reduces setup complexity while maintaining reproducibility.

Additionally, the model performs well at grounding responses in retrieved context, which is essential for our RAG systems