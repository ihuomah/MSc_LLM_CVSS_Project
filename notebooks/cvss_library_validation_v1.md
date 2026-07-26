# CVSS Library Validation v1

## Library

cvss (version 3.6)

Source:
https://github.com/RedHatProductSecurity/cvss

## Purpose

Validate the CVSS library before using it to independently recalculate scores from model-generated vector strings.

## Results

Vector 1:
Expected: 7.5
Calculated: 7.5
Passed: True

Vector 2:
Expected: 6.2
Calculated: 6.2
Passed: True

Vector 3:
Expected: 9.8
Calculated: 9.8
Passed: True

## Conclusion

All validation tests passed.

The library is approved for use as the canonical CVSS v3.1 score calculator in subsequent vector-score consistency analysis.