Run the following to test the bigram model:
python language_detector_update.py data/train/en/all_en.txt data/train/es/all_es.txt data/test/

Run the following to test the trigram model:
python language_detector_tri_update.py data/train/en/all_en.txt data/train/es/all_es.txt data/test/

Run the following to test backoff smoothing:
python language_detector_other_backoff.py data/train/en/all_en.txt data/train/es/all_es.txt data/test/
