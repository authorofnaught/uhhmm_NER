#!/bin/bash

### run.sh ###
# Use this script to run and score experiments with A, B, and G as their own features or in combination.
# Only those experiments should be uncommented which expect the features which features.py has currently been configured to produce.

# To make changes to the kinds of ABG features included in feature sets, edit features.py.
# Experiments will not correctly unless features.py has been edited to include only those features which are expected.

# All paths below should be changed to the directories or files containing the necessary data.


if [ $# -ne 1 ]; then
  echo "Usage: $0 [language]"
  exit 1
fi

LANGUAGE=$1

#MODEL_DIR="/Users/authorofnaught/Projects/LORELEI/NER/hausa_ne_model/" # Hausa model included with LRLP, do not use with train.py
MODEL_SPLIT_WORDFEATS="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_SPLIT_wordfeats/"
MODEL_SPLIT_WORDFEATS_A_B_G="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_SPLIT_wordfeats_A_B_G/"
MODEL_SPLIT_WORDFEATS_G="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_SPLIT_wordfeats_G/"
MODEL_SPLIT_A_B_G="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_SPLIT_A_B_G/"
MODEL_ALL_WORDFEATS="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_ALL_wordfeats/" # directory for trained model
MODEL_ALL_WORDFEATS_A_B_G="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_ALL_wordfeats_A_B_G/"
MODEL_ALL_WORDFEATS_G="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_ALL_wordfeats_G/"
MODEL_ALL_A_B_G="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_ALL_A_B_G/"
MODEL_RANDOM_A_B_G_F_J="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_random_A_B_G_F_J/"
MODEL_A_B_G_F_J="/Users/authorofnaught/Projects/LORELEI/NER/MODEL-DIR/${LANGUAGE}_A_B_G_F_J/"
LTF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/LTF-DIR/${LANGUAGE}/" # directory containing original LRLP LTF files
LTF_DIR_ABG="/Users/authorofnaught/Projects/LORELEI/NER/LTF-ABG/${LANGUAGE}/" # directory containing LTF files with uhhmm features
SYS_LAF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/SYS-LAF/${LANGUAGE}/" # directory for tagger output (LAF files)
TRAIN_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TRAIN-SCP/${LANGUAGE}.txt" # script file containing paths to LAF files (one per line)
TRAIN_ALL_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TRAIN-SCP/${LANGUAGE}ALL.txt" # same, but with all files listed if training and testing on same data
TEST_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/${LANGUAGE}.txt" # script file containing paths to LTF files (one per line)
TEST_ABG_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/${LANGUAGE}ABG.txt"
TEST_ALL_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/${LANGUAGE}ALL.txt" # same, but with all files listed if training and testing on same data
TEST_ALLABG_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/${LANGUAGE}ALLABG.txt" # same, but with all files listed if training and testing on same data
REF_LAF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/REF-LAF/${LANGUAGE}/" # directory containing gold standard LAF files

#echo
#echo
#echo "##### Use only prefix, suffix, word features (two word window) ABG features #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Data split into 302 Training files and 34 Testing files #####"
#echo "RUNNING train.py..."
#rm -rf $MODEL_SPLIT_WORDFEATS
#./train.py --display_progress -S $TRAIN_SCP $MODEL_SPLIT_WORDFEATS $LTF_DIR
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_SCP -L $SYS_LAF_DIR $MODEL_SPLIT_WORDFEATS
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR
#echo
#echo "Score from previous run:"
#echo "Hits: 276, Miss: 467, FA: 214"
#echo "Precision: 0.563265, Recall: 0.371467, F1: 0.447689" 
#
#
#echo
#echo
#echo "##### Use only prefix, suffix, word features (two word window) ABG features #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Training data = Testing data = all avaiable data #####"
##echo "RUNNING train.py..."
##rm -rf $MODEL_ALL_WORDFEATS
##./train.py --display_progress -S $TRAIN_ALL_SCP $MODEL_ALL_WORDFEATS $LTF_DIR
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ALL_SCP -L $SYS_LAF_DIR $MODEL_ALL_WORDFEATS
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR
#echo
#echo "Score from previous run:"
#echo "Hits: 4013, Miss: 2949, FA: 906"
#echo "Precision: 0.815816, Recall: 0.576415, F1: 0.675532" 
#
#
#echo
#echo
#echo "##### Use prefix, suffix, word features + A B G separate (two word window) #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Data split into 302 Training files and 34 Testing files #####"
##echo "RUNNING train.py..."
##rm -fr $MODEL_SPLIT_WORDFEATS_A_B_G
##./train.py --display_progress -S $TRAIN_SCP $MODEL_SPLIT_WORDFEATS_A_B_G $LTF_DIR_ABG
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ABG_SCP -L $SYS_LAF_DIR $MODEL_SPLIT_WORDFEATS_A_B_G
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
#echo
#echo "Score from previous run:"
#echo "Hits: 224, Miss: 519, FA: 211"
#echo "Precision: 0.514943, Recall: 0.301480, F1: 380306" 
#
#
#echo
#echo
#echo "##### Use prefix, suffix, word features + A B G separate (two word window) #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Training data = Testing data = all avaiable data #####"
##echo "RUNNING train.py..."
##rm -rf $MODEL_ALL_WORDFEATS_A_B_G
##./train.py --display_progress -S $TRAIN_ALL_SCP $MODEL_ALL_WORDFEATS_A_B_G $LTF_DIR_ABG
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ALLABG_SCP -L $SYS_LAF_DIR $MODEL_ALL_WORDFEATS_A_B_G
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
#echo
#echo "Score from previous run:"
#echo "Hits: 4135, Miss: 2827, FA: 839"
#echo "Precision: 0.831323, Recall: 0.593939, F1: 0.692862" 
#
#
#echo
#echo
#echo "##### Use prefix, suffix, word features +  G feature only (two word window) #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Data split into 302 Training files and 34 Testing files #####"
##echo "RUNNING train.py..."
##rm -fr $MODEL_SPLIT_WORDFEATS_G
##./train.py --display_progress -S $TRAIN_SCP $MODEL_SPLIT_WORDFEATS_G $LTF_DIR_ABG
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ABG_SCP -L $SYS_LAF_DIR $MODEL_SPLIT_WORDFEATS_G
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
#echo
#echo "Score from previous run:"
#echo "Hits: 282, Miss: 461, FA:268"
#echo "Precision: 0.552941, Recall: 379542, F1: 0.450120" 
#
#
#echo
#echo
#echo "##### Use prefix, suffix, word features + G feature only (two word window) #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Training data = Testing data = all avaiable data #####"
##echo "RUNNING train.py..."
##rm -rf $MODEL_ALL_WORDFEATS_G
##./train.py --display_progress -S $TRAIN_ALL_SCP $MODEL_ALL_WORDFEATS_G $LTF_DIR_ABG
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ALLABG_SCP -L $SYS_LAF_DIR $MODEL_ALL_WORDFEATS_G
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
#echo
#echo "Score from previous run:"
#echo "Hits: 4076, Miss: 2886, FA: 866"
#echo "Precision: 0.824767, Recall: 0.585464, F1: 0.684812" 
#
#
            #echo
            #echo
            #echo "##### Use only A B G features separately #####"
            #echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
            #echo "##### Data split into 302 Training files and 34 Testing files #####"
            #echo "RUNNING train.py..."
            #rm -fr $MODEL_SPLIT_A_B_G
            #./train.py --display_progress -S $TRAIN_SCP $MODEL_SPLIT_A_B_G $LTF_DIR_ABG
            #echo "RUNNING tagger.py..."
            #rm -rf $SYS_LAF_DIR
            #mkdir $SYS_LAF_DIR
            #./tagger.py -S $TEST_ABG_SCP -L $SYS_LAF_DIR $MODEL_SPLIT_A_B_G
            #echo "RUNNING score.py..."
            #./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
            #echo
            #echo "Score from previous run:"
            #echo "Hits: ____, Miss: ____, FA: ____"
            #echo "Precision: ____, Recall: ____, F1: ____" 
#
#
#echo
#echo
#echo "##### Use only A B G features separately #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Training data = Testing data = all avaiable data #####"
##echo "RUNNING train.py..."
##rm -rf $MODEL_ALL_A_B_G
##./train.py --display_progress -S $TRAIN_ALL_SCP $MODEL_ALL_A_B_G $LTF_DIR_ABG
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ALLABG_SCP -L $SYS_LAF_DIR $MODEL_ALL_A_B_G
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
#echo
#echo "Score from previous run:"
#echo "Hits: 209, Miss: 6753, FA: 180"
#echo "Precision: 0.537275, Recall: 0.030020, F1: 0.056863" 
#
#
#echo
#echo
#echo "##### See results for ABGFJ at chance #####"
#echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
#echo "##### Data split into 302 Training files and 34 Testing files #####"
##echo "RUNNING train.py..."
##rm -fr $MODEL_RANDOM_A_B_G_F_J
##./train.py --display_progress -S $TRAIN_SCP $MODEL_RANDOM_A_B_G_F_J $LTF_DIR_ABG
#echo "RUNNING tagger.py..."
#rm -rf $SYS_LAF_DIR
#mkdir $SYS_LAF_DIR
#./tagger.py -S $TEST_ABG_SCP -L $SYS_LAF_DIR $MODEL_RANDOM_A_B_G_F_J
#echo "RUNNING score.py..."
#./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
#echo
#echo "Score from previous run:"
#echo "Hits: 0, Miss: 743, FA: 4"
#echo "Precision: 0.0, Recall: 0.0, F1: 0.0"
#
# 
# echo
# echo
# echo "##### Try only ABGFJ features, each as a binary feature  #####"
# echo "WARNING: Make sure features.py has been configured to use these features and only these features!"
# echo "##### Data split into 302 Training files and 34 Testing files #####"
# echo "RUNNING train.py..."
# rm -fr $MODEL_A_B_G_F_J
# ./train.py --display_progress -S $TRAIN_SCP $MODEL_A_B_G_F_J $LTF_DIR_ABG
# echo "RUNNING tagger.py..."
# rm -rf $SYS_LAF_DIR
# mkdir $SYS_LAF_DIR
# ./tagger.py -S $TEST_ABG_SCP -L $SYS_LAF_DIR $MODEL_A_B_G_F_J
# echo "RUNNING score.py..."
# ./score.py $REF_LAF_DIR $SYS_LAF_DIR $LTF_DIR_ABG
# echo
# echo "Score from previous run:"
# echo "Hits: ____, Miss: ____, FA: ____"
# echo "Precision: ____, Recall: ____, F1: ____"
#
# 
