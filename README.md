## OpenAI Evals API

This repository explores defining and running custom [OpenAI Evals](https://github.com/openai/evals). The goal is to see how flexible the `evals` package is for use as a general platform for new evaluations (decoupled from the built in evaluations, configuration database, and CLI provided by the `evals` package).

For purposes of experimentation we implement the `arithmetic` custom eval (based on the documentation in [Custom Evals](https://github.com/openai/evals/blob/main/docs/custom-eval.md)). We then run this eval using the standard `oaieval` CLI tool. Finally, we run the eval entirely from a Python script (`runeval.py`) that makes use of the requisite `evals` Python APIs rather than involing the CLI.

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



### Custom Eval

The `arithmetic` directory contains our custom evaluation and also serves as the registry that hosts the evalulation definition and data:

|                                     |                                       |
|-------------------------------------|---------------------------------------|
| `arithmetic/evals/arithmetic.yaml`  | Evaluation definition                 |
| `arithmetic/eval.py`                | Custom eval derived from `evals.Eval` |
| `arithmetic/data/test.jsonl`        | Evaluation samples                    |
| `arithmetic/data/train.jsonl`       | Few shot samples                      |

The evaluation definitiion at `arithmetic/evals/arithmetic.yaml` is as follows:

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

Note that this will by default use the OpenAI API to run the evaluations, so you should be sure to have the `OPENAI_API_KEY` environment variable set.

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
|---------------------------|-------------------------------------------------------------------------------------------------|
| `extension/sqlite.py`     | Recorder class for [SQLite](https://sqlite.org/index.html) databases.                           |
| `extension/cloudflare.py` | Completion function for CloudFlare [Workers AI](https://developers.cloudflare.com/workers-ai/). |

We demonstrate the use of these extensions in the `runeval-extension.py` script. You can try this script but note it does require that you provide some CloudFlare environment variables (see the docs on the [Workers AI REST API ](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)for details on provisioning accounts and tokens):

``` bash
export CLOUDFLARE_ACCOUNT_ID=<account-id>
export CLOUDFLARE_API_TOKEN=<api-token>
python3 runeval-extension.py
```