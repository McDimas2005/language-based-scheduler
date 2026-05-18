# Legacy Notes

## PDF

`LEGACY/NLP_AOL_Language_based_Scheduler.pdf` describes an NLP AOL project focused on creating calendar events from voice input and classifying the type of scheduled activity. It documents BERT, Whisper, the full scheduler notebook, and Google Calendar API integration with OAuth/service-account examples. The listed team members are:

- Bintang Haidar Rabbani Pradipayasa
- Michael Dimas Chrispradipta
- Mousa Khalil Mousa Ayesh

## Full System Notebook

`LEGACY/Full_System_Scheduler_NLP_AOL.ipynb` contains the original end-to-end flow:

1. Input via browser recording, uploaded audio, or typed text.
2. Whisper `base` transcription.
3. spaCy `en_core_web_trf` extraction for `DATE`, `TIME`, and activity phrases.
4. Manual date/time parsing with `dateutil`, regex, and relative date rules.
5. Fine-tuned BERT activity classification.
6. Google Calendar event creation.

The notebook example transcript was:

```text
I want to go to the library at 7b and next Sunday.
```

Another extraction example produced:

```text
Activity: Go to the Library
Date: tomorrow
Time: 7 pm
```

## BERT Notebook

`LEGACY/FINAL_BERT_NLP_AOL_3_0.ipynb` fine-tuned `bert-base-uncased` with a sequence classification head. It collapsed original labels into five activity categories:

- social
- education
- health
- career
- hobby

The notebook tokenized with max length `128`, trained with PyTorch/transformers, and reported about `0.7606` weighted F1.

## Checkpoint

`LEGACY/last_trained_model_checkpoint.pth` is a PyTorch zip archive. String/archive inspection shows:

- `model_state_dict`
- `optimizer_state_dict`
- BERT layer weights
- classifier weights
- training metadata such as `epoch`, `best_val_loss`, and `early_stop_count`

The backend loads the model state into `BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=5)`.

## Audio Samples

- `LEGACY/ContentBased_audio_SRPreTrained_TEST.wav`: mono PCM, 24 kHz, about 57.82 seconds.
- `LEGACY/ContentBased_audio_SRPreTrained_TEST.mp3`: mono MP3, 24 kHz, about 347 KB.

These files are intended for manual end-to-end Whisper validation after backend dependencies and `ffmpeg` are installed.

