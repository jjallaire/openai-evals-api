## LLM Evaluation Frameworks

This document explores the capabilities of several existing LLM evaluation frameworks, with a particular eye towards their suitability as a platform for developing new evaluations. Frameworks covered include:

-   [OpenAI Evals](https://github.com/openai/evals)
-   [EleutherAI Eval Harness](https://github.com/EleutherAI/lm-evaluation-harness)
-   [Google BIG-bench](https://github.com/google/BIG-bench)
-   [CFRM Helm](https://crfm.stanford.edu/helm/latest/)

In order to explore various technical possibilities more concretely, this repo also includes some direct experimentation with the OpenAI evals package. This work is described in the repository [README](readm.mde).

### Capabiliities

Broadly speaking, all of the frameworks provide the following:

-   Suite of evaluations that cover a diverse range of tasks, drawing problems from linguistics, childhood development, math, common-sense reasoning, biology, physics, social bias, software development, and beyond.
-   Command-line interface for running single evaluations or sets of evaluations and recording their results.
-   Extensibility mechanism for running evaluations against REST APIs or locally hosted language models.
-   Registry of evaluations (typically defined using YAML) that can be extended via pull request from external contributors.

Of particular interest here is not so much the base suite of evaluations, but rather the suitability of the underlying platform as a foundation for flexibly building, running, and recording new evaluations. Capabilities of particular interest include:

-   Ability to develop and run new evaluations without forking/modifying the original repository
-   Ability to add new model types without without forking/modifying the original repository
-   Ability to write highly custom evaluations using pure Python code (i.e. not just using pre-fab templates and patterns)
-   Mechanism to declare model graded evaluations (rather than text matching/similarity or multiple choice)
-   Mechnaism to define chained evaluation logic (e.g. wrapping arbitrary evaluations in a chain of thought prompt)
-   A means for evaluations to make multiple calls to LLMs and maintain state across the calls.
-   Flexible storage for evaluation results (e.g. store in an external database rather than in JSON files)
-   User interfaces for browsing evaluation results
-   Ecosystem of third party tools (are others building on top of the framework)

### Comparison

In general, OpenAI and ElutherAI are designed and implemented more like general purpose evaluation platforms and Google and CFRM more like straightforward repositories of evaluations. This difference is reflected in the fact that with OpenAI and ElutherAI you can create new evaluations and model types in entirely different repositories, whereas with Google and CRFM you need to fork and modify the main repository.

All of the frameworks provide some sort of data driven registration of evaluations as well as the ability to implement evaluations in pure Python (note however than ElutherAI may be in the process of [deprecating](https://github.com/EleutherAI/lm-evaluation-harness/blob/big-refactor/docs/task_guide.md#no-longer-recommended-direct-task-subclassing) custom `Task` classes). OpenAI further enables declaration of some more sophisticated evaluation methods, including model-graded evaluations, wrapped evaluations (e.g. wrapping an existing eval in a chain of thought prompt), and "solvers" that can generate a response in any way, call models and any number of times, wait for human input, or generate a response from a programmatic bot without any models involved.

Here's a high level summary of how the various frameworks compare on the capabilities enumerated in the previous section:

| Capability              | OpenAI Evals            | ElutherAI Harness      | Google BIG-bench | CFRM Helm        |
|---------------|---------------|---------------|---------------|---------------|
| External Evaluations    | Yes (`--registry-path)` | Yes (`--include-path`) | No               | No               |
| External Model Types    | Yes (`CompletionFn`)    | Yes (`LM`)             | No               | No               |
| Pure Python Evaluations | Yes (`Eval`)            | Yes (`Task`)           | Yes (`Task`)     | Yes (`Scenario`) |
| Declare Model Graded    | Yes, (`modelgraded`)    | No                     | No               | No               |
| Declare Wrapped         | Yes (`completion_fns`)  | No                     | No               | No               |
| Multiple Calls w/ State | Yes (`Solvers)`         | Yes (`Filters`)        | No               | No               |
| Custom Results Storage  | Yes (`Recorder`)        | No                     | No               | No               |
| Datasets                | Internal                | External               | Internal         | External         |

Note that even though OpenAI is the only framework that allows for declarative use of more sophisticated evaluation processing, all of the other frameworks could in theory do the same things within pure Python evaluations (or `Filters` in the case of ElutherAI).

Note also that even though OpenAI is the only framework with an abstracted results recorder interface, the other frameworks can be adapted to use other storage by either creating a custom runner script or by ingesting the JSON files they write into a database after evals have been run.

One other point of difference between frameworks is how evaluation datasets are stored and managed. OpenAI and Google store data pre-processed for evaluation within the repository in JSON format (OpenAI uses Git LFS to mitigate large file sizes). This approach minimizes computation during evaluation and also reduces uncertainty about the provenance of data. ElutherAI and CFRM download data externally on the fly (from HuggingFace or raw URLs). This reduces the storage burden for the repository but does introduce the possibility that data could change unexpectedly between evaluations.

### Tools

#### Visualization

There are various native and third party tools available for visualizing the results of evals, these include:

-   OpenAI: [Zeno](https://github.com/zeno-ml/zeno-evals) and [oaievals-collector](https://github.com/nstankov-bg/oaievals-collector)
-   ElutherAI: [open_llm_leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard?ref=axion.zone)
-   Google: [task_postprocessing_scripts](https://github.com/google/BIG-bench/tree/main/bigbench/task_postprocessing_scripts)
-   CFRM Helm: [helm-summarize](https://crfm-helm.readthedocs.io/en/latest/tutorial/#using-helm-summarize) and [helm-frontend](https://github.com/stanford-crfm/helm/tree/main/src/helm-frontend)

None however are particularly deep or sophisticated so it's likely that non-trivial use of these frameworks will require additional custom UI/visualization work.

#### Execution

There is also some third party support for executing evaluations:

-   OpenAI: [Weights & Biases](https://wandb.ai/wandb_fc/openai-evals/reports/OpenAI-Evals-Demo-Using-W-B-Prompts-to-Run-Evaluations--Vmlldzo0MTI4ODA3) and [ChainForge](https://ianarawjo.medium.com/you-can-now-run-openai-evals-in-chainforge-81628446968d)
-   Google: [SeqIO](https://github.com/google/BIG-bench/blob/main/bigbench/bbseqio/README.md)