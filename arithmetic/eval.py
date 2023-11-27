from pathlib import Path
import random

import evals
import evals.metrics

class Arithmetic(evals.Eval):
    def __init__(self, train_jsonl, test_jsonl, train_samples_per_prompt=2, eval_registry_path = None, **kwargs):
        super().__init__(
            eval_registry_path=eval_registry_path if eval_registry_path else Path(),
            **kwargs
        )
        self.train_jsonl = self._prefix_registry_path(train_jsonl).as_posix()
        self.test_jsonl = self._prefix_registry_path(test_jsonl).as_posix()
        self.train_samples_per_prompt = train_samples_per_prompt

    def run(self, recorder):
        """
        Called by the `oaieval` CLI to run the eval. The `eval_all_samples` method calls `eval_sample`.
        """
        self.train_samples = evals.get_jsonl(self.train_jsonl)
        test_samples = evals.get_jsonl(self.test_jsonl)
        self.eval_all_samples(recorder, test_samples)

        # Record overall metrics
        return {
            "accuracy": evals.metrics.get_accuracy(recorder.get_events("match")),
        }
    
    def eval_sample(self, test_sample, rng: random.Random):
        """
        Called by the `eval_all_samples` method to evaluate a single sample.

        ARGS
        ====
        `test_sample`: a line from the JSONL test file
        `rng`: should be used for any randomness that is needed during evaluation

        This method does the following:
        1. Generate a prompt that contains the task statement, a few examples, and the test question.
        2. Generate a completion from the model.
        2. Check if the generated answer is correct.
        """
        stuffing = rng.sample(self.train_samples, self.train_samples_per_prompt)

        prompt = [
            {"role": "system", "content": "Solve the following math problems"},
        ]

        for i, sample in enumerate(stuffing + [test_sample]):
            if i < len(stuffing):
                prompt += [
                    {"role": "system", "content": sample["problem"], "name": "example_user"},
                    {"role": "system", "content": sample["answer"], "name": "example_assistant"},
                ]
            else:
                prompt += [{"role": "user", "content": sample["problem"]}]


        result = self.completion_fn(prompt=prompt, temperature=0.0, max_tokens=1)
        
        sampled = result.get_completions()[0]
        words = sampled.split(" ")
        answer = words[-1].rstrip(".")

        evals.record_and_check_match(prompt=prompt, sampled=answer, expected=test_sample["answer"])