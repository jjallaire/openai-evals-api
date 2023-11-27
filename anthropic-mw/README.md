## OpenAI Evals for Anthropic Model-Written Evaluation Datasets

This registry provides implementations of several of Anthropic's Model-Written Evaluation Datasets (<https://github.com/anthropics/evals>) as [OpenAI Evals](https://github.com/openai/evals). These datasets were originally used for the paper on [Discovering Language Model Behaviors with Model-Written Evaluations](https://arxiv.org/abs/2212.09251). 

To reproduce the import of the evaluations, switch to the `anthropic-mw` directory, then clone the <https://github.com/anthropics/evals> repo:

```bash
cd anthropic-mw
git clone https://github.com/anthropics/evals anthropics-evals
```

Then, run `import.py` to import the evals into the into the requisite registry format:

```bash
python3 import.py
```


