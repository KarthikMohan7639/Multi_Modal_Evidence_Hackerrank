import os
import base64
from typing import List, Optional
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field

# Ensure we use an initialized client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))

# Define structured output schemas according to allowed values

class ClaimPrediction(BaseModel):
    evidence_standard_met: bool = Field(description="Whether the image set is sufficient to evaluate the claim")
    evidence_standard_met_reason: str = Field(description="Short reason for the evidence decision")
    risk_flags: str = Field(description="Semicolon-separated risk flags (e.g., blurry_image, cropped_or_obstructed, low_light_or_glare, wrong_angle, wrong_object, wrong_object_part, damage_not_visible, claim_mismatch, possible_manipulation, non_original_image, text_instruction_present, user_history_risk, manual_review_required), or 'none'")
    issue_type: str = Field(description="Visible issue type: dent, scratch, crack, glass_shatter, broken_part, missing_part, torn_packaging, crushed_packaging, water_damage, stain, none, unknown")
    object_part: str = Field(description="Relevant object part (car: front_bumper, rear_bumper, door, hood, windshield, side_mirror, headlight, taillight, fender, quarter_panel, body, unknown; laptop: screen, keyboard, trackpad, hinge, lid, corner, port, base, body, unknown; package: box, package_corner, package_side, seal, label, contents, item, unknown)")
    claim_status: str = Field(description="supported, contradicted, or not_enough_information")
    claim_status_justification: str = Field(description="Concise explanation grounded in the image evidence")
    supporting_image_ids: str = Field(description="Image IDs supporting the decision, separated by semicolons; use 'none' if no image is sufficient")
    valid_image: bool = Field(description="Whether the image set is usable for automated review")
    severity: str = Field(description="none, low, medium, high, or unknown")

def encode_image(image_path):
    with open('dataset/' + image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def evaluate_claim(user_id, image_paths, user_claim, claim_object, user_history_df, evidence_requirements_df):
    """
    Evaluates a single claim using OpenAI structured output.
    """
    # 1. Look up user history
    user_hist_row = user_history_df[user_history_df['user_id'] == user_id]
    if not user_hist_row.empty:
        history_summary = user_hist_row.iloc[0]['history_summary']
        history_flags = user_hist_row.iloc[0]['history_flags']
    else:
        history_summary = "No history available."
        history_flags = "none"

    # 2. Look up evidence requirements
    # Get general requirements and object-specific ones
    reqs = evidence_requirements_df[
        (evidence_requirements_df['claim_object'] == 'all') | 
        (evidence_requirements_df['claim_object'] == claim_object)
    ]
    req_text = "\n".join([f"- {row['applies_to']}: {row['minimum_image_evidence']}" for _, row in reqs.iterrows()])

    # 3. Prepare the prompt textual content
    system_prompt = f"""
You are an expert AI system that verifies visual evidence for damage claims. 
The claim object is: {claim_object}

**Minimum Evidence Requirements:**
{req_text}

**User History Context:**
- History Summary: {history_summary}
- History Flags: {history_flags}

**Your Task:**
1. Extract the actual damage claim from the conversation.
2. Inspect the submitted images.
3. Decide whether the image evidence is sufficient (evidence_standard_met).
4. Identify the visible issue_type and object_part based on the allowed values. Use `issue_type=none` when the relevant part is visible and no issue is present. Use `unknown` when it cannot be determined.
5. Decide whether the claim is supported, contradicted, or not_enough_information (claim_status).
6. Select the image IDs (filenames without extension, e.g., 'img_1') that support the decision (supporting_image_ids). Separate by semicolons, or 'none'.
7. Flag risks (risk_flags) like blurry_image, wrong_object, etc. Separate by semicolons, or 'none'.
8. Estimate severity (severity: none, low, medium, high, unknown).
9. Produce short justifications grounded in the images.
"""

    user_prompt = f"Claim Conversation:\n{user_claim}\n\nReview the provided images to verify this claim."
    
    # 4. Prepare message content including images
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    
    content_list = [{"type": "text", "text": user_prompt}]
    
    # Process images
    image_paths_list = image_paths.split(';')
    for img_path in image_paths_list:
        try:
            base64_image = encode_image(img_path)
            # We assume filenames like 'img_1.jpg' are used. The ID is 'img_1'.
            img_id = os.path.splitext(os.path.basename(img_path))[0]
            content_list.append({"type": "text", "text": f"Image ID: {img_id}"})
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high"
                }
            })
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")

    messages.append({"role": "user", "content": content_list})

    # 5. Call OpenAI API
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=ClaimPrediction,
            temperature=0.0
        )
        prediction = response.choices[0].message.parsed
        return prediction.model_dump()
    except Exception as e:
        print(f"API Error: {e}")
        # Fallback empty response
        return {
            "evidence_standard_met": False,
            "evidence_standard_met_reason": "API Error processing claim.",
            "risk_flags": "manual_review_required",
            "issue_type": "unknown",
            "object_part": "unknown",
            "claim_status": "not_enough_information",
            "claim_status_justification": f"API Error: {str(e)}",
            "supporting_image_ids": "none",
            "valid_image": False,
            "severity": "unknown"
        }

