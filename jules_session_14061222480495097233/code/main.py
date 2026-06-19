from logging_helper import log_session_turn
import pandas as pd
import os
from agent import evaluate_claim

def main():
    print("Loading data...")
    claims_df = pd.read_csv("dataset/claims.csv")
    user_history_df = pd.read_csv("dataset/user_history.csv")
    evidence_requirements_df = pd.read_csv("dataset/evidence_requirements.csv")
    
    results = []
    
    total = len(claims_df)
    print(f"Processing {total} claims...")
    
    for idx, row in claims_df.iterrows():
        print(f"Processing claim {idx+1}/{total} (User: {row['user_id']})")
        
        prediction = evaluate_claim(
            user_id=row['user_id'],
            image_paths=row['image_paths'],
            user_claim=row['user_claim'],
            claim_object=row['claim_object'],
            user_history_df=user_history_df,
            evidence_requirements_df=evidence_requirements_df
        )
        
        # Combine input data and predictions
        result_row = {
            "user_id": row['user_id'],
            "image_paths": row['image_paths'],
            "user_claim": row['user_claim'],
            "claim_object": row['claim_object'],
            "evidence_standard_met": str(prediction['evidence_standard_met']).lower(),
            "evidence_standard_met_reason": prediction['evidence_standard_met_reason'],
            "risk_flags": prediction['risk_flags'],
            "issue_type": prediction['issue_type'],
            "object_part": prediction['object_part'],
            "claim_status": prediction['claim_status'],
            "claim_status_justification": prediction['claim_status_justification'],
            "supporting_image_ids": prediction['supporting_image_ids'],
            "valid_image": str(prediction['valid_image']).lower(),
            "severity": prediction['severity']
        }
        results.append(result_row)
        
    output_df = pd.DataFrame(results)
    output_df.to_csv("output.csv", index=False)
    print("Finished processing. Results saved to output.csv.")
    log_session_turn("Processed dataset/claims.csv and produced output.csv.", "Executed python code/main.py")

if __name__ == "__main__":
    main()
