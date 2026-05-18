# Model Card

## Model

The activity classifier uses `bert-base-uncased` with a sequence classification head for five activity labels. The checkpoint is recovered from:

```text
LEGACY/last_trained_model_checkpoint.pth
```

## Labels

The original notebook mapped Yahoo-style topic labels into:

- social
- education
- health
- career
- hobby

The notebook used `pandas.Categorical` / `LabelEncoder`, so inference order is alphabetical:

```text
0: career
1: education
2: health
3: hobby
4: social
```

## Input

- English activity text
- Tokenizer: `BertTokenizer.from_pretrained("bert-base-uncased")`
- Max length: `128`
- Padding: `max_length`
- Truncation: enabled

## Checkpoint Format

Archive inspection shows a PyTorch zip checkpoint with keys including:

- `epoch`
- `model_state_dict`
- `optimizer_state_dict`
- `best_val_loss`
- `early_stop_count`

The backend supports `model_state_dict`, `state_dict`, raw state dicts, and `module.` prefix stripping.

## Recovered Evaluation

From `FINAL_BERT_NLP_AOL_3_0.ipynb`:

- Accuracy: `0.7607699358`
- Weighted precision: `0.7661571693`
- Weighted recall: `0.7607699358`
- Weighted F1: `0.7605666098`

Confusion matrix:

```text
[[171  10   7  13  19]
 [ 23 133  27   6  14]
 [  8   9 190   6  13]
 [ 16   2   8 167  14]
 [ 39   7   8  12 169]]
```

## Limitations

- Training data was adapted from broad topic labels, not a dedicated calendar-intent dataset.
- Short activity phrases may be ambiguous.
- The model should be treated as an assistive classifier, not a source of truth.
- If the checkpoint or ML dependencies are missing, the backend returns a model-unavailable warning rather than fake predictions.

