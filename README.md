## OpenAI Evals API

This repository explores the use of the [OpenAI Evals](https://github.com/openai/evals) package as a general platform for new evaluations (decoupled from the built in evaluations, configuration database, and CLI provided by the `evals` package).

Examples for several uses of the Evals API are provided:

-   [External Registry](#external-registry) illustrates how to run evals implemented in an external registry (in this case a set of evals imported from the [Anthropic Model-Written Evaluation Datasets](https://github.com/anthropics/evals)).

-   [Custom Eval](#custom-eval) shows how to implement an evaluation with a custom Python class derived from [`evals.Eval`](https://github.com/openai/evals/blob/main/evals/eval.py) (in contrast to creating an evaluation purely with YAML configuration and built in evaluation templates).

-   [Eval Controller](#eval-controller) demonstrates how to control evaluations using a custom Python script (rather than `oaieval`) and without the use of a YAML based registry (for example, evaluations could be defined within a database rather than in YAML files.)

-   [Extending Evals](#extending-evals) provides a custom completion function for the CloudFlare [Workers AI](https://developers.cloudflare.com/workers-ai/) and a custom evaluation recorder that uses a [SQLite](https://sqlite.org/index.html) database.

### Setup

To run and experiment with the code in this repository you will need to clone the OpenAI `evals` repo into a directory alongside this one and then create a virtual environment that includes `evals` (note that recent versions of `evals` are not on PyPI so cloning locally is required). For example, starting from this directory structure:

``` bash
~/evals/
   openai-evals-api/
```

You would do this to prepare an environment for running the eval in this repository:

``` bash
cd ~/evals
git clone --depth 1 --branch main https://github.com/openai/evals
cd openai-evals-api
python3 -m venv .venv
source .venv/bin/activate
pip install ../evals
```

Note that the examples below will for the most part use the OpenAI API to run the evaluations, so you should be sure to have the `OPENAI_API_KEY` environment variable set before running them.

### External Registry 

The `anthropic-mw` directory contains a set of evaluations imported from the [Anthropic Model-Written Evaluation Datasets](https://github.com/anthropics/evals). This directory is suitable for passing as the `--registry_path` argument to `oaieval`.

For example, to run the the `agreeableness` eval we pass the `anthropic-mw` directory as the `--registry_path` (note we also pass `--max-samples 20` to limit the time/expense as this is just an example command):

``` bash
oaieval --registry_path anthropic-mw --max_samples 20 gpt-3.5-turbo agreeableness 
```

See the `import.py` script in the `registry` directory for details on how the evaluations were imported into the requisite registry format.

### Custom Eval

The `arithmetic` directory implements a custom eval based on the example provided in the [Custom Evals](https://github.com/openai/evals/blob/main/docs/custom-eval.md) documentation. We then run this eval using the standard `oaieval` CLI tool.

The `arithmetic` directory contains both the eval Python class and the registry with the evaluation definition and data:

|                                    |                                       |
|-----------------------------------|-------------------------------------|
| `arithmetic/evals/arithmetic.yaml` | Evaluation definition                 |
| `arithmetic/eval.py`               | Custom eval derived from `evals.Eval` |
| `arithmetic/data/test.jsonl`       | Evaluation samples                    |
| `arithmetic/data/train.jsonl`      | Few shot samples                      |

The evaluation definition at `arithmetic/evals/arithmetic.yaml` is as follows:

``` yaml
arithmetic:
  id: arithmetic.dev.match-v1
  metrics: [accuracy]
  description: Evaluate arithmetic ability
arithmetic.dev.match-v1:
  class: arithmetic.eval:Arithmetic
  args:
    train_jsonl: train.jsonl
    test_jsonl: test.jsonl
```

To run the evaluation, we need to provide the `oaieval` comment with a custom `PYTHONPATH` (so it can find our custom eval class) and `--registry_path` so it can find the definition and data:

``` bash
PYTHONPATH="." oaieval --registry_path=arithmetic  gpt-3.5-turbo arithmetic
```

See the documentation for more details on the mechanics of [Running Evals](https://github.com/openai/evals/blob/main/docs/run-evals.md).

### Eval Controller

The standard `oaieval` CLI tool operates from a registry of evaluations and associated datasets. Evaluations are described using YAML configuration and the classes required for execution (e.g. evaluators, completion functions, recorders, etc.) are automatically instantiated by the CLI tool.

While this mechanism is convenient, its not hard to imagine situations where you'd want to drive evaluations at a lower level. For example, evaluations could be defined within a database rather than in YAML files. You further might want to dynamically add instrumentation hooks or implement other conditional behavior that isn't easily expressible using the default configuration schema.

The script `runeval.py` demonstrates how to run the `arithmetic` evaluation purely from Python APIs and without reference to YAML configuration or a registry. The script is purposely oversimplified (e.g. it supports only one model type) for the sake of illustration.

You can run it as follows:

``` bash
python3 runeval.py
```

Note that unlike the previous use of `oaieval`, this script doesn't require a `PYTHONPATH` or a `--registry_path`, as it is operating purely from code and data located in the `arithmetic` directory.

### Extending Evals 

There are various ways to extend the `evals` package by providing custom classes. For example, you can provide a custom [completion function](https://github.com/openai/evals/blob/main/docs/completion-fns.md) or a custom [recorder](https://github.com/openai/evals/blob/main/evals/record.py) for logging evaluations.

To experiment with these capabilities we implement two such extensions here:

|                           |                                                                                                 |
|-------------------|-----------------------------------------------------|
| `extension/sqlite.py`     | Recorder class for [SQLite](https://sqlite.org/index.html) databases.                           |
| `extension/cloudflare.py` | Completion function for CloudFlare [Workers AI](https://developers.cloudflare.com/workers-ai/). |

We demonstrate the use of these extensions in the `runeval-extension.py` script. You can try this script but note it does require that you provide some CloudFlare environment variables (see the docs on the [Workers AI REST API](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)for details on provisioning accounts and tokens):

``` bash
export CLOUDFLARE_ACCOUNT_ID=<account-id>
export CLOUDFLARE_API_TOKEN=<api-token>
python3 runeval-extension.py
```