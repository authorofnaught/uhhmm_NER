#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 [language]"
  exit 1
fi

LANGUAGE=$1

#MODEL_DIR="/Users/authorofnaught/Projects/LORELEI/NER/hausa_ne_model/" # directory for trained model
MODEL_DIR="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}/" # directory for trained model
LTF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/LTF-DIR/${LANGUAGE}/" # directory containing LTF files
LTF_DIR_ABG1="/Users/authorofnaught/Projects/LORELEI/NER/LTF-ABG/${LANGUAGE}_100_approxiters/" # directory containing LTF files
LTF_DIR_ABG2="/Users/authorofnaught/Projects/LORELEI/NER/LTF-ABG/${LANGUAGE}_1000_approxiters/" # directory containing LTF files
SYS_LAF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/SYS-LAF/${LANGUAGE}/" # directory for tagger output (LAF files)
TRAIN_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TRAIN-SCP/${LANGUAGE}.txt" # script file containing paths to LAF files (one per line)
TRAIN_ALL_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TRAIN-SCP/${LANGUAGE}ALL.txt"
#TRAIN_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TRAIN-SCP/${LANGUAGE}FULL.txt" # script file containing paths to LAF files (one per line)
TEST_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/${LANGUAGE}.txt" # script file containing paths to LTF files (one per line)
TEST_ALL_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/${LANGUAGE}ALL.txt"
REF_LAF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/REF-LAF/${LANGUAGE}/" # directory containing gold standard LAF files

echo
echo
echo "##### Use no ABG features #####"
echo "RUNNING train.py..."
rm -rf $MODEL_DIR
./train.py --display_progress -S $TRAIN_SCP $MODEL_DIR $LTF_DIR
echo "RUNNING tagger.py..."
rm -rf $SYS_LAF_DIR
mkdir $SYS_LAF_DIR
./tagger.py -S $TEST_SCP -L $SYS_LAF_DIR $MODEL_DIR
echo "RUNNING score.py..."
./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR
#
#echo
#echo
#echo "##### Use ABG features after about 100 iterations #####"
#echo "RUNNING train.py..."
#rm -rf $MODEL_DIR
#./train.py --display_progress -S $TRAIN_SCP $MODEL_DIR $LTF_DIR_ABG1
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_SCP -L $SYS_LAF_DIR $MODEL_DIR
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR
#
#echo
#echo
#echo "##### Use ABG features after about 1000 iterations #####"
#echo "RUNNING train.py..."
#rm -fr $MODEL_DIR
#./train.py --display_progress -S $TRAIN_SCP $MODEL_DIR $LTF_DIR_ABG2
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_SCP -L $SYS_LAF_DIR $MODEL_DIR
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG2
#
#echo
#echo
#echo "##### Test for overfitting by testing on training data #####"
#echo "RUNNING train.py..."
#rm -rf $MODEL_DIR
#./train.py --display_progress -S $TRAIN_ALL_SCP $MODEL_DIR $LTF_DIR
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ALL_SCP -L $SYS_LAF_DIR $MODEL_DIR
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR
