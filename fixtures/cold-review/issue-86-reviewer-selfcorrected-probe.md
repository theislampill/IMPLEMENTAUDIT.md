# #86 positive fixture: reviewer corrects its own defective probe

reviewer-attestation: reviewer_identity: task-cold-2 | requested_model: GPT-5 | actual_model: GPT-5 | authoring_context_reuse: no | other_reviewer_output_seen: no | base_sha: 1111111111111111111111111111111111111111 | head_sha: 2222222222222222222222222222222222222222
reviewer-probe: self-corrected | defect: wrong-route | correction: reran-correct-route
cold-review-disposition: PASS
lane-status: executed

Expected disposition when checked: PASS
