import os
import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForMultipleChoice
from torch.utils.data import Dataset, DataLoader

class SimpleLLMDataset(Dataset):
    def __init__(self, df, tokenizer, max_length=256):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.options = ['A', 'B', 'C', 'D', 'E']
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        prompt = row['prompt']
        
        choices = [str(row.get(opt, "")) for opt in self.options]
        prompts = [prompt] * len(choices)
        
        tokenized = self.tokenizer(
            prompts,
            choices,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        return {key: val for key, val in tokenized.items()}

class Predictor:
    def __init__(self, model_dir="../../models"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForMultipleChoice.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()
        self.options = ['A', 'B', 'C', 'D', 'E']
        
    def predict(self, df: pd.DataFrame):
        dataset = SimpleLLMDataset(df, self.tokenizer)
        loader = DataLoader(dataset, batch_size=4, shuffle=False)
        
        all_logits = []
        
        with torch.no_grad():
            for batch in loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                all_logits.append(outputs.logits.cpu().numpy())
                
        if not all_logits:
            return []
            
        all_logits = np.concatenate(all_logits, axis=0)
        
        # Softmax for probabilities
        exp_logits = np.exp(all_logits - np.max(all_logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        
        results = []
        for i in range(len(probs)):
            p = probs[i]
            sorted_indices = np.argsort(-p)
            
            top_3 = [self.options[idx] for idx in sorted_indices[:3]]
            
            prob_dict = {self.options[idx]: float(p[idx]) for idx in range(5)}
            
            row_id = df.iloc[i].get('id', i)
            
            # Optional fields if ground truth exists
            row_dict = {
                "id": int(row_id) if str(row_id).isdigit() else row_id,
                "prediction": top_3,
                "top_prediction": top_3[0],
                "confidence": float(p[sorted_indices[0]]),
                "probabilities": prob_dict
            }
            
            # Copy prompt and actual answer if present
            if 'prompt' in df.columns:
                row_dict['prompt'] = str(df.iloc[i]['prompt'])
            if 'answer' in df.columns:
                row_dict['actual_answer'] = str(df.iloc[i]['answer'])
                row_dict['correct'] = top_3[0] == str(df.iloc[i]['answer'])
                row_dict['top_3_correct'] = str(df.iloc[i]['answer']) in top_3
                
            results.append(row_dict)
            
        return results
