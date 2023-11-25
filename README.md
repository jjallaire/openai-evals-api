## OpenAI Evals API

This repository explores defining and running custom [OpenAI Evals](https://github.com/openai/evals). The goal is to see how flexible the `evals` package is for use as a general platform / API for evaluations (decoupled from the built in evaluations and command line utilities provided by the `evals` package).

For purposes of experimentation we implement the `arithmetic` custom eval (based on the documentation in [Custom Evals](https://github.com/openai/evals/blob/main/docs/custom-eval.md)).

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

### Arithmetic Eval

The `arithmetic` directory contains our custom evaluation and includes the following files:

| File               | Description                           |
|--------------------|---------------------------------------|
| `eval.py`          | Custom eval derived from `evals.Eval` |
| `data/test.jsonl`  | Evaluation samples                    |
| `data/train.jsonl` | Few shot samples                      |

The evaluation is registered in `registry/evals/arithmetic.yaml`:

``` yaml
arithmetic:
  id: arithmetic.dev.match-v1
  metrics: [accuracy]
  description: Evaluate arithmetic ability
arithmetic.dev.match-v1:
  class: arithmetic.eval:Arithmetic
  args:
    train_jsonl: arithmetic/data/train.jsonl
    test_jsonl: arithmetic/data/test.jsonl
```

To run the evaluation, we need to provide the `oaieval` comment with a custom `PYTHONPATH` (so it can find our custom eval class) and `registry` (so it can find `arithmetic.yaml` which describes the evaluation):

``` bash
PYTHONPATH="." oaieval --registry_path=registry  gpt-3.5-turbo arithmetic
```

Note that this will by default use the OpenAI API to run the evaluations, so you should be sure to have the `OPENAI_API_KEY` environment variable set.

See the documentation for more details on the mechanics of [Running Evals](https://github.com/openai/evals/blob/main/docs/run-evals.md).