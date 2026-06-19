import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging_helper import log_session_turn
import pandas as pd
import time
from agent import evaluate_claim

def calculate_accuracy(predictions_df, ground_truth_df, field):
    correct = 0
    total = len(predictions_df)
    
    for idx, row in predictions_df.iterrows():
        gt_row = ground_truth_df.iloc[idx]
        
        pred_val = str(row[field]).strip().lower()
        gt_val = str(gt_row[field]).strip().lower()
        
        if pred_val == gt_val:
            correct += 1
            
    return (correct / total) * 100 if total > 0 else 0

def generate_report(metrics):
    report_content = f"""# Operational Analysis & Evaluation Report

## Execution Metrics
- **Number of claims processed**: {metrics['claims_processed']}
- **Total Images Processed**: {metrics['images_processed']}
- **Total Time Taken**: {metrics['total_time_seconds']:.2f} seconds
- **Average Time Per Claim**: {metrics['avg_time_per_claim']:.2f} seconds

## Accuracy Metrics (Sample Dataset)
- **Claim Status Accuracy**: {metrics['acc_claim_status']:.2f}%
- **Issue Type Accuracy**: {metrics['acc_issue_type']:.2f}%
- **Object Part Accuracy**: {metrics['acc_object_part']:.2f}%
- **Evidence Standard Met Accuracy**: {metrics['acc_evidence']:.2f}%

## Cost and Rate Limit Considerations
- **Model Used**: `gpt-4o-mini` (Structured Outputs)
- **Approximate API Calls**: {metrics['claims_processed']} (1 per claim)
- **Token Strategy**: Passed base64 encoded images at high detail. Could be optimized to low detail for basic checks, or thumbnails if API limits are hit.
- **Estimated Test Set Cost**: Assuming average 1k tokens per text + 1-2 images (at ~170 tokens for low detail, or ~850 per high detail image). Processing ~45 claims with 1-2 images each using gpt-4o-mini costs < $0.50 overall.
- **Handling Constraints**: Used single sequential loop. For larger datasets, `asyncio` or `concurrent.futures` should be used with backoff retries.
"""
    with open("code/evaluation/evaluation_report.md", "w") as f:
        f.write(report_content)
    print("Evaluation report generated at code/evaluation/evaluation_report.md")

def main():
    print("Loading sample data for evaluation...")
    sample_df = pd.read_csv("dataset/sample_claims.csv")
    user_history_df = pd.read_csv("dataset/user_history.csv")
    evidence_requirements_df = pd.read_csv("dataset/evidence_requirements.csv")
    
    results = []
    
    total = len(sample_df)
    total_images = 0
    start_time = time.time()
    
    print(f"Processing {total} sample claims...")
    
    for idx, row in sample_df.iterrows():
        print(f"Evaluating sample claim {idx+1}/{total}...")
        
        images = row['image_paths'].split(';')
        total_images += len(images)
        
        prediction = evaluate_claim(
            user_id=row['user_id'],
            image_paths=row['image_paths'],
            user_claim=row['user_claim'],
            claim_object=row['claim_object'],
            user_history_df=user_history_df,
            evidence_requirements_df=evidence_requirements_df
        )
        
        result_row = prediction.copy()
        result_row['evidence_standard_met'] = str(result_row['evidence_standard_met']).lower()
        results.append(result_row)
        
    end_time = time.time()
    total_time = end_time - start_time
        
    predictions_df = pd.DataFrame(results)
    
    metrics = {
        'claims_processed': total,
        'images_processed': total_images,
        'total_time_seconds': total_time,
        'avg_time_per_claim': total_time / total if total > 0 else 0,
        'acc_claim_status': calculate_accuracy(predictions_df, sample_df, 'claim_status'),
        'acc_issue_type': calculate_accuracy(predictions_df, sample_df, 'issue_type'),
        'acc_object_part': calculate_accuracy(predictions_df, sample_df, 'object_part'),
        'acc_evidence': calculate_accuracy(predictions_df, sample_df, 'evidence_standard_met')
    }
    
    generate_report(metrics)
    log_session_turn("Evaluated sample claims and generated evaluation_report.md.", "Executed python code/evaluation/main.py")

if __name__ == "__main__":
    main()
