# Backend Test Case Catalog

## Reports App

### ReportsModelTests

1. test_report_string_representation_returns_title
- Verifies Report.__str__ returns the title.

2. test_votes_unique_constraint_allows_only_one_vote_per_user_per_report
- Verifies one_vote_per_user unique constraint blocks duplicate votes by same user on same report.

3. test_votes_unique_constraint_still_allows_different_users
- Verifies different users can vote on the same report.

4. test_comments_reply_relationship_supports_nested_threads
- Verifies parent/child comment threading through reply_to and replies relation.

### ReportsApiTests

1. test_get_reports_overview_orders_by_newest_then_votes
- Verifies GET /api/v1/reports/overview ordering by date_submitted desc then vote_count desc.

2. test_get_report_returns_nested_comments
- Verifies GET /api/v1/reports/<id> returns nested replies under top-level comments.

3. test_get_report_returns_404_for_missing_report
- Verifies GET /api/v1/reports/<id> returns NOT_FOUND for missing report.

4. test_create_report_requires_authenticated_session
- Verifies POST /api/v1/reports/create rejects anonymous requests with UNAUTHORIZED.

5. test_create_report_validates_json_fields_and_outcode_mapping
- Verifies create-report validation paths:
- invalid JSON -> INVALID_JSON
- missing fields -> MISSING_FIELDS
- invalid postcode -> INVALID_POSTCODE
- unknown outcode -> OUTCODE_NOT_FOUND

6. test_create_report_successfully_persists_report_with_mapped_coordinates
- Verifies successful report creation stores mapped lat/lon and default vote_count.

7. test_upvote_endpoint_handles_auth_success_and_duplicate_vote
- Verifies upvote behavior:
- anonymous request -> 401
- first vote succeeds
- duplicate vote -> ALREADY_VOTED

8. test_remove_upvote_handles_not_voted_and_success_paths
- Verifies remove-upvote behavior:
- removing without vote -> NOT_VOTED
- existing vote removal succeeds and decrements vote_count.

9. test_add_comment_validates_auth_and_supports_replies
- Verifies comment endpoint behavior:
- anonymous request -> 401
- invalid JSON -> INVALID_JSON
- missing fields -> MISSING_FIELDS
- unknown parent -> NOT_FOUND
- top-level comment create succeeds
- reply comment create succeeds

## Accounts App

### RegisterTests

1. test_missing_fields_returns_error
- Verifies incomplete register payload returns VALIDATION_ERROR.

2. test_short_password_rejected
- Verifies short passwords are rejected with VALIDATION_ERROR.

3. test_duplicate_username_rejected
- Verifies duplicate username is rejected with DUPLICATE_CREDENTIALS.

4. test_duplicate_email_rejected
- Verifies duplicate email is rejected with DUPLICATE_CREDENTIALS.

### VerifyOTPTests

1. test_correct_otp_activates_account
- Verifies correct OTP activates inactive user and returns success.

2. test_wrong_otp_fails
- Verifies wrong OTP returns INVALID_OTP.

3. test_wrong_email_fails
- Verifies unknown email is rejected.

4. test_missing_fields_fails
- Verifies missing email or OTP fails.

### LoginTests

1. test_correct_credentials_logs_in
- Verifies valid credentials return success.

2. test_wrong_password_fails
- Verifies wrong password returns INVALID_CREDENTIALS.

3. test_wrong_email_fails
- Verifies unknown email login fails.

4. test_inactive_account_cannot_login
- Verifies inactive users cannot log in.

5. test_missing_fields_fails
- Verifies missing email/password fails.

### LogoutTests

1. test_logout_clears_session
- Verifies logout clears session user_id.

### UsersMeTests

1. test_authenticated_user_gets_profile
- Verifies authenticated request to /api/v1/users/me returns profile data.

2. test_unauthenticated_returns_401
- Verifies unauthenticated request to /api/v1/users/me returns 401.

### UpdateUserTests

1. test_update_username_success
- Verifies username update succeeds.

2. test_update_email_success
- Verifies email update succeeds.

3. test_duplicate_username_rejected
- Verifies updating to an existing username is rejected.

4. test_password_change_requires_current_password
- Verifies currentPassword is required when changing password.

5. test_password_change_wrong_current_password
- Verifies wrong currentPassword is rejected.

6. test_password_change_success
- Verifies password updates when currentPassword is correct.

7. test_unauthenticated_update_fails
- Verifies unauthenticated update request returns 401.

## Habitability App

### HabitabilityModelTests

1. test_extract_outcode_supports_common_postcode_shapes
- Verifies outcode parsing for None, blank, spaced, compact, and short formats.

2. test_neighborhood_save_normalizes_and_autofills_region_and_coordinates
- Verifies Neighborhood.save normalizes postcode, infers region, and autofills coordinates from mapping.

3. test_habitability_generated_scores_follow_weighted_formulas
- Verifies generated score fields match expected weighted formulas.

### HabitabilityApiTests

1. test_get_neighbourhoods_returns_ordered_payload
- Verifies GET /api/v1/neighbourhoods response shape, ordering, and JSON response behavior.

2. test_get_habitability_by_postcode_returns_400_for_blank_postcode
- Verifies blank postcode returns MISSING_POSTCODE with 400.

3. test_get_habitability_by_postcode_returns_score_when_score_id_matches_region_id
- Verifies primary lookup path where score_id equals region_id.

4. test_get_habitability_by_postcode_uses_relational_fallback_when_ids_do_not_align
- Verifies fallback lookup through neighborhood__region when IDs differ.

5. test_get_habitability_by_postcode_returns_fallback_payload_when_county_mapping_missing
- Verifies fallback score payload when no outcode mapping exists for requested postcode.

6. test_get_habitability_by_postcode_returns_404_when_region_not_found
- Verifies mapped county without Region row returns NOT_FOUND with 404.

7. test_get_habitability_by_postcode_returns_404_when_region_exists_without_scores
- Verifies region with no HabitabilityScores returns NOT_FOUND with 404.
