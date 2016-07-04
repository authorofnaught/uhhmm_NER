#!/bin/bash
LANGUAGE='hausa'
WORKING_DIR='hausa_01'

THRESHOLD='0.1'
DECREMENT='0.025'
MIN_THRESHOLD='0.0'

python3 bootstrapped_run.py --threshold ${THRESHOLD} --decrement ${DECREMENT} --min_threshold ${MIN_THRESHOLD} ${LANGUAGE} ${WORKING_DIR}
