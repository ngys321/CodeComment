from __future__ import absolute_import
import os
import sys
import pickle
import torch
import json
import random
import logging
import argparse
import numpy as np
from io import open
from itertools import cycle
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, SequentialSampler, RandomSampler,TensorDataset
from torch.utils.data.distributed import DistributedSampler
from transformers import (WEIGHTS_NAME, AdamW, get_linear_schedule_with_warmup,
                          RobertaConfig, RobertaModel, RobertaTokenizer)
from transformers import (BartConfig, BartForConditionalGeneration, BartTokenizer,
                          T5Config, T5ForConditionalGeneration, T5Tokenizer,
                          PLBartConfig, PLBartForConditionalGeneration, PLBartTokenizer,
                         PLBartModel, AutoTokenizer)


MODEL_CLASSES = {'roberta': (RobertaConfig, RobertaModel, RobertaTokenizer),
                 't5': (T5Config, T5ForConditionalGeneration, T5Tokenizer),
                 'codet5': (T5Config, T5ForConditionalGeneration, RobertaTokenizer),
                 'bart': (BartConfig, BartForConditionalGeneration, BartTokenizer),
                 'plbart': (PLBartConfig, PLBartForConditionalGeneration, PLBartTokenizer),
                 'unixcoder': (RobertaConfig,RobertaModel,RobertaTokenizer),
                 'codet5p': (T5Config, T5ForConditionalGeneration, AutoTokenizer)}


decoder_model_type = 'codet5p'
decoder_model_name_or_path = "Salesforce/codet5p-220m"
decoder_local_rank = -1
decoder_n_gpu = 1
max_source_length = 512
max_target_length = 128
beam_size = 5

decoder_model_path = '/home/ysnamgoong42/ws/4_2023-11-24_CodeBase/saved_models/Salesforce/codet5p-220m/checkpoint-best-ppl/pytorch_model.bin'




# 파서를 생성하고 인자를 정의합니다.
parser = argparse.ArgumentParser()
parser.add_argument("--input_code", type=str, help="Input string")

# 인자를 파싱합니다.
args = parser.parse_args()




# Setup CUDA, GPU & distributed training

decoder_device = torch.device("cpu")
# decoder_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
decoder_n_gpu = torch.cuda.device_count()


config_class, model_class, tokenizer_class = MODEL_CLASSES[decoder_model_type]
tokenizer = tokenizer_class.from_pretrained(decoder_model_name_or_path,do_lower_case=False)
config = config_class.from_pretrained(decoder_model_name_or_path)


#build model
model = model_class.from_pretrained(decoder_model_name_or_path)

#load model
# print(f'reload model from {decoder_model_path}')
model.load_state_dict(torch.load(decoder_model_path, map_location=torch.device('cpu')))

model.to(decoder_device)


# print("Model Loaded") # 여기까지 잘 되나? -> 잘됨



def main(input_):

    source = input_

    # model inference
    source_tokens = tokenizer.tokenize(source)[:max_source_length-2]
    source_tokens = [tokenizer.cls_token] + source_tokens + [tokenizer.sep_token]
    source_ids = tokenizer.convert_tokens_to_ids(source_tokens)

    padding_length = max_source_length - len(source_ids)
    source_ids += [tokenizer.pad_token_id] * padding_length
    source_mask = [1] * len(source_tokens)
    source_mask += [0] * padding_length

    source_ids = torch.tensor(source_ids).unsqueeze(0).to(decoder_device)
    source_mask = torch.tensor(source_mask).unsqueeze(0).to(decoder_device)

    # generate
    with torch.no_grad():
        if decoder_n_gpu > 1:
            preds = model.module.generate(source_ids,
                                attention_mask=source_mask,
                                use_cache=True,
                                num_beams=beam_size,
                                early_stopping=False, # 如果是summarize就设为True
                                max_length=max_target_length)

        else:
            preds = model.generate(source_ids,                              
                                attention_mask=source_mask,      
                                use_cache=True,
                                num_beams=beam_size,
                                early_stopping=False, # 如果是summarize就设为True
                                max_length=max_target_length)
        # source_ids 가 배치로 들어가면, preds 도 배치로 나옴


    # print
    pred_str = tokenizer.decode(preds[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
    print(pred_str)


if __name__ == '__main__':
	main(args.input_code)