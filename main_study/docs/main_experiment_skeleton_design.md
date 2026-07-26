run_main_experiment.py

main()
│
├── 1. Read command-line arguments
│     ├── --run-id run_001
│     ├── --records 1,2   optional pre-flight subset
│     └── --export-every 25
│
├── 2. Resolve project paths
│     ├── experiment input parquet
│     ├── runtime config/parser/prompts
│     ├── results folders
│     └── frozen originals for hash-check
│
├── 3. Validate runtime integrity
│     ├── hash runtime prompts/parser
│     ├── compare with frozen originals
│     ├── hash input dataset
│     └── stop if mismatch
│
├── 4. Probe provider capability once
│     ├── OpenAI temperature/seed support
│     ├── Gemini temperature/seed support
│     └── Ollama temperature/seed support
│
├── 5. Save provenance manifest
│     ├── hashes
│     ├── model IDs
│     ├── package versions
│     ├── Python version
│     └── capability probe results
│
├── 6. Load inference dataset once
│     └── record_id + description_for_model
│
├── 7. Build task list
│     ├── records
│     ├── providers
│     └── prompt conditions
│
├── 8. Skip completed tasks
│     └── skip only if canonical parsed file exists with api_success=True
│
├── 9. Execute remaining tasks
│     ├── render prompt
│     ├── call provider with retry
│     ├── save raw response
│     ├── save API response
│     ├── parse response
│     └── save canonical parsed file if api_success=True
│
├── 10. Log API failures only
│      └── failures/run_001_failures.jsonl
│
├── 11. Rebuild aggregate exports
│      ├── scan canonical parsed files
│      ├── write parquet
│      ├── write csv
│      └── write xlsx
│
└── 12. Print completion summary
      ├── total expected
      ├── completed
      ├── skipped
      ├── API failures
      └── parse failures