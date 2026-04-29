# Recon: Canadian Federal Spending DB

_Source: read-only Render Postgres replica via proxy at `hackathon-2026-GOA`._

- Server: `PostgreSQL 18.3 (Debian 18.3-1.pgdg12+1)`
- Database: `database_database_w2a1`  •  Role: `database_database_w2a1_user`
- Raw query outputs: `recon/raw/00..10.json`

## Verdict

**(A) Structured fiscal/grants/charity tables, with embedded EN+FR program-purpose text per agreement.**

The dominant content is `fed.grants_contributions` — 1.28M federal grant/contribution agreements (3 GB), each with a dollar value, recipient, dates, owning department, and long bilingual prose fields (`prog_name_en/fr`, `prog_purpose_en/fr`, `description_en/fr`, `expected_results_en/fr`, `agreement_title_en/fr`). That gives us both the $ flows and the policy-language to classify them against stated commitments. Federal procurement (`public.contracts`, 153K rows) and Alberta provincial spending (`ab.ab_grants`, 1.99M rows; `ab.ab_contracts`, `ab.ab_sole_source`) are second-tier sources. CRA charity schema (49 tables) profiles ~84K registered charities including a per-charity federal/provincial/municipal funding split. A `general` schema provides an entity-resolution layer (entities, golden records, splink predictions) that already cross-links recipients across the fed/cra/ab silos.

Not a document corpus, not a knowledge graph — it's a fiscal warehouse with text-rich rows.

## Schemas

| schema | tables | rows | size |
|---|---:|---:|---:|
| `general` | 14 | 5,294,210 | 6.09 GB |
| `fed` | 6 | 1,275,889 | 3.15 GB |
| `cra` | 49 | 8,758,528 | 2.14 GB |
| `ab` | 9 | 2,612,047 | 1.26 GB |
| `public` | 1 | 153,455 | 0.09 GB |

Schema purpose at a glance:
- **`fed`** — federal proactive disclosure of grants and contributions (`grants_contributions`) plus lookups; the headline dataset for federal policy-alignment work.
- **`public`** — federal procurement contracts (`contracts`) with vendor, commodity, indigenous-business flag, and bilingual descriptions.
- **`cra`** — Canada Revenue Agency charity sector (T3010 returns, identification, financials, directors, government funding by charity, network analyses: `loops`, `johnson_cycles`, `scc_components`).
- **`ab`** — Alberta provincial grants, contracts, sole-source, and non-profit registry.
- **`general`** — cross-source entity-resolution layer (entities, golden records, source links, merge candidates, Splink predictions) plus an Alberta-only ministerial history table.

## Tables (largest first)

Row counts are exact `count(*)` (NULL = count timed out or view); sizes are `pg_total_relation_size`.

| schema.table | exact rows | est rows | total size |
|---|---:|---:|---:|
| `fed.grants_contributions` | 1,275,521 | 1,275,521 | 3006 MB |
| `general.entity_golden_records` | 851,300 | 853,710 | 1382 MB |
| `general.entity_source_links` | ? | 5,157,743 | 1342 MB |
| `general.entity_merge_candidates` | 1,643,060 | 1,646,131 | 1254 MB |
| `general.entities` | 926,670 | 928,687 | 1179 MB |
| `ab.ab_grants` | 1,986,676 | 1,983,886 | 1044 MB |
| `cra.cra_directors` | 2,873,624 | 2,872,615 | 530 MB |
| `general.entity_resolution_log` | 1,266,141 | 1,255,151 | 472 MB |
| `cra.cra_qualified_donees` | 1,664,343 | 1,664,343 | 350 MB |
| `cra.cra_charitable_programs` | 478,691 | 478,691 | 242 MB |
| `cra.cra_financial_details` | 420,849 | 420,849 | 134 MB |
| `cra.cra_identification` | 421,866 | 421,866 | 133 MB |
| `general.splink_predictions` | 540,640 | 540,640 | 125 MB |
| `cra.donee_name_quality` | 439,867 | 439,867 | 122 MB |
| `cra.overhead_by_charity` | 420,021 | 420,021 | 94 MB |
| `cra.cra_financial_general` | 422,683 | 422,683 | 82 MB |
| `public.contracts` | 153,455 | 153,455 | 82 MB |
| `ab.ab_grants_recipients` | 452,900 | 452,900 | 79 MB |
| `cra.cra_foundation_info` | 422,569 | 422,569 | 67 MB |
| `cra.loop_edges` | 53,771 | 53,771 | 60 MB |
| `general.entity_merges` | 66,147 | 63,782 | 54 MB |
| `cra.cra_compensation` | 216,380 | 216,380 | 40 MB |
| `ab.ab_non_profit` | 69,271 | 69,271 | 37 MB |
| `cra.govt_funding_by_charity` | 166,968 | 166,968 | 35 MB |
| `ab.ab_contracts` | 67,079 | 67,079 | 25 MB |
| `cra.t3010_impossibilities` | 54,010 | 54,010 | 23 MB |
| `cra.cra_web_urls` | 169,123 | 169,123 | 21 MB |
| `cra._dnq_canonical` | 91,129 | 91,129 | 18 MB |
| `cra.identification_name_history` | 92,437 | 92,437 | 15 MB |
| `cra.cra_resources_sent_outside` | 68,028 | 68,028 | 11 MB |
| `ab.ab_sole_source` | 15,533 | 15,533 | 11 MB |
| `cra.cra_gifts_in_kind` | 54,575 | 54,575 | 9816 kB |
| `cra.cra_activities_outside_countries` | 44,683 | 44,683 | 6632 kB |
| `cra.cra_non_qualified_donees` | 29,270 | 29,270 | 6496 kB |
| `cra.matrix_census` | 10,177 | 10,177 | 6432 kB |
| `cra.cra_disbursement_quota` | 22,151 | 22,151 | 5288 kB |
| `ab.ab_grants_programs` | 20,208 | 20,208 | 4360 kB |
| `cra.cra_activities_outside_details` | 25,139 | 25,139 | 4344 kB |
| `cra.loop_participants` | 30,003 | 30,003 | 4064 kB |
| `cra.loop_edge_year_flows` | 30,003 | 30,003 | 4048 kB |
| `cra.loops` | 5,808 | 5,808 | 3480 kB |
| `cra.scc_components` | 10,177 | 10,177 | 2904 kB |
| `cra.johnson_cycles` | 4,601 | 4,601 | 2832 kB |
| `cra.cra_political_activity_desc` | 313 | 286 | 936 kB |
| `cra.cra_exported_goods` | 4,029 | 4,029 | 776 kB |
| `cra.loop_financials` | 5,808 | 5,808 | 704 kB |
| `cra.t3010_plausibility_flags` | 1,075 | 1,075 | 664 kB |
| `cra.loop_universe` | 1,501 | 1,501 | 624 kB |
| `cra.loop_charity_financials` | 1,501 | 1,501 | 376 kB |
| `cra.scc_summary` | 347 | 347 | 144 kB |
| `cra.partitioned_cycles` | 108 | 108 | 136 kB |
| `ab.ab_grants_ministries` | 352 | 352 | 136 kB |
| `general.ministries_crosswalk` | 162 | 162 | 128 kB |
| `general.ministries_history` | 62 | 62 | 120 kB |
| `cra.cra_political_activity_resources` | 234 | 234 | 96 kB |
| `general.ministries` | 27 | -1 | 96 kB |
| `cra.cra_sub_category_lookup` | 247 | 247 | 80 kB |
| `cra.cra_country_lookup` | 264 | 264 | 72 kB |
| `fed.country_lookup` | 250 | 250 | 64 kB |
| `cra.cra_province_state_lookup` | 73 | 73 | 56 kB |
| `ab.ab_non_profit_status_lookup` | 16 | -1 | 48 kB |
| `ab.ab_grants_fiscal_years` | 12 | -1 | 48 kB |
| `general.donee_trigram_candidates` | 0 | -1 | 40 kB |
| `cra.t3010_completeness_issues` | 0 | -1 | 40 kB |
| `cra.identified_hubs` | 20 | -1 | 32 kB |
| `cra.cra_designation_lookup` | 3 | -1 | 32 kB |
| `cra.overhead_by_year` | 5 | -1 | 32 kB |
| `cra.overhead_by_year_designation` | 16 | -1 | 32 kB |
| `cra.govt_funding_by_year` | 5 | -1 | 32 kB |
| `general.splink_aliases` | 0 | -1 | 32 kB |
| `cra.cra_category_lookup` | 30 | 30 | 32 kB |
| `fed.currency_lookup` | 94 | 94 | 32 kB |
| `fed.province_lookup` | 13 | -1 | 32 kB |
| `fed.recipient_type_lookup` | 8 | -1 | 32 kB |
| `fed.agreement_type_lookup` | 3 | -1 | 32 kB |
| `cra.cra_program_type_lookup` | 3 | -1 | 32 kB |
| `general.splink_build_metadata` | 1 | -1 | 32 kB |
| `cra.cra_political_activity_funding` | 0 | -1 | 24 kB |
| `general.resolution_batches` | 0 | -1 | 16 kB |

### Views (no on-disk size; reflect underlying tables)
- `ab.vw_grants_by_ministry` (7 cols)
- `ab.vw_grants_by_recipient` (6 cols)
- `ab.vw_non_profit_decoded` (8 cols)
- `cra.vw_charity_financials_by_year` (19 cols)
- `cra.vw_charity_profiles` (19 cols)
- `cra.vw_charity_programs` (8 cols)
- `fed.vw_grants_by_department` (8 cols)
- `fed.vw_grants_by_province` (6 cols)
- `fed.vw_grants_decoded` (36 cols)
- `general.vw_entity_funding` (26 cols)
- `general.vw_entity_search` (11 cols)

## Columns by table

Compact format: `name : udt_name [NN]` (NN = NOT NULL). Primary-key columns are marked with **bold**. Full catalog with precision/scale: `recon/raw/04_columns.json`.

### `fed`

#### `fed.agreement_type_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`

#### `fed.country_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`

#### `fed.currency_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`

#### `fed.grants_contributions`

- **`_id`** : `int4` NN
- `ref_number` : `text`
- `amendment_number` : `text`
- `amendment_date` : `date`
- `agreement_type` : `text`
- `agreement_number` : `text`
- `recipient_type` : `text`
- `recipient_business_number` : `text`
- `recipient_legal_name` : `text`
- `recipient_operating_name` : `text`
- `research_organization_name` : `text`
- `recipient_country` : `text`
- `recipient_province` : `text`
- `recipient_city` : `text`
- `recipient_postal_code` : `text`
- `federal_riding_name_en` : `text`
- `federal_riding_name_fr` : `text`
- `federal_riding_number` : `text`
- `prog_name_en` : `text`
- `prog_name_fr` : `text`
- `prog_purpose_en` : `text`
- `prog_purpose_fr` : `text`
- `agreement_title_en` : `text`
- `agreement_title_fr` : `text`
- `agreement_value` : `numeric`
- `foreign_currency_type` : `text`
- `foreign_currency_value` : `numeric`
- `agreement_start_date` : `date`
- `agreement_end_date` : `date`
- `coverage` : `text`
- `description_en` : `text`
- `description_fr` : `text`
- `expected_results_en` : `text`
- `expected_results_fr` : `text`
- `additional_information_en` : `text`
- `additional_information_fr` : `text`
- `naics_identifier` : `text`
- `owner_org` : `text`
- `owner_org_title` : `text`
- `is_amendment` : `bool`

#### `fed.province_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`

#### `fed.recipient_type_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`

#### `fed.vw_grants_by_department` *(view)*

- `owner_org` : `text`
- `owner_org_title` : `text`
- `agreement_type` : `text`
- `grant_count` : `int8`
- `total_value` : `numeric`
- `avg_value` : `numeric`
- `earliest_start` : `date`
- `latest_start` : `date`

#### `fed.vw_grants_by_province` *(view)*

- `recipient_province` : `text`
- `province_name` : `text`
- `grant_count` : `int8`
- `total_value` : `numeric`
- `avg_value` : `numeric`
- `department_count` : `int8`

#### `fed.vw_grants_decoded` *(view)*

- `_id` : `int4`
- `ref_number` : `text`
- `amendment_number` : `text`
- `amendment_date` : `date`
- `agreement_type` : `text`
- `agreement_type_name` : `text`
- `agreement_number` : `text`
- `recipient_type` : `text`
- `recipient_type_name` : `text`
- `recipient_business_number` : `text`
- `recipient_legal_name` : `text`
- `recipient_operating_name` : `text`
- `research_organization_name` : `text`
- `recipient_country` : `text`
- `country_name` : `text`
- `recipient_province` : `text`
- `province_name` : `text`
- `recipient_city` : `text`
- `recipient_postal_code` : `text`
- `federal_riding_name_en` : `text`
- `federal_riding_number` : `text`
- `prog_name_en` : `text`
- `prog_purpose_en` : `text`
- `agreement_title_en` : `text`
- `agreement_value` : `numeric`
- `foreign_currency_type` : `text`
- `foreign_currency_value` : `numeric`
- `agreement_start_date` : `date`
- `agreement_end_date` : `date`
- `coverage` : `text`
- `description_en` : `text`
- `expected_results_en` : `text`
- `additional_information_en` : `text`
- `naics_identifier` : `text`
- `owner_org` : `text`
- `owner_org_title` : `text`

### `public`

#### `public.contracts`

- **`id`** : `int4` NN
- `reference_number` : `text`
- `procurement_id` : `text`
- `vendor_name` : `text`
- `vendor_postal_code` : `text`
- `buyer_name` : `text`
- `contract_date` : `text`
- `economic_object_code` : `text`
- `description_en` : `text`
- `description_fr` : `text`
- `contract_period_start` : `text`
- `delivery_date` : `text`
- `contract_value` : `text`
- `original_value` : `text`
- `amendment_value` : `text`
- `comments_en` : `text`
- `comments_fr` : `text`
- `additional_comments_en` : `text`
- `additional_comments_fr` : `text`
- `agreement_type_code` : `text`
- `trade_agreement` : `text`
- `land_claims` : `text`
- `commodity_type` : `text`
- `commodity_code` : `text`
- `country_of_vendor` : `text`
- `solicitation_procedure` : `text`
- `limited_tendering_reason` : `text`
- `trade_agreement_exceptions` : `text`
- `indigenous_business` : `text`
- `indigenous_business_excluding_psib` : `text`
- `intellectual_property` : `text`
- `potential_commercial_exploitation` : `text`
- `former_public_servant` : `text`
- `contracting_entity` : `text`
- `standing_offer_number` : `text`
- `instrument_type` : `text`
- `ministers_office` : `text`
- `number_of_bids` : `text`
- `article_6_exceptions` : `text`
- `award_criteria` : `text`
- `socioeconomic_indicator` : `text`
- `reporting_period` : `text`
- `owner_org` : `text`
- `owner_org_title` : `text`

### `ab`

#### `ab.ab_contracts`

- **`id`** : `uuid` NN
- `display_fiscal_year` : `text`
- `recipient` : `text`
- `amount` : `numeric`
- `ministry` : `text`

#### `ab.ab_grants`

- **`id`** : `int4` NN
- `ministry` : `text`
- `business_unit_name` : `text`
- `recipient` : `text`
- `program` : `text`
- `amount` : `numeric`
- `lottery` : `text`
- `payment_date` : `timestamp`
- `fiscal_year` : `text`
- `display_fiscal_year` : `text`
- `lottery_fund` : `text`
- `version` : `int4`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`

#### `ab.ab_grants_fiscal_years`

- **`id`** : `int4` NN
- `mongo_id` : `varchar`
- `display_fiscal_year` : `text`
- `count` : `int4`
- `total_amount` : `numeric`
- `last_updated` : `timestamp`
- `version` : `int4`

#### `ab.ab_grants_ministries`

- **`id`** : `int4` NN
- `mongo_id` : `varchar`
- `ministry` : `text`
- `display_fiscal_year` : `text`
- `aggregation_type` : `text`
- `count` : `int4`
- `total_amount` : `numeric`
- `last_updated` : `timestamp`
- `version` : `int4`

#### `ab.ab_grants_programs`

- **`id`** : `int4` NN
- `mongo_id` : `varchar`
- `program` : `text`
- `ministry` : `text`
- `display_fiscal_year` : `text`
- `aggregation_type` : `text`
- `count` : `int4`
- `total_amount` : `numeric`
- `last_updated` : `timestamp`
- `version` : `int4`

#### `ab.ab_grants_recipients`

- **`id`** : `int4` NN
- `mongo_id` : `varchar`
- `recipient` : `text`
- `payments_count` : `int4`
- `payments_amount` : `numeric`
- `programs_count` : `int4`
- `ministries_count` : `int4`
- `last_updated` : `timestamp`
- `version` : `int4`

#### `ab.ab_non_profit`

- **`id`** : `uuid` NN
- `type` : `text`
- `legal_name` : `text`
- `status` : `text`
- `registration_date` : `date`
- `city` : `text`
- `postal_code` : `text`

#### `ab.ab_non_profit_status_lookup`

- **`id`** : `int4` NN
- `status` : `text` NN
- `description` : `text`

#### `ab.ab_sole_source`

- **`id`** : `uuid` NN
- `ministry` : `text`
- `department_street` : `text`
- `department_street_2` : `text`
- `department_city` : `text`
- `department_province` : `text`
- `department_postal_code` : `text`
- `department_country` : `text`
- `vendor` : `text`
- `vendor_street` : `text`
- `vendor_street_2` : `text`
- `vendor_city` : `text`
- `vendor_province` : `text`
- `vendor_postal_code` : `text`
- `vendor_country` : `text`
- `start_date` : `date`
- `end_date` : `date`
- `amount` : `numeric`
- `contract_number` : `text`
- `contract_services` : `text`
- `permitted_situations` : `text`
- `display_fiscal_year` : `text`
- `special` : `text`

#### `ab.vw_grants_by_ministry` *(view)*

- `display_fiscal_year` : `text`
- `ministry` : `text`
- `payment_count` : `int8`
- `total_amount` : `numeric`
- `avg_amount` : `numeric`
- `min_amount` : `numeric`
- `max_amount` : `numeric`

#### `ab.vw_grants_by_recipient` *(view)*

- `recipient` : `text`
- `payment_count` : `int8`
- `total_amount` : `numeric`
- `fiscal_years_active` : `int8`
- `ministries_count` : `int8`
- `programs_count` : `int8`

#### `ab.vw_non_profit_decoded` *(view)*

- `id` : `uuid`
- `type` : `text`
- `legal_name` : `text`
- `status` : `text`
- `registration_date` : `date`
- `city` : `text`
- `postal_code` : `text`
- `status_description` : `text`

### `cra`

#### `cra._dnq_canonical`

- `bn` : `varchar`
- `legal_name` : `text`
- `nname` : `text`

#### `cra.cra_activities_outside_countries`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `country` : `bpchar`

#### `cra.cra_activities_outside_details`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `field_200` : `numeric`
- `field_210` : `bool`
- `field_220` : `bool`
- `field_230` : `text`
- `field_240` : `bool`
- `field_250` : `bool`
- `field_260` : `bool`

#### `cra.cra_category_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`
- `description_en` : `text`
- `description_fr` : `text`

#### `cra.cra_charitable_programs`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`program_type`** : `varchar` NN
- `description` : `text`

#### `cra.cra_compensation`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `field_300` : `int4`
- `field_305` : `int4`
- `field_310` : `int4`
- `field_315` : `int4`
- `field_320` : `int4`
- `field_325` : `int4`
- `field_330` : `int4`
- `field_335` : `int4`
- `field_340` : `int4`
- `field_345` : `int4`
- `field_370` : `int4`
- `field_380` : `numeric`
- `field_390` : `numeric`

#### `cra.cra_country_lookup`

- **`code`** : `bpchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`

#### `cra.cra_designation_lookup`

- **`code`** : `bpchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`
- `description_en` : `text`
- `description_fr` : `text`

#### `cra.cra_directors`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `last_name` : `text`
- `first_name` : `text`
- `initials` : `text`
- `position` : `text`
- `at_arms_length` : `bool`
- `start_date` : `date`
- `end_date` : `date`

#### `cra.cra_disbursement_quota`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `field_805` : `numeric`
- `field_810` : `numeric`
- `field_815` : `numeric`
- `field_820` : `numeric`
- `field_825` : `numeric`
- `field_830` : `numeric`
- `field_835` : `numeric`
- `field_840` : `numeric`
- `field_845` : `numeric`
- `field_850` : `numeric`
- `field_855` : `numeric`
- `field_860` : `numeric`
- `field_865` : `numeric`
- `field_870` : `numeric`
- `field_875` : `numeric`
- `field_880` : `numeric`
- `field_885` : `numeric`
- `field_890` : `numeric`

#### `cra.cra_exported_goods`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `item_name` : `text`
- `item_value` : `numeric`
- `destination` : `text`
- `country` : `bpchar`

#### `cra.cra_financial_details`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `section_used` : `bpchar`
- `field_4020` : `bpchar`
- `field_4050` : `bool`
- `field_4100` : `numeric`
- `field_4101` : `numeric`
- `field_4102` : `numeric`
- `field_4110` : `numeric`
- `field_4120` : `numeric`
- `field_4130` : `numeric`
- `field_4140` : `numeric`
- `field_4150` : `numeric`
- `field_4155` : `numeric`
- `field_4157` : `numeric`
- `field_4158` : `numeric`
- `field_4160` : `numeric`
- `field_4165` : `numeric`
- `field_4166` : `numeric`
- `field_4170` : `numeric`
- `field_4180` : `numeric`
- `field_4190` : `numeric`
- `field_4200` : `numeric`
- `field_4250` : `numeric`
- `field_4300` : `numeric`
- `field_4310` : `numeric`
- `field_4320` : `numeric`
- `field_4330` : `numeric`
- `field_4350` : `numeric`
- `field_4400` : `bool`
- `field_4490` : `bool`
- `field_4500` : `numeric`
- `field_4505` : `numeric`
- `field_4510` : `numeric`
- `field_4530` : `numeric`
- `field_4540` : `numeric`
- `field_4550` : `numeric`
- `field_4560` : `numeric`
- `field_4565` : `bool`
- `field_4570` : `numeric`
- `field_4571` : `numeric`
- `field_4575` : `numeric`
- `field_4576` : `numeric`
- `field_4577` : `numeric`
- `field_4580` : `numeric`
- `field_4590` : `numeric`
- `field_4600` : `numeric`
- `field_4610` : `numeric`
- `field_4620` : `numeric`
- `field_4630` : `numeric`
- `field_4640` : `numeric`
- `field_4650` : `numeric`
- `field_4655` : `text`
- `field_4700` : `numeric`
- `field_4800` : `numeric`
- `field_4810` : `numeric`
- `field_4820` : `numeric`
- `field_4830` : `numeric`
- `field_4840` : `numeric`
- `field_4850` : `numeric`
- `field_4860` : `numeric`
- `field_4870` : `numeric`
- `field_4880` : `numeric`
- `field_4890` : `numeric`
- `field_4891` : `numeric`
- `field_4900` : `numeric`
- `field_4910` : `numeric`
- `field_4920` : `numeric`
- `field_4930` : `text`
- `field_4950` : `numeric`
- `field_5000` : `numeric`
- `field_5010` : `numeric`
- `field_5020` : `numeric`
- `field_5030` : `numeric`
- `field_5040` : `numeric`
- `field_5045` : `numeric`
- `field_5050` : `numeric`
- `field_5100` : `numeric`
- `field_5500` : `numeric`
- `field_5510` : `numeric`
- `field_5610` : `numeric`
- `field_5750` : `numeric`
- `field_5900` : `numeric`
- `field_5910` : `numeric`
- `field_5030_indicator` : `text`

#### `cra.cra_financial_general`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `program_area_1` : `varchar`
- `program_area_2` : `varchar`
- `program_area_3` : `varchar`
- `program_percentage_1` : `int4`
- `program_percentage_2` : `int4`
- `program_percentage_3` : `int4`
- `program_description_1` : `text`
- `program_description_2` : `text`
- `program_description_3` : `text`
- `internal_division_1510_01` : `int4`
- `internal_division_1510_02` : `int4`
- `internal_division_1510_03` : `int4`
- `internal_division_1510_04` : `int4`
- `internal_division_1510_05` : `int4`
- `field_1510_subordinate` : `bool`
- `field_1510_parent_bn` : `varchar`
- `field_1510_parent_name` : `text`
- `field_1570` : `bool`
- `field_1600` : `bool`
- `field_1610` : `bool`
- `field_1620` : `bool`
- `field_1630` : `bool`
- `field_1640` : `bool`
- `field_1650` : `bool`
- `field_1800` : `bool`
- `field_2000` : `bool`
- `field_2100` : `bool`
- `field_2110` : `bool`
- `field_2300` : `bool`
- `field_2350` : `bool`
- `field_2400` : `bool`
- `field_2500` : `bool`
- `field_2510` : `bool`
- `field_2520` : `bool`
- `field_2530` : `bool`
- `field_2540` : `bool`
- `field_2550` : `bool`
- `field_2560` : `bool`
- `field_2570` : `bool`
- `field_2575` : `bool`
- `field_2580` : `bool`
- `field_2590` : `bool`
- `field_2600` : `bool`
- `field_2610` : `bool`
- `field_2620` : `bool`
- `field_2630` : `bool`
- `field_2640` : `bool`
- `field_2650` : `bool`
- `field_2660` : `text`
- `field_2700` : `bool`
- `field_2730` : `bool`
- `field_2740` : `bool`
- `field_2750` : `bool`
- `field_2760` : `bool`
- `field_2770` : `bool`
- `field_2780` : `bool`
- `field_2790` : `text`
- `field_2800` : `bool`
- `field_3200` : `bool`
- `field_3205` : `bool`
- `field_3210` : `bool`
- `field_3220` : `bool`
- `field_3230` : `bool`
- `field_3235` : `bool`
- `field_3240` : `bool`
- `field_3250` : `bool`
- `field_3260` : `bool`
- `field_3270` : `bool`
- `field_3400` : `bool`
- `field_3600` : `bool`
- `field_3610` : `bool`
- `field_3900` : `bool`
- `field_4000` : `bool`
- `field_4010` : `bool`
- `field_5000` : `bool`
- `field_5010` : `bool`
- `field_5030` : `numeric`
- `field_5031` : `numeric`
- `field_5032` : `numeric`
- `field_5450` : `numeric`
- `field_5460` : `numeric`
- `field_5800` : `bool`
- `field_5810` : `bool`
- `field_5820` : `bool`
- `field_5830` : `bool`
- `field_5840` : `bool`
- `field_5841` : `bool`
- `field_5842` : `int4`
- `field_5843` : `numeric`
- `field_5844` : `bool`
- `field_5845` : `bool`
- `field_5846` : `bool`
- `field_5847` : `bool`
- `field_5848` : `bool`
- `field_5849` : `bool`
- `field_5850` : `bool`
- `field_5851` : `bool`
- `field_5852` : `bool`
- `field_5853` : `bool`
- `field_5854` : `bool`
- `field_5855` : `bool`
- `field_5856` : `bool`
- `field_5857` : `bool`
- `field_5858` : `bool`
- `field_5859` : `bool`
- `field_5860` : `bool`
- `field_5861` : `int4`
- `field_5862` : `numeric`
- `field_5863` : `numeric`
- `field_5864` : `numeric`

#### `cra.cra_foundation_info`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `field_100` : `bool`
- `field_110` : `bool`
- `field_111` : `numeric`
- `field_112` : `numeric`
- `field_120` : `bool`
- `field_130` : `bool`

#### `cra.cra_gifts_in_kind`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `field_500` : `bool`
- `field_505` : `bool`
- `field_510` : `bool`
- `field_515` : `bool`
- `field_520` : `bool`
- `field_525` : `bool`
- `field_530` : `bool`
- `field_535` : `bool`
- `field_540` : `bool`
- `field_545` : `bool`
- `field_550` : `bool`
- `field_555` : `bool`
- `field_560` : `bool`
- `field_565` : `text`
- `field_580` : `numeric`

#### `cra.cra_identification`

- **`bn`** : `varchar` NN
- **`fiscal_year`** : `int4` NN
- `category` : `varchar`
- `sub_category` : `varchar`
- `designation` : `bpchar`
- `legal_name` : `text`
- `account_name` : `text`
- `address_line_1` : `text`
- `address_line_2` : `text`
- `city` : `text`
- `province` : `varchar`
- `postal_code` : `varchar`
- `country` : `bpchar`
- `registration_date` : `date`
- `language` : `varchar`
- `contact_phone` : `text`
- `contact_email` : `text`

#### `cra.cra_non_qualified_donees`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `recipient_name` : `text`
- `purpose` : `text`
- `cash_amount` : `numeric`
- `non_cash_amount` : `numeric`
- `country` : `text`

#### `cra.cra_political_activity_desc`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- `description` : `text`

#### `cra.cra_political_activity_funding`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `activity` : `text`
- `amount` : `numeric`
- `country` : `bpchar`

#### `cra.cra_political_activity_resources`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `staff` : `bool`
- `volunteers` : `bool`
- `financial` : `bool`
- `property` : `bool`
- `other_resource` : `text`

#### `cra.cra_program_type_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`
- `description_en` : `text`
- `description_fr` : `text`

#### `cra.cra_province_state_lookup`

- **`code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`
- `country` : `bpchar`

#### `cra.cra_qualified_donees`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `donee_bn` : `varchar`
- `donee_name` : `text`
- `associated` : `bool`
- `city` : `text`
- `province` : `varchar`
- `total_gifts` : `numeric`
- `gifts_in_kind` : `numeric`
- `number_of_donees` : `int4`
- `political_activity_gift` : `bool`
- `political_activity_amount` : `numeric`

#### `cra.cra_resources_sent_outside`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `form_id` : `int4`
- **`sequence_number`** : `int4` NN
- `individual_org_name` : `text`
- `amount` : `numeric`
- `country` : `bpchar`

#### `cra.cra_sub_category_lookup`

- **`category_code`** : `varchar` NN
- **`sub_category_code`** : `varchar` NN
- `name_en` : `text` NN
- `name_fr` : `text`
- `description_en` : `text`
- `description_fr` : `text`

#### `cra.cra_web_urls`

- **`bn`** : `varchar` NN
- **`fiscal_year`** : `int4` NN
- **`sequence_number`** : `int4` NN
- `contact_url` : `text`

#### `cra.donee_name_quality`

- **`donee_bn`** : `varchar` NN
- **`donee_name`** : `text` NN
- `canonical_name` : `text`
- `mismatch_category` : `text` NN
- `bn_defect` : `text`
- `trigram_sim` : `numeric`
- `citations` : `int4`
- `total_gifts` : `numeric`

#### `cra.govt_funding_by_charity`

- **`bn`** : `varchar` NN
- **`fiscal_year`** : `int4` NN
- `legal_name` : `text`
- `designation` : `bpchar`
- `category` : `varchar`
- `federal` : `numeric`
- `provincial` : `numeric`
- `municipal` : `numeric`
- `combined_sectiond` : `numeric`
- `total_govt` : `numeric`
- `revenue` : `numeric`
- `govt_share_of_rev` : `numeric`

#### `cra.govt_funding_by_year`

- **`fiscal_year`** : `int4` NN
- `charities_filed` : `int4`
- `charities_any_govt` : `int4`
- `federal` : `numeric`
- `provincial` : `numeric`
- `municipal` : `numeric`
- `combined_sectiond` : `numeric`
- `total_govt` : `numeric`
- `total_revenue` : `numeric`
- `federal_pct` : `numeric`
- `provincial_pct` : `numeric`
- `municipal_pct` : `numeric`
- `total_govt_pct` : `numeric`

#### `cra.identification_name_history`

- `bn` : `varchar`
- `legal_name` : `text`
- `account_name` : `text`
- `first_year` : `int4`
- `last_year` : `int4`
- `years_present` : `int4`

#### `cra.identified_hubs`

- **`bn`** : `varchar` NN
- `legal_name` : `text`
- `scc_id` : `int4`
- `in_degree` : `int4`
- `out_degree` : `int4`
- `total_degree` : `int4`
- `total_inflow` : `numeric`
- `total_outflow` : `numeric`
- `hub_type` : `varchar`

#### `cra.johnson_cycles`

- **`id`** : `int4` NN
- `hops` : `int4` NN
- `path_bns` : `_varchar` NN
- `path_display` : `text` NN
- `bottleneck_amt` : `numeric`
- `total_flow` : `numeric`
- `min_year` : `int4`
- `max_year` : `int4`

#### `cra.loop_charity_financials`

- **`bn`** : `varchar` NN
- `legal_name` : `text`
- `designation` : `bpchar`
- `category` : `varchar`
- `circular_outflow` : `numeric`
- `circular_inflow` : `numeric`
- `loops_count` : `int4`
- `revenue` : `numeric`
- `gifts_received_charities` : `numeric`
- `gifts_given_donees` : `numeric`
- `total_expenditures` : `numeric`
- `program_spending` : `numeric`
- `admin_spending` : `numeric`
- `fundraising_spending` : `numeric`
- `compensation_spending` : `numeric`

#### `cra.loop_edge_year_flows`

- **`loop_id`** : `int4` NN
- **`hop_idx`** : `int4` NN
- `src` : `varchar` NN
- `dst` : `varchar` NN
- `year_flow` : `numeric` NN
- `gift_count` : `int4` NN

#### `cra.loop_edges`

- **`src`** : `varchar` NN
- **`dst`** : `varchar` NN
- `total_amt` : `numeric` NN
- `edge_count` : `int4` NN
- `min_year` : `int4`
- `max_year` : `int4`
- `years` : `_int4`

#### `cra.loop_financials`

- **`loop_id`** : `int4` NN
- `hops` : `int4` NN
- `same_year` : `bool` NN
- `min_year` : `int4`
- `max_year` : `int4`
- `bottleneck_window` : `numeric`
- `total_flow_window` : `numeric`
- `bottleneck_allyears` : `numeric`
- `total_flow_allyears` : `numeric`

#### `cra.loop_participants`

- `bn` : `varchar` NN
- **`loop_id`** : `int4` NN
- **`position_in_loop`** : `int4` NN
- `sends_to` : `varchar`
- `receives_from` : `varchar`

#### `cra.loop_universe`

- **`bn`** : `varchar` NN
- `legal_name` : `text`
- `total_loops` : `int4`
- `loops_2hop` : `int4`
- `loops_3hop` : `int4`
- `loops_4hop` : `int4`
- `loops_5hop` : `int4`
- `loops_6hop` : `int4`
- `loops_7plus` : `int4`
- `max_bottleneck` : `numeric`
- `total_circular_amt` : `numeric`
- `score` : `int4`
- `scored_at` : `timestamptz`

#### `cra.loops`

- **`id`** : `int4` NN
- `hops` : `int4` NN
- `path_bns` : `_varchar` NN
- `path_display` : `text` NN
- `bottleneck_amt` : `numeric`
- `total_flow` : `numeric`
- `min_year` : `int4`
- `max_year` : `int4`

#### `cra.matrix_census`

- **`bn`** : `varchar` NN
- `legal_name` : `text`
- `walks_2` : `numeric`
- `walks_3` : `numeric`
- `walks_4` : `numeric`
- `walks_5` : `numeric`
- `walks_6` : `numeric`
- `walks_7` : `numeric`
- `walks_8` : `numeric`
- `max_walk_length` : `int4`
- `total_walk_count` : `numeric`
- `in_johnson_cycle` : `bool`
- `in_selfjoin_cycle` : `bool`
- `scc_id` : `int4`
- `scc_size` : `int4`

#### `cra.overhead_by_charity`

- **`bn`** : `varchar` NN
- **`fiscal_year`** : `int4` NN
- `legal_name` : `text`
- `designation` : `bpchar`
- `category` : `varchar`
- `revenue` : `numeric`
- `total_expenditures` : `numeric`
- `compensation` : `numeric`
- `administration` : `numeric`
- `fundraising` : `numeric`
- `programs` : `numeric`
- `strict_overhead` : `numeric`
- `broad_overhead` : `numeric`
- `strict_overhead_pct` : `numeric`
- `broad_overhead_pct` : `numeric`
- `outlier_flag` : `bool`

#### `cra.overhead_by_year`

- **`fiscal_year`** : `int4` NN
- `charities_filed` : `int4`
- `outliers_excluded` : `int4`
- `revenue` : `numeric`
- `total_expenditures` : `numeric`
- `compensation` : `numeric`
- `administration` : `numeric`
- `fundraising` : `numeric`
- `programs` : `numeric`
- `strict_overhead` : `numeric`
- `broad_overhead` : `numeric`
- `comp_pct_rev` : `numeric`
- `admin_pct_rev` : `numeric`
- `fundraising_pct_rev` : `numeric`
- `strict_overhead_pct_rev` : `numeric`
- `broad_overhead_pct_rev` : `numeric`
- `comp_pct_exp` : `numeric`
- `admin_pct_exp` : `numeric`
- `fundraising_pct_exp` : `numeric`
- `strict_overhead_pct_exp` : `numeric`
- `broad_overhead_pct_exp` : `numeric`

#### `cra.overhead_by_year_designation`

- **`fiscal_year`** : `int4` NN
- **`designation`** : `bpchar` NN
- `charities` : `int4`
- `revenue` : `numeric`
- `total_expenditures` : `numeric`
- `compensation` : `numeric`
- `administration` : `numeric`
- `fundraising` : `numeric`
- `programs` : `numeric`
- `strict_overhead` : `numeric`
- `broad_overhead` : `numeric`
- `strict_overhead_pct_rev` : `numeric`
- `broad_overhead_pct_rev` : `numeric`
- `strict_overhead_pct_exp` : `numeric`
- `broad_overhead_pct_exp` : `numeric`

#### `cra.partitioned_cycles`

- **`id`** : `int4` NN
- `hops` : `int4` NN
- `path_bns` : `_varchar` NN
- `path_display` : `text` NN
- `bottleneck_amt` : `numeric`
- `total_flow` : `numeric`
- `min_year` : `int4`
- `max_year` : `int4`
- `tier` : `varchar` NN
- `source_scc_id` : `int4`
- `source_scc_size` : `int4`

#### `cra.scc_components`

- **`bn`** : `varchar` NN
- `scc_id` : `int4` NN
- `scc_root` : `varchar` NN
- `scc_size` : `int4` NN
- `legal_name` : `text`

#### `cra.scc_summary`

- **`scc_id`** : `int4` NN
- `scc_root` : `varchar` NN
- `node_count` : `int4` NN
- `edge_count` : `int4` NN
- `total_internal_flow` : `numeric`
- `cycle_count_from_loops` : `int4`
- `cycle_count_from_johnson` : `int4`
- `top_charity_names` : `_text`

#### `cra.t3010_completeness_issues`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `fiscal_year` : `int4` NN
- `legal_name` : `text`
- **`rule_code`** : `text` NN
- **`missing_field`** : `text` NN
- `context_rule` : `text` NN
- `details` : `text`

#### `cra.t3010_impossibilities`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `fiscal_year` : `int4` NN
- `legal_name` : `text`
- **`rule_code`** : `text` NN
- `rule_family` : `text` NN
- `details` : `text`
- `severity` : `numeric`

#### `cra.t3010_plausibility_flags`

- **`bn`** : `varchar` NN
- **`fpe`** : `date` NN
- `fiscal_year` : `int4` NN
- `legal_name` : `text`
- **`rule_code`** : `text` NN
- **`offending_field`** : `text` NN
- `details` : `text`
- `severity` : `numeric`

#### `cra.vw_charity_financials_by_year` *(view)*

- `bn` : `varchar`
- `legal_name` : `text`
- `account_name` : `text`
- `fiscal_period_end` : `date`
- `fiscal_year` : `numeric`
- `total_revenue` : `numeric`
- `tax_receipted_gifts` : `numeric`
- `federal_government_revenue` : `numeric`
- `provincial_government_revenue` : `numeric`
- `municipal_government_revenue` : `numeric`
- `total_expenditures_before_disbursements` : `numeric`
- `charitable_programs_expenditure` : `numeric`
- `management_and_admin_expenditure` : `numeric`
- `fundraising_expenditure` : `numeric`
- `gifts_to_qualified_donees` : `numeric`
- `total_expenditures` : `numeric`
- `total_assets` : `numeric`
- `total_liabilities` : `numeric`
- `net_assets` : `numeric`

#### `cra.vw_charity_profiles` *(view)*

- `bn` : `varchar`
- `fiscal_year` : `int4`
- `legal_name` : `text`
- `account_name` : `text`
- `address_line_1` : `text`
- `address_line_2` : `text`
- `city` : `text`
- `province` : `varchar`
- `province_name` : `text`
- `postal_code` : `varchar`
- `country` : `bpchar`
- `country_name` : `text`
- `category` : `varchar`
- `category_name` : `text`
- `sub_category` : `varchar`
- `sub_category_name` : `text`
- `designation` : `bpchar`
- `designation_name` : `text`
- `designation_description` : `text`

#### `cra.vw_charity_programs` *(view)*

- `bn` : `varchar`
- `legal_name` : `text`
- `account_name` : `text`
- `fiscal_period_end` : `date`
- `fiscal_year` : `numeric`
- `program_type` : `varchar`
- `program_type_name` : `text`
- `description` : `text`

### `general`

#### `general.donee_trigram_candidates`

- **`id`** : `int4` NN
- `donee_name` : `text` NN
- `donee_name_norm` : `text` NN
- `candidate_entity_id` : `int4` NN
- `candidate_canonical_name` : `text` NN
- `candidate_bn_root` : `varchar`
- `similarity` : `numeric` NN
- `citations` : `int4` NN
- `total_gifts` : `numeric`
- `status` : `text` NN
- `llm_verdict` : `text`
- `llm_confidence` : `numeric`
- `llm_reasoning` : `text`
- `reviewed_at` : `timestamp`
- `applied_at` : `timestamp`
- `created_at` : `timestamp`

#### `general.entities`

- **`id`** : `int4` NN
- `canonical_name` : `text` NN
- `alternate_names` : `_text`
- `entity_type` : `text`
- `bn_root` : `varchar`
- `bn_variants` : `_text`
- `metadata` : `jsonb`
- `source_count` : `int4`
- `dataset_sources` : `_text`
- `confidence` : `numeric`
- `status` : `text`
- `reviewed_by` : `text`
- `llm_review` : `jsonb`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`
- `merged_into` : `int4`
- `norm_canonical` : `text`

#### `general.entity_golden_records`

- **`id`** : `int4` NN
- `canonical_name` : `text` NN
- `norm_name` : `text`
- `entity_type` : `text`
- `bn_root` : `varchar`
- `bn_variants` : `_text`
- `aliases` : `jsonb`
- `dataset_sources` : `_text`
- `source_summary` : `jsonb`
- `source_link_count` : `int4`
- `addresses` : `jsonb`
- `cra_profile` : `jsonb`
- `fed_profile` : `jsonb`
- `ab_profile` : `jsonb`
- `related_entities` : `jsonb`
- `merge_history` : `jsonb`
- `llm_authored` : `jsonb`
- `confidence` : `numeric`
- `status` : `text`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`

#### `general.entity_merge_candidates`

- **`id`** : `int4` NN
- `entity_id_a` : `int4` NN
- `entity_id_b` : `int4` NN
- `candidate_method` : `text` NN
- `similarity_score` : `numeric`
- `status` : `text`
- `llm_verdict` : `text`
- `llm_confidence` : `numeric`
- `llm_reasoning` : `text`
- `llm_response` : `jsonb`
- `llm_provider` : `text`
- `llm_tokens_in` : `int4`
- `llm_tokens_out` : `int4`
- `batch_id` : `int4`
- `reviewed_at` : `timestamp`
- `created_at` : `timestamp`

#### `general.entity_merges`

- **`id`** : `int4` NN
- `survivor_id` : `int4` NN
- `absorbed_id` : `int4` NN
- `candidate_id` : `int4`
- `merge_method` : `text` NN
- `names_added` : `_text`
- `bns_added` : `_text`
- `metadata_merged` : `jsonb`
- `links_redirected` : `int4`
- `merged_at` : `timestamp`
- `merged_by` : `text`

#### `general.entity_resolution_log`

- **`id`** : `int4` NN
- `source_schema` : `text` NN
- `source_table` : `text` NN
- `source_name` : `text` NN
- `original_names` : `_text`
- `bn` : `text`
- `record_count` : `int4`
- `status` : `text`
- `entity_id` : `int4`
- `match_confidence` : `numeric`
- `match_method` : `text`
- `candidates` : `jsonb`
- `llm_response` : `jsonb`
- `error_message` : `text`
- `batch_id` : `int4`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`

#### `general.entity_source_links`

- **`id`** : `int4` NN
- `entity_id` : `int4` NN
- `source_schema` : `text` NN
- `source_table` : `text` NN
- `source_pk` : `jsonb` NN
- `source_name` : `text`
- `match_confidence` : `numeric`
- `match_method` : `text`
- `link_status` : `text`
- `metadata` : `jsonb`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`

#### `general.ministries`

- **`id`** : `int4` NN
- `short_name` : `varchar` NN
- `name` : `text` NN
- `description` : `text`
- `minister` : `text`
- `deputy_minister` : `text`
- `effective_from` : `date`
- `effective_to` : `date`
- `is_active` : `bool`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`

#### `general.ministries_crosswalk`

- **`id`** : `int4` NN
- `raw_ministry` : `text` NN
- `normalized_ministry` : `text` NN
- `canonical_short_name` : `varchar` NN
- `historical_short_name` : `varchar`
- `confidence` : `text` NN
- `transform_note` : `text`
- `created_at` : `timestamp`

#### `general.ministries_history`

- **`id`** : `int4` NN
- `short_name` : `varchar` NN
- `canonical_name` : `text` NN
- `effective_from` : `date`
- `effective_to` : `date`
- `predecessors` : `_text`
- `successors` : `_text`
- `mandate_summary` : `text`
- `aliases` : `_text`
- `is_active` : `bool`
- `source_citation` : `text`
- `created_at` : `timestamp`
- `updated_at` : `timestamp`

#### `general.resolution_batches`

- **`id`** : `int4` NN
- `started_at` : `timestamp`
- `completed_at` : `timestamp`
- `source_description` : `text`
- `status` : `text`
- `total_records` : `int4`
- `processed_records` : `int4`
- `matched_records` : `int4`
- `created_records` : `int4`
- `llm_reviewed` : `int4`
- `error_records` : `int4`
- `config` : `jsonb`

#### `general.splink_aliases`

- **`id`** : `int4` NN
- `cluster_id` : `text` NN
- `alias` : `text` NN
- `source_dataset` : `text`
- `source_id` : `text`
- `match_probability` : `numeric`
- `build_id` : `int4`

#### `general.splink_build_metadata`

- **`id`** : `int4` NN
- `started_at` : `timestamp`
- `completed_at` : `timestamp`
- `splink_version` : `text`
- `backend` : `text`
- `threshold` : `numeric`
- `total_records` : `int4`
- `total_predictions` : `int4`
- `total_clusters` : `int4`
- `config` : `jsonb`
- `status` : `text`

#### `general.splink_predictions`

- **`id`** : `int4` NN
- `source_l` : `text` NN
- `record_l` : `text` NN
- `source_r` : `text` NN
- `record_r` : `text` NN
- `match_probability` : `numeric` NN
- `match_weight` : `numeric`
- `features` : `jsonb`
- `cluster_id` : `text`
- `build_id` : `int4`
- `created_at` : `timestamp`

#### `general.vw_entity_funding` *(view)*

- `entity_id` : `int4`
- `canonical_name` : `text`
- `bn_root` : `varchar`
- `entity_type` : `text`
- `dataset_sources` : `_text`
- `source_count` : `int4`
- `confidence` : `numeric`
- `status` : `text`
- `cra_total_revenue` : `numeric`
- `cra_total_expenditures` : `numeric`
- `cra_gifts_to_donees` : `numeric`
- `cra_program_spending` : `numeric`
- `cra_filing_count` : `int8`
- `cra_earliest_year` : `int4`
- `cra_latest_year` : `int4`
- `fed_total_grants` : `numeric`
- `fed_grant_count` : `int8`
- `fed_earliest_grant` : `date`
- `fed_latest_grant` : `date`
- `ab_total_grants` : `numeric`
- `ab_grant_payment_count` : `int8`
- `ab_total_contracts` : `numeric`
- `ab_contract_count` : `int8`
- `ab_total_sole_source` : `numeric`
- `ab_sole_source_count` : `int8`
- `total_all_funding` : `numeric`

#### `general.vw_entity_search` *(view)*

- `id` : `int4`
- `canonical_name` : `text`
- `alternate_names` : `_text`
- `entity_type` : `text`
- `bn_root` : `varchar`
- `bn_variants` : `_text`
- `metadata` : `jsonb`
- `source_count` : `int4`
- `dataset_sources` : `_text`
- `confidence` : `numeric`
- `status` : `text`

## Samples (3 rows per table, strings truncated to ~200 chars)

Full payloads in `recon/raw/08_samples.json`. Inline below for the policy-relevant headline tables; everything else is in the JSON.

### `fed.grants_contributions` — first row

| column | value |
|---|---|
| `_id` | 365015652 |
| `ref_number` | 141-2020-2021-Q4-02241 |
| `amendment_number` | 0 |
| `amendment_date` |  |
| `agreement_type` | C |
| `agreement_number` | 016736894 |
| `recipient_type` | G |
| `recipient_business_number` | 890138597RP0001 |
| `recipient_legal_name` | Village of St. Peter's |
| `recipient_operating_name` |  |
| `research_organization_name` |  |
| `recipient_country` | CA |
| `recipient_province` | NS |
| `recipient_city` | St. Peter's |
| `recipient_postal_code` | B0E3B0 |
| `federal_riding_name_en` |  |
| `federal_riding_name_fr` |  |
| `federal_riding_number` |  |
| `prog_name_en` | Youth - Canada Summer Jobs |
| `prog_name_fr` | Jeunesse - Emplois d'été Canada |
| `prog_purpose_en` | The Canada Summer Jobs (CSJ) program provides wage subsidies to employers to create employment for youth. CSJ provides funding to not-for-profit organizations, public-sector employers, and private sec...[+67ch] |
| `prog_purpose_fr` | Le programme Emplois d’été Canada offre des subventions salariales pour inciter les employeurs à créer de l’emploi pour les jeunes. Ce programme fournit des fonds aux organisations sans but lucratif e...[+118ch] |
| `agreement_title_en` | Village Beautification Assistant |
| `agreement_title_fr` |  |
| `agreement_value` | 7028.00 |
| `foreign_currency_type` |  |
| `foreign_currency_value` |  |
| `agreement_start_date` | 2020-06-15 |
| `agreement_end_date` | 2020-10-02 |
| `coverage` |  |
| `description_en` | Through the application of national and local priorities, the CSJ program seeks to provide youth, particularly those who face barriers to employment with access to work opportunities. Funded employers...[+140ch] |
| `description_fr` | Conformément aux priorités nationales et locales, le programme cherche à fournir aux jeunes en parliculier ceux qui sont confrontés à des obstacles à l’emploi un accès à des occasions d’emploi. Les em...[+166ch] |
| `expected_results_en` | The expected outcomes of CSJ are:    • Youth are employed, in training or education, or in further employment services and interventions. |
| `expected_results_fr` | Les résultats escomptés d’EÉC sont les suivants : • Les jeunes occupent un emploi ou soient en formation ou aux études ou bénéficient d’interventions ou de services avancés d’emploi. |
| `additional_information_en` |  |
| `additional_information_fr` |  |
| `naics_identifier` |  |
| `owner_org` | esdc-edsc |
| `owner_org_title` | Employment and Social Development Canada \| Emploi et Développement social Canada |
| `is_amendment` | False |

### `public.contracts` — first row

| column | value |
|---|---|
| `id` | 1 |
| `reference_number` | C-2019-2020-Q4-1 |
| `procurement_id` | P2000002 |
| `vendor_name` | Simzer Design Inc. |
| `vendor_postal_code` |  |
| `buyer_name` |  |
| `contract_date` | 2020-02-26 |
| `economic_object_code` | 0351 |
| `description_en` | Communications professional services not elsewhere specified |
| `description_fr` | Services professionnels de communications non specifies ailleurs |
| `contract_period_start` | 2019-11-15 |
| `delivery_date` | 2020-05-30 |
| `contract_value` | 38900.25 |
| `original_value` | 15255.0 |
| `amendment_value` | 23645.25 |
| `comments_en` | Increase contract by $23,645 |
| `comments_fr` | Augmentation du contrat de 23 645 $ |
| `additional_comments_en` |  |
| `additional_comments_fr` |  |
| `agreement_type_code` | 0 |
| `trade_agreement` |  |
| `land_claims` |  |
| `commodity_type` | S |
| `commodity_code` | T005 |
| `country_of_vendor` | CA |
| `solicitation_procedure` | TN |
| `limited_tendering_reason` | 85 |
| `trade_agreement_exceptions` | 00 |
| `indigenous_business` |  |
| `indigenous_business_excluding_psib` | N |
| `intellectual_property` | A3 |
| `potential_commercial_exploitation` | N |
| `former_public_servant` | N |
| `contracting_entity` |  |
| `standing_offer_number` |  |
| `instrument_type` | A |
| `ministers_office` | N |
| `number_of_bids` |  |
| `article_6_exceptions` |  |
| `award_criteria` |  |
| `socioeconomic_indicator` |  |
| `reporting_period` | 2019-2020-Q4 |
| `owner_org` | casdo-ocena |
| `owner_org_title` | Accessibility Standards Canada \| Normes d’accessibilité Canada |

### `ab.ab_grants` — first row

| column | value |
|---|---|
| `id` | 1 |
| `ministry` | INNOVATION AND ADVANCED EDUCATION |
| `business_unit_name` | INNOVATION &ADVANCED EDUCATION |
| `recipient` | OLDS COLLEGE |
| `program` | COMPREHENSIVE COMMUNITY INSTS |
| `amount` | -1125000.00 |
| `lottery` | False |
| `payment_date` | 2014-04-02T00:00:00 |
| `fiscal_year` | 2014 - 2015 |
| `display_fiscal_year` | 2014 - 2015 |
| `lottery_fund` |  |
| `version` | 0 |
| `created_at` | 2025-03-03T23:18:46.645000 |
| `updated_at` | 2025-03-03T23:18:46.645000 |

### `ab.ab_contracts` — first row

| column | value |
|---|---|
| `id` | 0a228873-81b5-4a5c-b3c5-33dda4437804 |
| `display_fiscal_year` | 2025 - 2026 |
| `recipient` | 101 STREET ASPEN PROPERTIES (EDM) GP INC. |
| `amount` | 250851.89 |
| `ministry` | Infrastructure |

### `ab.ab_sole_source` — first row

| column | value |
|---|---|
| `id` | a5acee78-4b1b-4a3e-a635-815151c44203 |
| `ministry` | Innovation and Advanced Education |
| `department_street` | 400, 10020 - 101A Avenue NW |
| `department_street_2` |  |
| `department_city` | Edmonton |
| `department_province` | AB |
| `department_postal_code` | T5J 3Gs |
| `department_country` | Canada |
| `vendor` | Employment and Social Development Canada |
| `vendor_street` | 140 Promendate du Portage |
| `vendor_street_2` | Bag 4, Pahse IV |
| `vendor_city` | Gatineau |
| `vendor_province` | Quebec |
| `vendor_postal_code` | K1A 0J9 |
| `vendor_country` | Canada |
| `start_date` | 2015-06-22 |
| `end_date` | 2016-03-31 |
| `amount` | 771680.00 |
| `contract_number` | AR 47026 |
| `contract_services` | Administrative Changes to Cease ACES |
| `permitted_situations` | b |
| `display_fiscal_year` | 2015 - 2016 |
| `special` | false |

### `cra.cra_identification` — first row

| column | value |
|---|---|
| `bn` | 831282512RR0001 |
| `fiscal_year` | 2020 |
| `category` | 210 |
| `sub_category` | 2 |
| `designation` | A |
| `legal_name` | Hill Pride Legacy Fund |
| `account_name` | Hill Pride Legacy Fund |
| `address_line_1` | 129 - 2550 MATHESON BLVD E |
| `address_line_2` |  |
| `city` | MISSISSAUGA |
| `province` | ON |
| `postal_code` | L4W4Z1 |
| `country` | CA |
| `registration_date` |  |
| `language` |  |
| `contact_phone` |  |
| `contact_email` |  |

### `cra.govt_funding_by_charity` — first row

| column | value |
|---|---|
| `bn` | 100021237RR0001 |
| `fiscal_year` | 2020 |
| `legal_name` | Académie Lafontaine inc. |
| `designation` | C |
| `category` | 10 |
| `federal` | 0 |
| `provincial` | 11848880.00 |
| `municipal` | 0 |
| `combined_sectiond` | 0 |
| `total_govt` | 11848880.00 |
| `revenue` | 22900132.00 |
| `govt_share_of_rev` | 51.74 |

### `cra.govt_funding_by_year` — first row

| column | value |
|---|---|
| `fiscal_year` | 2020 |
| `charities_filed` | 84533 |
| `charities_any_govt` | 35904 |
| `federal` | 10787745361.00 |
| `provincial` | 182584987002.00 |
| `municipal` | 11653471313.00 |
| `combined_sectiond` | 155310053.00 |
| `total_govt` | 205181513729.00 |
| `total_revenue` | 305276412831.00 |
| `federal_pct` | 3.53 |
| `provincial_pct` | 59.81 |
| `municipal_pct` | 3.82 |
| `total_govt_pct` | 67.21 |

### `general.entities` — first row

| column | value |
|---|---|
| `id` | 480333 |
| `canonical_name` | SPA & TENNIS CONDOMINIUM ASSOCIATION |
| `alternate_names` | [] |
| `entity_type` | non_profit |
| `bn_root` |  |
| `bn_variants` | [] |
| `metadata` | {} |
| `source_count` | 1 |
| `dataset_sources` | ['ab'] |
| `confidence` | 0.700 |
| `status` | draft |
| `reviewed_by` |  |
| `llm_review` |  |
| `created_at` | 2026-04-20T03:40:05.689820 |
| `updated_at` | 2026-04-20T03:40:05.689820 |
| `merged_into` |  |
| `norm_canonical` | SPA TENNIS CONDOMINIUM ASSOCIATION |

### `general.ministries` — first row

| column | value |
|---|---|
| `id` | 1 |
| `short_name` | AE |
| `name` | Advanced Education |
| `description` | Advanced Education |
| `minister` | Myles McDougall |
| `deputy_minister` | Shannon Marchand |
| `effective_from` | 2025-05-16 |
| `effective_to` |  |
| `is_active` | True |
| `created_at` | 2026-04-13T03:55:11.924028 |
| `updated_at` | 2026-04-13T03:55:11.924028 |

### `general.ministries_history` — first row

| column | value |
|---|---|
| `id` | 4 |
| `short_name` | MHA |
| `canonical_name` | Mental Health and Addiction |
| `effective_from` | 2022-10-24 |
| `effective_to` |  |
| `predecessors` | ['HEALTH_LEGACY'] |
| `successors` | [] |
| `mandate_summary` | Recovery-oriented addictions care, mental health services, opioid response. |
| `aliases` | ['MENTAL HEALTH AND ADDICTION', 'MENTAL HEALTH AND ADDICTIONS'] |
| `is_active` | True |
| `source_citation` | https://en.wikipedia.org/wiki/List_of_Alberta_provincial_ministers |
| `created_at` | 2026-04-19T22:28:05.261568 |
| `updated_at` | 2026-04-20T02:58:17.991246 |

### `general.entity_source_links` — first row

| column | value |
|---|---|
| `id` | 1 |
| `entity_id` | 85340 |
| `source_schema` | cra |
| `source_table` | cra_identification |
| `source_pk` | {'bn_root': '896671989'} |
| `source_name` | DIRA |
| `match_confidence` | 0.990 |
| `match_method` | bn_anchor |
| `link_status` | confirmed |
| `metadata` | {} |
| `created_at` | 2026-04-20T03:20:28.233587 |
| `updated_at` | 2026-04-20T03:20:28.233587 |

## Date / timestamp ranges

Some queries hit the proxy's 30s `statement_timeout` on unindexed scans of the largest tables — those are listed at the end as `(timeout)`. Full output: `recon/raw/09_date_minmax.json`.

| table.column | type | min | max | non-null |
|---|---|---|---|---:|
| `ab.ab_grants.payment_date` | `timestamp` | 2014-04-01 00:00:00 | 2026-03-31 00:00:00 | 1,983,355 |
| `ab.ab_grants_fiscal_years.last_updated` | `timestamp` | 2026-04-20 02:33:02.517968 | 2026-04-20 02:33:02.517968 | 12 |
| `ab.ab_grants_ministries.last_updated` | `timestamp` | 2026-04-20 02:33:02.517968 | 2026-04-20 02:33:02.517968 | 352 |
| `ab.ab_grants_programs.last_updated` | `timestamp` | 2026-04-20 02:33:02.517968 | 2026-04-20 02:33:02.517968 | 20,208 |
| `ab.ab_grants_recipients.last_updated` | `timestamp` | 2026-04-20 02:33:02.517968 | 2026-04-20 02:33:02.517968 | 452,900 |
| `ab.ab_non_profit.registration_date` | `date` | 1900-03-25 | 2026-03-31 | 69,271 |
| `ab.ab_sole_source.start_date` | `date` | 1975-04-01 | 2025-09-29 | 15,533 |
| `ab.ab_sole_source.end_date` | `date` | 2015-04-28 | 2099-03-31 | 15,530 |
| `ab.vw_non_profit_decoded.registration_date` | `date` | 1900-03-25 | 2026-03-31 | 69,271 |
| `cra.cra_activities_outside_countries.fpe` | `date` | 2020-01-01 | 2024-12-31 | 44,683 |
| `cra.cra_activities_outside_details.fpe` | `date` | 2020-01-01 | 2024-12-31 | 25,139 |
| `cra.cra_charitable_programs.fpe` | `date` | 2020-01-01 | 2024-12-31 | 478,691 |
| `cra.cra_compensation.fpe` | `date` | 2020-01-01 | 2024-12-31 | 216,380 |
| `cra.cra_directors.fpe` | `date` | 2020-01-01 | 2024-12-31 | 2,873,624 |
| `cra.cra_disbursement_quota.fpe` | `date` | 2023-07-31 | 2024-12-31 | 22,151 |
| `cra.cra_exported_goods.fpe` | `date` | 2020-01-15 | 2024-12-31 | 4,029 |
| `cra.cra_financial_details.fpe` | `date` | 2020-01-01 | 2024-12-31 | 420,849 |
| `cra.cra_financial_general.fpe` | `date` | 2020-01-01 | 2024-12-31 | 422,683 |
| `cra.cra_foundation_info.fpe` | `date` | 2020-01-01 | 2024-12-31 | 422,569 |
| `cra.cra_gifts_in_kind.fpe` | `date` | 2020-01-01 | 2024-12-31 | 54,575 |
| `cra.cra_identification.registration_date` | `date` | None | None | 0 |
| `cra.cra_non_qualified_donees.fpe` | `date` | 2022-06-30 | 2024-12-31 | 29,270 |
| `cra.cra_political_activity_desc.fpe` | `date` | 2020-01-31 | 2023-08-31 | 313 |
| `cra.cra_political_activity_funding.fpe` | `date` | None | None | 0 |
| `cra.cra_political_activity_resources.fpe` | `date` | 2020-03-20 | 2023-08-31 | 234 |
| `cra.cra_qualified_donees.fpe` | `date` | 2020-01-01 | 2024-12-31 | 1,664,343 |
| `cra.cra_resources_sent_outside.fpe` | `date` | 2020-01-01 | 2024-12-31 | 68,028 |
| `cra.loop_universe.scored_at` | `timestamptz` | 2026-04-19 20:00:28.143327+00 | 2026-04-19 20:01:46.746383+00 | 1,501 |
| `cra.t3010_completeness_issues.fpe` | `date` | None | None | 0 |
| `cra.t3010_impossibilities.fpe` | `date` | 2020-01-01 | 2024-12-31 | 54,010 |
| `cra.t3010_plausibility_flags.fpe` | `date` | 2020-03-31 | 2024-12-31 | 1,075 |
| `cra.vw_charity_financials_by_year.fiscal_period_end` | `date` | 2020-01-01 | 2024-12-31 | 420,849 |
| `fed.grants_contributions.agreement_start_date` | `date` | 1899-12-30 | 2027-01-01 | 1,275,521 |
| `fed.grants_contributions.agreement_end_date` | `date` | 0209-10-16 | 9999-12-31 | 1,087,655 |
| `general.donee_trigram_candidates.reviewed_at` | `timestamp` | None | None | 0 |
| `general.donee_trigram_candidates.applied_at` | `timestamp` | None | None | 0 |
| `general.donee_trigram_candidates.created_at` | `timestamp` | None | None | 0 |
| `general.entities.created_at` | `timestamp` | 2026-04-20 03:19:48.04046 | 2026-04-20 03:42:57.497048 | 926,670 |
| `general.entity_merge_candidates.reviewed_at` | `timestamp` | 2026-04-20 10:14:05.138335 | 2026-04-20 22:27:58.13824 | 1,614,607 |
| `general.entity_merge_candidates.created_at` | `timestamp` | 2026-04-20 03:54:08.357115 | 2026-04-20 10:13:50.898058 | 1,643,060 |
| `general.entity_merges.merged_at` | `timestamp` | 2026-04-20 10:14:05.853707 | 2026-04-20 21:20:27.269917 | 66,147 |
| `general.entity_resolution_log.created_at` | `timestamp` | 2026-04-20 03:20:29.604654 | 2026-04-20 03:42:56.391982 | 1,266,141 |
| `general.ministries.effective_from` | `date` | 2022-10-11 | 2025-05-16 | 25 |
| `general.ministries.effective_to` | `date` | None | None | 0 |
| `general.ministries.created_at` | `timestamp` | 2026-04-13 03:55:11.924028 | 2026-04-13 03:55:13.246887 | 27 |
| `general.ministries.updated_at` | `timestamp` | 2026-04-13 03:55:11.924028 | 2026-04-13 03:55:13.246887 | 27 |
| `general.ministries_crosswalk.created_at` | `timestamp` | 2026-04-20 02:58:21.459182 | 2026-04-20 02:58:30.83318 | 162 |
| `general.ministries_history.effective_from` | `date` | 2015-05-24 | 2025-05-16 | 62 |
| `general.ministries_history.effective_to` | `date` | 2015-10-21 | 2025-05-15 | 35 |
| `general.ministries_history.created_at` | `timestamp` | 2026-04-19 22:28:05.107448 | 2026-04-19 22:28:08.172671 | 62 |
| `general.ministries_history.updated_at` | `timestamp` | 2026-04-20 02:58:17.839106 | 2026-04-20 02:58:21.070167 | 62 |
| `general.resolution_batches.started_at` | `timestamp` | None | None | 0 |
| `general.resolution_batches.completed_at` | `timestamp` | None | None | 0 |
| `general.splink_build_metadata.started_at` | `timestamp` | 2026-04-20 03:48:41.249651 | 2026-04-20 03:48:41.249651 | 1 |
| `general.splink_build_metadata.completed_at` | `timestamp` | 2026-04-20 03:54:01.463944 | 2026-04-20 03:54:01.463944 | 1 |
| `general.splink_predictions.created_at` | `timestamp` | 2026-04-20 03:48:41.394672 | 2026-04-20 03:48:41.394672 | 540,640 |

**Timed out (need indexes or sampled scan to profile):**
- `ab.ab_grants.created_at`
- `ab.ab_grants.updated_at`
- `cra.cra_directors.start_date`
- `cra.cra_directors.end_date`
- `cra.vw_charity_programs.fiscal_period_end`
- `fed.grants_contributions.amendment_date`
- `fed.vw_grants_by_department.earliest_start`
- `fed.vw_grants_by_department.latest_start`
- `fed.vw_grants_decoded.amendment_date`
- `fed.vw_grants_decoded.agreement_start_date`
- `fed.vw_grants_decoded.agreement_end_date`
- `general.entities.updated_at`
- `general.entity_golden_records.created_at`
- `general.entity_golden_records.updated_at`
- `general.entity_resolution_log.updated_at`
- `general.entity_source_links.created_at`
- `general.entity_source_links.updated_at`
- `general.vw_entity_funding.fed_earliest_grant`
- `general.vw_entity_funding.fed_latest_grant`

## Likely join keys

### Declared foreign keys
- `cra.loop_edge_year_flows.loop_id` → `cra.loops.id`
- `cra.loop_financials.loop_id` → `cra.loops.id`
- `cra.loop_participants.loop_id` → `cra.loops.id`
- `general.donee_trigram_candidates.candidate_entity_id` → `general.entities.id`
- `general.entities.merged_into` → `general.entities.id`
- `general.entity_merge_candidates.entity_id_b` → `general.entities.id`
- `general.entity_merge_candidates.entity_id_a` → `general.entities.id`
- `general.entity_merges.absorbed_id` → `general.entities.id`
- `general.entity_merges.survivor_id` → `general.entities.id`
- `general.entity_resolution_log.entity_id` → `general.entities.id`
- `general.entity_source_links.entity_id` → `general.entities.id`

All declared FKs live inside `cra` (loop graph) and `general` (entity resolution). Cross-schema joins are by convention; the keys to know are below.

### Candidate cross-schema join keys (column-name overlap, manually curated)
#### Business Number (CRA charity registration #)
- `fed.grants_contributions.recipient_business_number`
- `cra.cra_identification.bn` and every other `cra.*` table
- `general.entity_source_links.source_pk` (JSON, includes `bn_root`)

Bridges federal grants → CRA charity profile and financials. Not a strict FK; fed `recipient_business_number` includes account suffixes (e.g. `…RP0001`), CRA uses `bn` (15-char) and `bn_root` (9-char). Strip last 6 chars to align.

#### Recipient name (free-text)
- `fed.grants_contributions.recipient_legal_name` / `recipient_operating_name`
- `cra.cra_identification.legal_name` / `account_name`
- `ab.ab_grants_recipients.recipient`
- `general.entities.canonical_name` / `alternate_names`

Use `general.entities` + `general.entity_source_links` for resolution rather than string-matching directly; the entity layer already maps source rows to canonical IDs.

#### Owning department (federal)
- `fed.grants_contributions.owner_org` / `owner_org_title`
- `public.contracts.owner_org` / `owner_org_title`

Department slug (e.g. `esdc-edsc`) for grouping spending by ministry.

#### Province
- `fed.grants_contributions.recipient_province`
- `fed.province_lookup`
- `cra.cra_province_state_lookup`
- `ab.ab_sole_source.department_province` / `vendor_province`

Two-letter codes; lookup tables in `fed` and `cra`.

#### Fiscal period
- `cra.*.fpe` (fiscal_period_end, date)
- `cra.cra_financial_general.fiscal_year` (int)
- `fed.grants_contributions.agreement_start_date` / `agreement_end_date`
- `ab.ab_grants.fiscal_year` / `payment_date`

CRA uses fiscal-period-end dates; fed uses agreement start/end; AB uses Apr–Mar fiscal year strings.

#### Entity ID (cross-source canonical)
- `general.entities.id`
- `general.entity_source_links.entity_id` + `(source_schema, source_table, source_pk)`
- `general.entity_golden_records.entity_id`
- `general.entity_merge_candidates.entity_id_a/b`
- `general.entity_resolution_log.entity_id`

The pre-built bridge from {fed, cra, ab} source rows to a canonical entity. ~927K entities, ~5.16M source links.

#### Ministry (Alberta)
- `ab.ab_grants.ministry` / `ab.ab_contracts.ministry` / `ab.ab_sole_source.ministry`
- `general.ministries.short_name` / `name`
- `general.ministries_crosswalk.raw_ministry` → `canonical_short_name`
- `general.ministries_history.short_name`

`ministries_crosswalk` is the alias-to-canonical bridge for messy raw ministry strings.

### Other column-name overlaps
Full list (any column name that appears in ≥2 tables): `recon/raw/10_name_overlap.json`.

## Indexes (highlights)

Total indexes catalogued: 274 — full list in `recon/raw/07_indexes.json`.

Notable indexes on the headline tables:

**`fed.grants_contributions`** (16 indexes)
- `grants_contributions_pkey` — `CREATE UNIQUE INDEX grants_contributions_pkey ON fed.grants_contributions USING btree (_id)`
- `idx_fed_gc_agreement_type` — `CREATE INDEX idx_fed_gc_agreement_type ON fed.grants_contributions USING btree (agreement_type)`
- `idx_fed_gc_country` — `CREATE INDEX idx_fed_gc_country ON fed.grants_contributions USING btree (recipient_country)`
- `idx_fed_gc_end_date` — `CREATE INDEX idx_fed_gc_end_date ON fed.grants_contributions USING btree (agreement_end_date)`
- `idx_fed_gc_is_amendment` — `CREATE INDEX idx_fed_gc_is_amendment ON fed.grants_contributions USING btree (is_amendment)`
- `idx_fed_gc_naics` — `CREATE INDEX idx_fed_gc_naics ON fed.grants_contributions USING btree (naics_identifier)`
- `idx_fed_gc_owner_org` — `CREATE INDEX idx_fed_gc_owner_org ON fed.grants_contributions USING btree (owner_org)`
- `idx_fed_gc_program_name` — `CREATE INDEX idx_fed_gc_program_name ON fed.grants_contributions USING gin (to_tsvector('english'::regconfig, COALESCE(prog_name_en, ''::text)))`
- _…and 8 more_

**`public.contracts`** (1 indexes)
- `contracts_pkey` — `CREATE UNIQUE INDEX contracts_pkey ON public.contracts USING btree (id)`

**`ab.ab_grants`** (10 indexes)
- `ab_grants_pkey` — `CREATE UNIQUE INDEX ab_grants_pkey ON ab.ab_grants USING btree (id)`
- `idx_ab_grants_amount` — `CREATE INDEX idx_ab_grants_amount ON ab.ab_grants USING btree (amount)`
- `idx_ab_grants_fiscal_year` — `CREATE INDEX idx_ab_grants_fiscal_year ON ab.ab_grants USING btree (display_fiscal_year)`
- `idx_ab_grants_ministry` — `CREATE INDEX idx_ab_grants_ministry ON ab.ab_grants USING btree (ministry)`
- `idx_ab_grants_payment_date` — `CREATE INDEX idx_ab_grants_payment_date ON ab.ab_grants USING btree (payment_date)`
- `idx_ab_grants_program` — `CREATE INDEX idx_ab_grants_program ON ab.ab_grants USING btree (program)`
- `idx_ab_grants_recipient` — `CREATE INDEX idx_ab_grants_recipient ON ab.ab_grants USING btree (recipient)`
- `idx_ab_grants_recipient_tsvector` — `CREATE INDEX idx_ab_grants_recipient_tsvector ON ab.ab_grants USING gin (to_tsvector('english'::regconfig, COALESCE(recipient, ''::text)))`
- _…and 2 more_

**`cra.cra_identification`** (7 indexes)
- `cra_identification_pkey` — `CREATE UNIQUE INDEX cra_identification_pkey ON cra.cra_identification USING btree (bn, fiscal_year)`
- `idx_identification_account` — `CREATE INDEX idx_identification_account ON cra.cra_identification USING gin (to_tsvector('english'::regconfig, account_name))`
- `idx_identification_category` — `CREATE INDEX idx_identification_category ON cra.cra_identification USING btree (category)`
- `idx_identification_designation` — `CREATE INDEX idx_identification_designation ON cra.cra_identification USING btree (designation)`
- `idx_identification_name` — `CREATE INDEX idx_identification_name ON cra.cra_identification USING gin (to_tsvector('english'::regconfig, legal_name))`
- `idx_identification_province` — `CREATE INDEX idx_identification_province ON cra.cra_identification USING btree (province)`
- `idx_identification_year` — `CREATE INDEX idx_identification_year ON cra.cra_identification USING btree (fiscal_year)`

**`cra.cra_financial_general`** (2 indexes)
- `cra_financial_general_pkey` — `CREATE UNIQUE INDEX cra_financial_general_pkey ON cra.cra_financial_general USING btree (bn, fpe)`
- `idx_financial_general_bn_fpe` — `CREATE INDEX idx_financial_general_bn_fpe ON cra.cra_financial_general USING btree (bn, fpe)`

**`cra.govt_funding_by_charity`** (4 indexes)
- `govt_funding_by_charity_pkey` — `CREATE UNIQUE INDEX govt_funding_by_charity_pkey ON cra.govt_funding_by_charity USING btree (bn, fiscal_year)`
- `idx_gfbc_designation` — `CREATE INDEX idx_gfbc_designation ON cra.govt_funding_by_charity USING btree (designation)`
- `idx_gfbc_total_govt` — `CREATE INDEX idx_gfbc_total_govt ON cra.govt_funding_by_charity USING btree (total_govt DESC)`
- `idx_gfbc_year` — `CREATE INDEX idx_gfbc_year ON cra.govt_funding_by_charity USING btree (fiscal_year)`

**`general.entities`** (19 indexes)
- `entities_pkey` — `CREATE UNIQUE INDEX entities_pkey ON general.entities USING btree (id)`
- `idx_entities_active_name_trgm` — `CREATE INDEX idx_entities_active_name_trgm ON general.entities USING gin (upper(canonical_name) gin_trgm_ops) WHERE (merged_into IS NULL)`
- `idx_entities_alt_names` — `CREATE INDEX idx_entities_alt_names ON general.entities USING gin (alternate_names)`
- `idx_entities_alt_names_trgm` — `CREATE INDEX idx_entities_alt_names_trgm ON general.entities USING gin (general.array_upper_join(alternate_names) gin_trgm_ops)`
- `idx_entities_bn_root` — `CREATE INDEX idx_entities_bn_root ON general.entities USING btree (bn_root)`
- `idx_entities_bn_root_trgm` — `CREATE INDEX idx_entities_bn_root_trgm ON general.entities USING gin (bn_root gin_trgm_ops) WHERE (bn_root IS NOT NULL)`
- `idx_entities_bn_variants` — `CREATE INDEX idx_entities_bn_variants ON general.entities USING gin (bn_variants)`
- `idx_entities_canonical_name` — `CREATE INDEX idx_entities_canonical_name ON general.entities USING btree (canonical_name)`
- _…and 11 more_

**`general.entity_source_links`** (5 indexes)
- `entity_source_links_pkey` — `CREATE UNIQUE INDEX entity_source_links_pkey ON general.entity_source_links USING btree (id)`
- `idx_source_links_entity` — `CREATE INDEX idx_source_links_entity ON general.entity_source_links USING btree (entity_id)`
- `idx_source_links_pk` — `CREATE INDEX idx_source_links_pk ON general.entity_source_links USING gin (source_pk jsonb_path_ops)`
- `idx_source_links_source` — `CREATE INDEX idx_source_links_source ON general.entity_source_links USING btree (source_schema, source_table)`
- `idx_source_links_status` — `CREATE INDEX idx_source_links_status ON general.entity_source_links USING btree (link_status)`

## Open items / caveats

- **Date min/max timeouts.** Several columns on the largest tables timed out at 30s; rerun with index-aware queries or sampled scans if needed: `agreement_start_date` and `amendment_date` were captured for `fed.grants_contributions` but `vw_grants_decoded` and a few `general` audit-timestamp columns timed out.
- **Sentinel/garbage dates.** `fed.grants_contributions.agreement_start_date` min is `1899-12-30` (Excel epoch sentinel) and `agreement_end_date` ranges `0209-10-16` → `9999-12-31` — the data needs a `[2010-01-01, today + 5y]` filter for any time-series.
- **`general.ministries*` is Alberta-only.** Source citation in `ministries_history` is the Wikipedia list of Alberta provincial ministers. There's no federal-ministers table — derive federal departments from `owner_org_title` strings if needed.
- **Foreign keys are sparse.** Only 11 declared FKs; cross-schema joins must rely on `general.entity_source_links` for canonical entity IDs and on business-number normalization for charity matches.
- **Text-stats step (artifact 11) was killed mid-run.** Average/max length per text column was deferred to keep the recon scoped. Headline EN-text columns we need to read for policy classification are obvious from samples: `prog_purpose_en`, `description_en`, `expected_results_en`, `agreement_title_en`, `additional_information_en` in `fed.grants_contributions`; `description_en`, `comments_en` in `public.contracts`.
- **CRA T3010 forms use opaque `field_NNNN` columns.** `cra_financial_details` and `cra_financial_general` are wide tables with hundreds of T3010 line-item codes. We'll need a CRA T3010 codebook to interpret specific lines.
