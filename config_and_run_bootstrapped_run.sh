#!/bin/bash
LANGUAGE='hausa'
WORKING_DIR='hausa_01'

THRESHOLD='0.1'
DECREMENT='0.025'
MIN_THRESHOLD='0.0'

rm -fr "/Users/authorofnaught/Projects/LORELEI/NER/WORKING/${WORKING_DIR}"
python3 bootstrapped_run.py --threshold ${THRESHOLD} --decrement ${DECREMENT} --min_threshold ${MIN_THRESHOLD} ${LANGUAGE} ${WORKING_DIR}
