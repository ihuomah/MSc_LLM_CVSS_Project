from cvss import CVSS3


TEST_VECTORS = [
    {
        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "expected_score": 7.5,
    },
    {
        "vector": "CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "expected_score": 6.2,
    },
    {
        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "expected_score": 9.8,
    },
]


def main():
    all_passed = True

    for item in TEST_VECTORS:
        vector = item["vector"]
        expected = item["expected_score"]

        cvss_obj = CVSS3(vector)
        calculated = cvss_obj.scores()[0]
        severity = cvss_obj.severities()[0]

        passed = calculated == expected
        all_passed = all_passed and passed

        print("=" * 80)
        print(f"Vector: {vector}")
        print(f"Expected score: {expected}")
        print(f"Calculated score: {calculated}")
        print(f"Severity: {severity}")
        print(f"Passed: {passed}")

    print("=" * 80)
    print(f"All validation tests passed: {all_passed}")


if __name__ == "__main__":
    main()