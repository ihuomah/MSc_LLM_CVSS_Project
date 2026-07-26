\# Dataset Sanitisation Protocol



\## Purpose



The dataset is sanitised to reduce the risk that LLMs recognise known CVEs from identifiers, vendor names, product names, or exact database wording. The aim is to test vulnerability scoring ability from technical descriptions rather than memorised vulnerability records.



\## Data Hidden from the Model



The model will not receive:



\- CVE identifiers

\- vendor names

\- product names

\- official CVSS vectors

\- official CVSS base scores

\- official severity labels

\- EPSS scores

\- publication dates



\## Data Retained for Evaluation



The internal evaluation dataset will retain:



\- original CVE ID

\- original vulnerability description

\- sanitised vulnerability description

\- official CVSS vector

\- official CVSS base score

\- official severity

\- EPSS score

\- vulnerability category

\- publication date



\## Sanitisation Rules



1\. Remove CVE identifiers.

2\. Replace vendor names with generic labels such as Vendor X.

3\. Replace product or software names with generic labels such as Software Y.

4\. Lightly paraphrase the description while preserving technical meaning.

5\. Preserve CVSS-relevant information such as attack vector, required privileges, user interaction, scope-related wording, and confidentiality, integrity, and availability impacts.

6\. Do not include official CVSS or EPSS values in the model prompt.

7\. Store the original and sanitised descriptions separately.



\## Example



Original description:



A vulnerability in a named vendor product allows a remote unauthenticated attacker to execute arbitrary code via crafted network requests.



Sanitised description:



A vulnerability in Software Y allows a remote unauthenticated attacker to execute arbitrary code by sending specially crafted network requests.



\## Rationale



This approach reduces memorisation bias while preserving the technical information required for CVSS vector estimation. It supports a fairer evaluation of model reasoning, consistency, and prompt sensitivity.

